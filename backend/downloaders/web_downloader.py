"""
═══════════════════════════════════════════════════════════════════════════════
                СКАЧИВАНИЕ С ВЕБ-САЙТОВ (ИСПРАВЛЕННАЯ ВЕРСИЯ v2)
═══════════════════════════════════════════════════════════════════════════════

ИСПРАВЛЕНО:
    ✅ Одна сессия на весь цикл (cookie, keep-alive, connection pool)
    ✅ Скачивание во временный .tmp файл → rename (атомарность)
    ✅ Проверка Content-Type (HTML error-page не сохраняется как PDF)
    ✅ Парсинг Content-Disposition (правильное имя файла от сервера)
    ✅ Автоопределение кодировки (UTF-8, CP1251, Latin-1…)
    ✅ Fallback парсера: lxml → html.parser
    ✅ Referer при скачивании файлов
    ✅ Semaphore для параллельных загрузок
    ✅ Пагинация (follow_pagination=True)
    ✅ Расширенный поиск ссылок: <a>, <iframe>, <embed>, data-href и т.д.
    ✅ Обработка HTTP 429 (Retry-After)
    ✅ Контекстный менеджер (async with)
    ✅ Минимальный размер файла (отсеивает HTML-заглушки)
    ✅ Перекачка битых / неполных файлов
"""

import os
import re
import ssl
import asyncio
import logging
import random
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Set
from urllib.parse import urljoin, urlparse, unquote, parse_qs

import aiohttp
import aiofiles
from bs4 import BeautifulSoup

# ═══════════════════════════════════════════════════════════════════════════════
# Парсер: lxml быстрее, но может не быть установлен
# ═══════════════════════════════════════════════════════════════════════════════
try:
    import lxml  # noqa: F401
    HTML_PARSER = 'lxml'
except ImportError:
    HTML_PARSER = 'html.parser'

# ═══════════════════════════════════════════════════════════════════════════════
# User-Agent: fake_useragent или резервный список
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from fake_useragent import UserAgent
    _ua = UserAgent()
    USE_FAKE_UA = True
except ImportError:
    USE_FAKE_UA = False
    _ua = None

logger = logging.getLogger(__name__)

FALLBACK_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) '
    'Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
    '(KHTML, like Gecko) Version/17.4 Safari/605.1.15',
]


class WebDownloader:
    """
    Класс для скачивания файлов с веб-сайтов.

    ИСПОЛЬЗОВАНИЕ:
        async with WebDownloader(download_path=Path('./downloads')) as dl:
            files = await dl.download_from_page(
                url='https://example.com/manuals',
                file_extensions=['.pdf', '.doc'],
            )

    Или без контекстного менеджера (не забудьте close()):
        dl = WebDownloader(download_path=Path('./downloads'))
        files = await dl.download_from_page(...)
        await dl.close()
    """

    def __init__(
        self,
        download_path: Path,
        timeout: int = 60,
        max_retries: int = 3,
        delay: float = 1.0,
        proxy: Optional[str] = None,
        max_concurrent: int = 3,
        verify_ssl: bool = True,
        min_file_size: int = 1024,
    ):
        """
        Args:
            download_path:   Папка для сохранения файлов
            timeout:         Таймаут на запрос (сек)
            max_retries:     Кол-во повторных попыток
            delay:           Базовая задержка между запросами (сек)
            proxy:           HTTP/SOCKS прокси ('http://host:port')
            max_concurrent:  Макс. параллельных загрузок
            verify_ssl:      Проверять ли SSL-сертификаты
            min_file_size:   Мин. размер файла (байт) — меньше = HTML-заглушка
        """
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)

        self.timeout = aiohttp.ClientTimeout(
            total=timeout,
            connect=15,
            sock_read=timeout,
        )
        self.max_retries = max_retries
        self.delay = delay
        self.proxy = proxy
        self.max_concurrent = max_concurrent
        self.min_file_size = min_file_size

        # ── Сессия создаётся лениво ──────────────────────────────────
        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._downloaded_urls: Set[str] = set()

        # ── SSL ──────────────────────────────────────────────────────
        if not verify_ssl:
            self._ssl_context: Optional[ssl.SSLContext] = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self._ssl_context = None

        # ── Логирование ──────────────────────────────────────────────
        logger.info(f"🌐 WebDownloader: parser={HTML_PARSER}, "
                     f"concurrent={max_concurrent}, ssl={verify_ssl}")
        if USE_FAKE_UA:
            logger.info("   ✅ fake_useragent загружен")
        else:
            logger.info("   ⚠️ fake_useragent не найден → резервный список UA")

        # ── Статистика ───────────────────────────────────────────────
        self.stats: Dict[str, int] = {
            'pages_processed': 0,
            'links_found': 0,
            'files_downloaded': 0,
            'files_skipped': 0,
            'files_redownloaded': 0,
            'errors': 0,
            'total_size': 0,
        }

    # ══════════════════════════════════════════════════════════════════════
    #  УПРАВЛЕНИЕ СЕССИЕЙ
    # ══════════════════════════════════════════════════════════════════════

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        ИСПРАВЛЕНИЕ #1: Единственная сессия на весь жизненный цикл.

        Раньше: новая ClientSession на КАЖДЫЙ запрос → куки терялись,
                keep-alive не работал, пулы соединений не использовались.
        Теперь: одна сессия с CookieJar, TCPConnector, общими заголовками.
        """
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_concurrent * 2,
                limit_per_host=self.max_concurrent,
                ssl=self._ssl_context,
                enable_cleanup_closed=True,
                ttl_dns_cache=300,
            )
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=connector,
                cookie_jar=aiohttp.CookieJar(),
                headers=self._build_base_headers(),
            )
        return self._session

    async def close(self):
        """Корректно закрывает сессию и все соединения"""
        if self._session and not self._session.closed:
            await self._session.close()
            await asyncio.sleep(0.25)  # даём время на graceful shutdown

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    # ══════════════════════════════════════════════════════════════════════
    #  ЗАГОЛОВКИ
    # ══════════════════════════════════════════════════════════════════════

    def _get_random_ua(self) -> str:
        if USE_FAKE_UA and _ua:
            try:
                return _ua.random
            except Exception:
                pass
        return random.choice(FALLBACK_USER_AGENTS)

    def _build_base_headers(self) -> Dict[str, str]:
        """Основные заголовки для обычных запросов (страницы)"""
        return {
            'User-Agent': self._get_random_ua(),
            'Accept': ('text/html,application/xhtml+xml,'
                       'application/xml;q=0.9,*/*;q=0.8'),
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }

    def _build_download_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """
        ИСПРАВЛЕНИЕ #4: Referer при скачивании файлов.

        Многие сайты блокируют прямое скачивание без Referer.
        """
        headers = {
            'User-Agent': self._get_random_ua(),
            'Accept': ('application/octet-stream,application/pdf,'
                       'application/zip,*/*;q=0.8'),
            'Accept-Encoding': 'gzip, deflate, br',
        }
        if referer:
            headers['Referer'] = referer
        return headers

    # ══════════════════════════════════════════════════════════════════════
    #  ПОЛУЧЕНИЕ HTML СТРАНИЦ
    # ══════════════════════════════════════════════════════════════════════

    async def get_page_content(
        self,
        url: str,
        encoding: Optional[str] = None,
    ) -> Optional[str]:
        """
        Получает HTML страницы с повторными попытками.

        ИСПРАВЛЕНИЕ #7: Автоопределение кодировки.
            Если сервер отдаёт CP1251 без charset — пробуем несколько кодировок.

        ИСПРАВЛЕНИЕ #11: Обработка HTTP 429.
            Ждём Retry-After секунд.

        Args:
            url:      URL страницы
            encoding: Форсировать кодировку (напр. 'cp1251')

        Returns:
            HTML-текст или None при неудаче
        """
        session = await self._get_session()

        for attempt in range(self.max_retries):
            try:
                async with session.get(
                    url,
                    proxy=self.proxy,
                    allow_redirects=True,
                    max_redirects=10,
                ) as response:

                    # ── Успех ──────────────────────────────────────
                    if response.status == 200:
                        return await self._read_response_text(response, encoding)

                    # ── Rate limit ────────────────────────────────
                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 30))
                        logger.warning(f"⏳ HTTP 429, ждём {retry_after}s: {url}")
                        await asyncio.sleep(retry_after)
                        continue

                    # ── 403 → Ротация UA ──────────────────────────
                    if response.status == 403:
                        logger.warning(f"🚫 HTTP 403: {url} (попытка {attempt + 1})")
                        # Обновляем UA на уровне сессии
                        if self._session:
                            self._session._default_headers['User-Agent'] = (
                                self._get_random_ua()
                            )

                    # ── 5xx → сервер лежит ────────────────────────
                    elif response.status >= 500:
                        logger.warning(f"💥 HTTP {response.status}: {url}")

                    else:
                        logger.warning(f"⚠️ HTTP {response.status}: {url}")

            except asyncio.TimeoutError:
                logger.debug(f"Таймаут {url} (попытка {attempt + 1})")
            except aiohttp.ClientError as e:
                logger.debug(f"Сетевая ошибка {url} (попытка {attempt + 1}): {e}")
            except Exception as e:
                logger.debug(f"Ошибка {url} (попытка {attempt + 1}): {e}")

            # Экспоненциальный backoff с jitter
            if attempt < self.max_retries - 1:
                wait = self.delay * (attempt + 1) * (1 + random.random() * 0.5)
                await asyncio.sleep(wait)

        logger.error(f"❌ Не удалось получить {url} после {self.max_retries} попыток")
        return None

    async def _read_response_text(
        self,
        response: aiohttp.ClientResponse,
        forced_encoding: Optional[str] = None,
    ) -> str:
        """
        ИСПРАВЛЕНИЕ #7: Умное определение кодировки.

        Порядок:
        1. Если передан forced_encoding — используем его
        2. Если сервер указал charset — используем charset
        3. Пробуем UTF-8 → CP1251 → Latin-1 → UTF-8 с заменой
        """
        if forced_encoding:
            return await response.text(encoding=forced_encoding)

        # charset из Content-Type
        server_encoding = response.charset

        if server_encoding:
            try:
                return await response.text(encoding=server_encoding)
            except (UnicodeDecodeError, LookupError):
                pass

        # Читаем байты и пробуем кодировки вручную
        raw = await response.read()
        for enc in ('utf-8', 'cp1251', 'latin-1'):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue

        # Крайний случай
        return raw.decode('utf-8', errors='replace')

    # ══════════════════════════════════════════════════════════════════════
    #  ПОИСК ССЫЛОК НА ФАЙЛЫ
    # ══════════════════════════════════════════════════════════════════════

    def find_file_links(
        self,
        html: str,
        base_url: str,
        file_extensions: List[str],
    ) -> List[Dict]:
        """
        Находит ссылки на файлы в HTML.

        ИСПРАВЛЕНИЕ #3: Использует HTML_PARSER (lxml если есть, иначе html.parser).
        ИСПРАВЛЕНИЕ #12: Ищет не только в <a>, но и в <iframe>, <embed>,
                         <object>, data-href, data-url, onclick.

        Args:
            html:             HTML-код страницы
            base_url:         Базовый URL для разрешения относительных ссылок
            file_extensions:  Список расширений ('.pdf', '.doc', …)

        Returns:
            Список словарей {'url', 'text', 'filename', 'tag'}
        """
        soup = BeautifulSoup(html, HTML_PARSER)  # ← ИСПРАВЛЕНО: не хардкод 'lxml'
        links: List[Dict] = []
        seen_urls: Set[str] = set()

        # Нормализуем расширения
        norm_exts = [
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in file_extensions
        ]

        def _check_and_add(href: str, text: str = '', tag_name: str = ''):
            """Проверяет URL и добавляет к результатам если подходит"""
            if not href:
                return
            href = href.strip()
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                return

            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            # Убираем фрагмент для дедупликации
            clean_url = parsed._replace(fragment='').geturl()
            if clean_url in seen_urls:
                return

            path_lower = unquote(parsed.path).lower()
            query_lower = unquote(parsed.query).lower()

            for ext in norm_exts:
                # Проверяем путь И query-параметры (напр. ?file=manual.pdf)
                if path_lower.endswith(ext) or ext in query_lower:
                    seen_urls.add(clean_url)

                    filename = os.path.basename(unquote(parsed.path))
                    if not filename or '.' not in filename:
                        filename = self._extract_filename_from_url(clean_url)

                    links.append({
                        'url': clean_url,
                        'text': text.strip() if text else '',
                        'filename': filename,
                        'tag': tag_name,
                    })
                    break

        # ── 1. Стандартные <a href> ──────────────────────────────────
        for tag in soup.find_all('a', href=True):
            _check_and_add(tag['href'], tag.get_text(strip=True), 'a')

        # ── 2. <iframe src> (PDF-просмотрщики) ───────────────────────
        for tag in soup.find_all('iframe', src=True):
            _check_and_add(tag['src'], '', 'iframe')

        # ── 3. <embed src> ────────────────────────────────────────────
        for tag in soup.find_all('embed', src=True):
            _check_and_add(tag['src'], '', 'embed')

        # ── 4. <object data> ─────────────────────────────────────────
        for tag in soup.find_all('object', attrs={'data': True}):
            _check_and_add(tag['data'], '', 'object')

        # ── 5. data-* атрибуты ────────────────────────────────────────
        data_attrs = ['data-href', 'data-url', 'data-src',
                      'data-file', 'data-download']
        for attr_name in data_attrs:
            for tag in soup.find_all(attrs={attr_name: True}):
                _check_and_add(tag[attr_name], tag.get_text(strip=True), attr_name)

        # ── 6. onclick="window.open('/file.pdf')" ────────────────────
        for tag in soup.find_all(attrs={'onclick': True}):
            urls_in_onclick = re.findall(
                r"""['"]((?:https?://[^'"]+|/[^'"]+))['"]\s*""",
                tag['onclick'],
            )
            for match in urls_in_onclick:
                _check_and_add(match, tag.get_text(strip=True), 'onclick')

        self.stats['links_found'] += len(links)
        return links

    def find_pagination_links(self, html: str, base_url: str) -> List[str]:
        """
        ИСПРАВЛЕНИЕ #9: Находит ссылки пагинации на странице.

        Ищет по CSS-селекторам и по паттернам ?page=N, /page/N.
        """
        soup = BeautifulSoup(html, HTML_PARSER)
        pagination_urls: Set[str] = set()

        # Популярные CSS-селекторы пагинации
        selectors = [
            'nav.pagination a[href]',
            '.pagination a[href]',
            '.pager a[href]',
            '.page-numbers a[href]',
            'ul.pages a[href]',
            '.nav-links a[href]',
            'a.page-link[href]',
            'a[rel="next"][href]',
        ]
        for sel in selectors:
            try:
                for tag in soup.select(sel):
                    href = tag.get('href')
                    if href:
                        pagination_urls.add(urljoin(base_url, href))
            except Exception:
                continue

        # Паттерны ?page=N или /page/N
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full = urljoin(base_url, href)
            if re.search(r'[?&]page=\d+', full) or re.search(r'/page/\d+/?', full):
                pagination_urls.add(full)

        # Убираем текущую страницу
        pagination_urls.discard(base_url)
        return sorted(pagination_urls)

    # ══════════════════════════════════════════════════════════════════════
    #  СКАЧИВАНИЕ ФАЙЛОВ
    # ══════════════════════════════════════════════════════════════════════

    async def download_file(
        self,
        url: str,
        filename: Optional[str] = None,
        subfolder: Optional[str] = None,
        referer: Optional[str] = None,
        expected_size: Optional[int] = None,
    ) -> Optional[Path]:
        """
        Скачивает один файл с проверкой целостности.

        ИСПРАВЛЕНИЯ:
            #2: Скачивание в .tmp → rename (не остаётся битых файлов)
            #4: Referer передаётся серверу
            #5: Content-Type проверяется (HTML ≠ PDF)
            #6: Content-Disposition разбирается для имени файла

        Args:
            url:            URL файла
            filename:       Имя для сохранения (авто-определяется если не указано)
            subfolder:      Подпапка внутри download_path
            referer:        Страница, с которой пришли
            expected_size:  Ожидаемый размер (байт) для проверки целостности

        Returns:
            Path к скачанному файлу или None
        """
        # Дедупликация в рамках сессии
        if url in self._downloaded_urls:
            self.stats['files_skipped'] += 1
            return None

        if not filename:
            filename = self._extract_filename_from_url(url)
        filename = self._sanitize_filename(filename)

        if subfolder:
            save_folder = self.download_path / subfolder
            save_folder.mkdir(parents=True, exist_ok=True)
        else:
            save_folder = self.download_path

        filepath = save_folder / filename

        # ── Проверка существующего файла ─────────────────────────────
        if filepath.exists():
            existing_size = filepath.stat().st_size

            if expected_size:
                # Есть эталонный размер → сравниваем с допуском 1%
                if abs(existing_size - expected_size) < max(1024, expected_size * 0.01):
                    self._downloaded_urls.add(url)
                    self.stats['files_skipped'] += 1
                    logger.debug(f"  ⏭️ Уже есть (полный): {filename}")
                    return filepath
                else:
                    # Файл неполный → удаляем и перекачиваем
                    logger.info(f"  🔄 Перекачка (неполный {existing_size}/{expected_size}): "
                                f"{filename}")
                    filepath.unlink(missing_ok=True)
                    self.stats['files_redownloaded'] += 1
            else:
                # Нет эталона → считаем "хорошим" если больше min_file_size
                if existing_size >= self.min_file_size:
                    self._downloaded_urls.add(url)
                    self.stats['files_skipped'] += 1
                    logger.debug(f"  ⏭️ Уже есть: {filename}")
                    return filepath
                else:
                    logger.info(f"  🔄 Перекачка (слишком мал {existing_size}Б): {filename}")
                    filepath.unlink(missing_ok=True)

        # ── Скачивание с ограничением параллелизма ────────────────────
        async with self._semaphore:
            return await self._do_download(
                url, filepath, filename, referer, expected_size,
            )

    async def _do_download(
        self,
        url: str,
        filepath: Path,
        filename: str,
        referer: Optional[str],
        expected_size: Optional[int],
    ) -> Optional[Path]:
        """
        Внутренняя логика скачивания с temp-файлом.

        Поток:
            request → проверка Content-Type → парсинг Content-Disposition
            → запись в .tmp файл → проверка размера → rename в финальный файл
        """
        session = await self._get_session()
        temp_path = filepath.with_suffix(filepath.suffix + '.tmp')

        for attempt in range(self.max_retries):
            try:
                headers = self._build_download_headers(referer)

                async with session.get(
                    url,
                    headers=headers,
                    proxy=self.proxy,
                    allow_redirects=True,
                    max_redirects=10,
                ) as response:

                    # ── Проверяем статус ──────────────────────────
                    if response.status == 404:
                        logger.debug(f"  404 Not Found: {url}")
                        self.stats['errors'] += 1
                        return None  # Нет смысла повторять

                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 30))
                        logger.warning(f"  ⏳ 429 Rate Limit, ждём {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue

                    if response.status != 200:
                        logger.debug(f"  HTTP {response.status}: {url} "
                                     f"(попытка {attempt + 1})")
                        continue

                    # ── ИСПРАВЛЕНИЕ #5: Проверяем Content-Type ────
                    content_type = response.headers.get('Content-Type', '').lower()
                    file_ext = os.path.splitext(filename)[1].lower()

                    if 'text/html' in content_type and file_ext not in (
                        '.html', '.htm', '.php', '.asp', '.aspx',
                    ):
                        logger.warning(
                            f"  ⚠️ Сервер вернул HTML вместо файла: {filename}"
                        )
                        self.stats['errors'] += 1
                        return None

                    # ── ИСПРАВЛЕНИЕ #6: Content-Disposition ───────
                    content_disposition = response.headers.get(
                        'Content-Disposition', ''
                    )
                    if content_disposition:
                        cd_filename = self._parse_content_disposition(
                            content_disposition
                        )
                        if cd_filename:
                            cd_filename = self._sanitize_filename(cd_filename)
                            if cd_filename != filename:
                                logger.debug(f"  Имя из Content-Disposition: "
                                             f"{filename} → {cd_filename}")
                                filename = cd_filename
                                filepath = filepath.parent / filename
                                temp_path = filepath.with_suffix(
                                    filepath.suffix + '.tmp'
                                )

                                # Перегоняем проверку на новое имя
                                if filepath.exists():
                                    sz = filepath.stat().st_size
                                    if sz >= self.min_file_size:
                                        self._downloaded_urls.add(url)
                                        self.stats['files_skipped'] += 1
                                        return filepath

                    # ── Обновляем expected_size из Content-Length ──
                    cl = response.headers.get('Content-Length')
                    if cl:
                        try:
                            expected_size = int(cl)
                        except ValueError:
                            pass

                    # ── ИСПРАВЛЕНИЕ #2: Скачиваем в .tmp ─────────
                    downloaded = 0
                    async with aiofiles.open(temp_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(
                            16384
                        ):
                            await f.write(chunk)
                            downloaded += len(chunk)

                    # ── Проверяем минимальный размер ──────────────
                    if downloaded < self.min_file_size:
                        logger.warning(
                            f"  ⚠️ {filename}: слишком мал ({downloaded}Б), "
                            f"вероятно HTML-заглушка"
                        )
                        temp_path.unlink(missing_ok=True)
                        self.stats['errors'] += 1
                        return None

                    # ── Проверяем полноту загрузки ─────────────────
                    if expected_size and downloaded < expected_size * 0.95:
                        logger.warning(
                            f"  ⚠️ {filename}: неполный "
                            f"({downloaded}/{expected_size}Б)"
                        )
                        temp_path.unlink(missing_ok=True)
                        continue  # → retry

                    # ── Rename .tmp → финальный файл ──────────────
                    if filepath.exists():
                        filepath = self._get_unique_path(filepath)

                    temp_path.rename(filepath)

                    # ── Статистика ─────────────────────────────────
                    self._downloaded_urls.add(url)
                    self.stats['files_downloaded'] += 1
                    self.stats['total_size'] += downloaded

                    logger.info(
                        f"  📄 {filepath.name} ({self._format_size(downloaded)})"
                    )

                    # ── Вежливая задержка ──────────────────────────
                    jitter = random.random() * self.delay * 0.5
                    await asyncio.sleep(self.delay + jitter)

                    return filepath

            except asyncio.TimeoutError:
                logger.debug(f"  Таймаут {filename} (попытка {attempt + 1})")
            except asyncio.CancelledError:
                # При отмене — обязательно чистим .tmp
                temp_path.unlink(missing_ok=True)
                raise
            except aiohttp.ClientError as e:
                logger.debug(f"  Сетевая ошибка {filename} "
                             f"(попытка {attempt + 1}): {e}")
            except Exception as e:
                logger.warning(f"  Ошибка {filename} "
                               f"(попытка {attempt + 1}): {e}")
            finally:
                # Чистим .tmp если финальный файл не создался
                if temp_path.exists() and not filepath.exists():
                    temp_path.unlink(missing_ok=True)

            # Exponential backoff с jitter
            if attempt < self.max_retries - 1:
                wait = self.delay * (attempt + 1) * (1 + random.random() * 0.5)
                await asyncio.sleep(wait)

        self.stats['errors'] += 1
        logger.error(f"  ❌ Не удалось скачать: {filename}")
        return None

    # ══════════════════════════════════════════════════════════════════════
    #  ВЫСОКОУРОВНЕВЫЕ МЕТОДЫ
    # ══════════════════════════════════════════════════════════════════════

    async def download_from_page(
        self,
        url: str,
        file_extensions: Optional[List[str]] = None,
        subfolder: Optional[str] = None,
        keywords_include: Optional[List[str]] = None,
        keywords_exclude: Optional[List[str]] = None,
        follow_pagination: bool = False,
        max_pages: int = 50,
        encoding: Optional[str] = None,
    ) -> List[Path]:
        """
        Скачивает все файлы со страницы (с опциональной пагинацией).

        ИСПРАВЛЕНИЕ #9: follow_pagination=True обходит все страницы каталога.

        Args:
            url:                Начальный URL
            file_extensions:    Расширения файлов
            subfolder:          Подпапка для сохранения
            keywords_include:   Только файлы, содержащие эти слова
            keywords_exclude:   Исключить файлы с этими словами
            follow_pagination:  Переходить по страницам пагинации
            max_pages:          Макс. количество страниц для обхода
            encoding:           Принудительная кодировка

        Returns:
            Список путей к скачанным файлам
        """
        if file_extensions is None:
            file_extensions = ['.pdf', '.doc', '.docx', '.zip', '.rar']

        downloaded_files: List[Path] = []
        processed_pages: Set[str] = set()
        pages_queue: List[str] = [url]

        while pages_queue and len(processed_pages) < max_pages:
            current_url = pages_queue.pop(0)

            if current_url in processed_pages:
                continue
            processed_pages.add(current_url)

            logger.info(f"🔍 Парсим: {current_url}")

            html = await self.get_page_content(current_url, encoding=encoding)
            if not html:
                logger.error(f"❌ Не удалось получить: {current_url}")
                continue

            self.stats['pages_processed'] += 1

            # ── Находим ссылки на файлы ───────────────────────────
            file_links = self.find_file_links(html, current_url, file_extensions)
            logger.info(f"📎 Найдено ссылок: {len(file_links)}")

            # ── Находим пагинацию ─────────────────────────────────
            if follow_pagination:
                pagination = self.find_pagination_links(html, current_url)
                for pg_url in pagination:
                    if pg_url not in processed_pages:
                        pages_queue.append(pg_url)
                if pagination:
                    logger.debug(
                        f"  📄 Найдено страниц пагинации: {len(pagination)}"
                    )

            # ── Фильтруем и скачиваем ─────────────────────────────
            for link_info in file_links:
                search_text = (
                    f"{link_info['filename']} {link_info['text']}"
                ).lower()

                if keywords_include:
                    if not any(kw.lower() in search_text
                               for kw in keywords_include):
                        continue

                if keywords_exclude:
                    if any(kw.lower() in search_text
                           for kw in keywords_exclude):
                        continue

                filepath = await self.download_file(
                    url=link_info['url'],
                    filename=link_info['filename'],
                    subfolder=subfolder,
                    referer=current_url,  # ← ИСПРАВЛЕНИЕ #4
                )

                if filepath:
                    downloaded_files.append(filepath)

            # Вежливая задержка между страницами
            if pages_queue:
                await asyncio.sleep(self.delay)

        return downloaded_files

    async def download_from_multiple_pages(
        self,
        urls: List[str],
        file_extensions: Optional[List[str]] = None,
        subfolder: Optional[str] = None,
        keywords_include: Optional[List[str]] = None,
        keywords_exclude: Optional[List[str]] = None,
    ) -> List[Path]:
        """Скачивает файлы с нескольких страниц последовательно"""
        all_files: List[Path] = []

        for url in urls:
            files = await self.download_from_page(
                url=url,
                file_extensions=file_extensions,
                subfolder=subfolder,
                keywords_include=keywords_include,
                keywords_exclude=keywords_exclude,
            )
            all_files.extend(files)

        return all_files

    # ══════════════════════════════════════════════════════════════════════
    #  УТИЛИТЫ
    # ══════════════════════════════════════════════════════════════════════

    def _extract_filename_from_url(self, url: str) -> str:
        """Извлекает имя файла из URL, включая query-параметры"""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        filename = os.path.basename(path)

        if not filename or '.' not in filename:
            # Ищем имя в query-параметрах: ?file=manual.pdf
            query = parse_qs(parsed.query)
            for param in ('file', 'filename', 'name', 'f', 'download', 'dl'):
                if param in query:
                    candidate = query[param][0]
                    if '.' in candidate:
                        filename = candidate
                        break

        if not filename or filename == '/':
            # Генерируем уникальное имя на основе URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f'file_{url_hash}'

        return filename

    def _sanitize_filename(self, filename: str) -> str:
        """Очищает имя файла от недопустимых символов"""
        invalid_chars = '<>:"/\\|?*\n\r\t\x00'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        filename = re.sub(r'_+', '_', filename)
        filename = re.sub(r'\s+', ' ', filename).strip().strip('.')

        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200 - len(ext)] + ext

        return filename if filename and filename not in ('_', '') else 'unnamed_file'

    def _parse_content_disposition(self, cd: str) -> Optional[str]:
        """
        ИСПРАВЛЕНИЕ #6: Парсинг Content-Disposition для реального имени файла.

        Поддерживает:
            filename*=UTF-8''%D0%BC%D0%B0%D0%BD%D1%83%D0%B0%D0%BB.pdf
            filename="manual.pdf"
            filename=manual.pdf
        """
        # RFC 5987: filename*=UTF-8''encoded_name
        match = re.search(
            r"filename\*\s*=\s*(?:UTF-8|utf-8)''(.+?)(?:\s*;|$)", cd, re.I
        )
        if match:
            return unquote(match.group(1).strip().strip('"'))

        # Обычный filename="..."
        match = re.search(r'filename\s*=\s*"?([^";\n]+)"?', cd, re.I)
        if match:
            return unquote(match.group(1).strip())

        return None

    def _get_unique_path(self, filepath: Path) -> Path:
        """Генерирует уникальное имя, если файл уже существует"""
        if not filepath.exists():
            return filepath

        stem = filepath.stem
        ext = filepath.suffix
        parent = filepath.parent

        for counter in range(1, 10000):
            new_path = parent / f"{stem}_{counter}{ext}"
            if not new_path.exists():
                return new_path

        # Крайний случай
        url_hash = hashlib.md5(str(filepath).encode()).hexdigest()[:6]
        return parent / f"{stem}_{url_hash}{ext}"

    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер в человеко-читаемый вид"""
        for unit in ('Б', 'КБ', 'МБ', 'ГБ'):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} ТБ"

    def get_stats(self) -> Dict:
        """Возвращает статистику скачивания"""
        return {
            **self.stats,
            'total_size_formatted': self._format_size(self.stats['total_size']),
        }

    def reset_stats(self):
        """Сбрасывает счётчики (между источниками)"""
        for key in self.stats:
            self.stats[key] = 0
