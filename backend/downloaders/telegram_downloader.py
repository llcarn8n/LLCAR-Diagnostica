"""
═══════════════════════════════════════════════════════════════════════════════
            TELEGRAM DOWNLOADER v3 — С ПРОСМОТРОМ И ВЫБОРОМ ФАЙЛОВ
═══════════════════════════════════════════════════════════════════════════════

НОВОЕ:
    ✅ list_channel_files() — просмотр содержимого канала БЕЗ скачивания
    ✅ download_selected_files() — скачивание выбранных файлов по ID
    ✅ Temp-файл → rename (атомарное скачивание)
    ✅ Progress callback (прогресс-бар)
    ✅ Корректный сброс статистики между каналами
    ✅ Защита от FloodWait с адаптивной задержкой
    ✅ Session file в configurable директории
    ✅ Ленивая синхронизация трекера (не при каждом старте)

ИСПОЛЬЗОВАНИЕ:
    # Режим 1: Просмотр содержимого канала
    files = await downloader.list_channel_files('@channel', extensions=['.pdf'])
    for f in files:
        print(f"[{f['message_id']}] {f['filename']} ({f['size_str']})")

    # Режим 2: Скачивание выбранных файлов
    selected_ids = [123, 456, 789]
    results = await downloader.download_selected_files('@channel', selected_ids)

    # Режим 3: Автоматическое скачивание всех (как раньше)
    results = await downloader.download_from_channel('@channel', ...)
"""

import os
import re
import json
import asyncio
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict

from telethon import TelegramClient
from telethon.tl.types import (
    DocumentAttributeFilename,
    MessageMediaDocument,
    MessageMediaPhoto,
    Channel,
    Chat,
)
from telethon.errors import (
    FloodWaitError,
    ChannelPrivateError,
    UsernameNotOccupiedError,
    ChatAdminRequiredError,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  ПАРСЕР TELEGRAM-ССЫЛОК
# ═══════════════════════════════════════════════════════════════════════════

class TelegramLinkParser:
    """
    Парсинг и скачивание по Telegram-ссылкам.

    Поддерживаемые форматы:
        https://t.me/channel_name/12345
        https://t.me/c/1234567890/12345   (приватные каналы)
        tg://resolve?domain=channel&post=12345
    """

    # Паттерны ссылок
    PATTERNS = [
        # https://t.me/channel/123
        re.compile(
            r'(?:https?://)?t\.me/(?P<channel>[a-zA-Z][\w]{3,30})/(?P<msg_id>\d+)'
        ),
        # https://t.me/c/1234567890/123 (приватные по ID)
        re.compile(
            r'(?:https?://)?t\.me/c/(?P<channel_id>\d+)/(?P<msg_id>\d+)'
        ),
        # tg://resolve?domain=channel&post=123
        re.compile(
            r'tg://resolve\?domain=(?P<channel>\w+)&post=(?P<msg_id>\d+)'
        ),
    ]

    @staticmethod
    def parse_link(url: str) -> Optional[Dict[str, Any]]:
        """
        Парсит Telegram-ссылку.

        Returns:
            {'channel': '@name' или channel_id, 'message_id': 123}
            или None если не распознана

        Примеры:
            parse_link('https://t.me/avtomanualy/1500')
            → {'channel': 'avtomanualy', 'message_id': 1500}

            parse_link('https://t.me/c/1234567890/500')
            → {'channel_id': 1234567890, 'message_id': 500}
        """
        url = url.strip()

        for pattern in TelegramLinkParser.PATTERNS:
            match = pattern.match(url)
            if match:
                groups = match.groupdict()
                result = {'message_id': int(groups['msg_id'])}

                if 'channel' in groups and groups['channel']:
                    result['channel'] = groups['channel']
                elif 'channel_id' in groups:
                    result['channel_id'] = int(groups['channel_id'])

                return result

        return None

    @staticmethod
    def parse_multiple(text: str) -> List[Dict]:
        """
        Находит ВСЕ Telegram-ссылки в тексте.

        Удобно для вставки списка ссылок из буфера обмена.
        """
        results = []
        for pattern in TelegramLinkParser.PATTERNS:
            for match in pattern.finditer(text):
                parsed = TelegramLinkParser.parse_link(match.group(0))
                if parsed and parsed not in results:
                    results.append(parsed)
        return results


# ═══════════════════════════════════════════════════════════════════════════
#  DATACLASS ДЛЯ ИНФОРМАЦИИ О ФАЙЛЕ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TelegramFileInfo:
    """Информация о файле в Telegram-канале"""
    message_id: int
    filename: str
    size: int
    size_str: str = ''
    mime_type: str = ''
    date: Optional[datetime] = None
    caption: str = ''
    channel: str = ''
    extension: str = ''

    # Состояние
    is_downloaded: bool = False
    local_path: Optional[str] = None

    def __post_init__(self):
        if not self.size_str:
            self.size_str = self._format_size(self.size)
        if not self.extension:
            self.extension = os.path.splitext(self.filename)[1].lower()

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ('Б', 'КБ', 'МБ', 'ГБ'):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} ТБ"


# ═══════════════════════════════════════════════════════════════════════════
#  ТРЕКЕР СКАЧАННЫХ ФАЙЛОВ (УЛУЧШЕННЫЙ)
# ═══════════════════════════════════════════════════════════════════════════

class DownloadedFilesTracker:
    """
    Отслеживает скачанные файлы.

    ИСПРАВЛЕНИЯ:
        - Блокировка при записи (asyncio.Lock)
        - Ленивая синхронизация с диском (по запросу, не при старте)
        - Нормализация имён через frozenset
        - Compact формат для экономии памяти
    """

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.db_file = self.base_path / 'downloaded_files.json'
        self._names: Set[str] = set()
        self._data: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
        self._dirty = False

        self._load()

    def _normalize(self, filename: str) -> str:
        return filename.lower().strip()

    def _load(self):
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                for key, data in self._data.items():
                    name = data.get('filename', key.split('|')[0])
                    self._names.add(self._normalize(name))
                logger.info(
                    f"📂 Трекер: {len(self._names)} файлов в базе"
                )
            except Exception as e:
                logger.warning(f"Ошибка загрузки базы: {e}")
                self._data = {}
                self._names = set()
        else:
            logger.info("📂 Создаём новую базу трекера")

    def _save(self):
        """Сохраняет базу (вызывается под _lock)"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)

            # Атомарная запись через temp-файл
            tmp = self.db_file.with_suffix('.json.tmp')
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=1, default=str)
            tmp.replace(self.db_file)
            self._dirty = False
        except Exception as e:
            logger.warning(f"Ошибка сохранения базы: {e}")

    def sync_with_disk(self, scan_folder: Path):
        """
        Синхронизация с диском — вызывать ВРУЧНУЮ, не при каждом старте.
        """
        if not scan_folder.exists():
            return

        logger.info(f"🔄 Синхронизация с диском: {scan_folder}")
        added = 0

        for filepath in scan_folder.rglob('*'):
            if not filepath.is_file():
                continue
            norm = self._normalize(filepath.name)
            if norm not in self._names:
                key = f"{norm}|{filepath.stat().st_size}"
                self._data[key] = {
                    'filename': filepath.name,
                    'size': filepath.stat().st_size,
                    'filepath': str(filepath),
                    'date': datetime.now().isoformat(),
                }
                self._names.add(norm)
                added += 1

        if added > 0:
            logger.info(f"   ✅ Добавлено с диска: {added}")
            self._save()

    def is_downloaded(self, filename: str) -> bool:
        return self._normalize(filename) in self._names

    async def mark_downloaded(
        self,
        filename: str,
        size: int,
        channel: str = '',
        filepath: str = '',
    ):
        """Потокобезопасная пометка файла"""
        async with self._lock:
            norm = self._normalize(filename)
            key = f"{norm}|{size}"
            self._names.add(norm)
            self._data[key] = {
                'filename': filename,
                'size': size,
                'channel': channel,
                'filepath': str(filepath),
                'date': datetime.now().isoformat(),
            }
            self._dirty = True

    async def flush(self):
        """Сохраняет накопленные изменения"""
        async with self._lock:
            if self._dirty:
                self._save()

    def get_count(self) -> int:
        return len(self._names)


# ═══════════════════════════════════════════════════════════════════════════
#  ОСНОВНОЙ КЛАСС ЗАГРУЗЧИКА
# ═══════════════════════════════════════════════════════════════════════════

class TelegramDownloader:
    """
    Скачивание из Telegram-каналов с просмотром и выбором файлов.

    НОВЫЕ МЕТОДЫ:
        list_channel_files()      — список файлов в канале (БЕЗ скачивания)
        download_selected_files() — скачивание выбранных по message_id
        get_channel_info()        — информация о канале
    """

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
        download_path: Path,
        session_dir: Optional[Path] = None,
        session_name: str = 'telegram_session',
        base_delay: float = 0.5,
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.base_delay = base_delay

        # Session file в указанной директории (не в cwd)
        if session_dir:
            session_dir = Path(session_dir)
            session_dir.mkdir(parents=True, exist_ok=True)
            self._session_path = str(session_dir / session_name)
        else:
            data_dir = self.download_path.parent / '.sessions'
            data_dir.mkdir(parents=True, exist_ok=True)
            self._session_path = str(data_dir / session_name)

        self.client: Optional[TelegramClient] = None

        # Трекер
        self.tracker = DownloadedFilesTracker(
            base_path=self.download_path.parent
        )

        # Адаптивная задержка: увеличивается при FloodWait
        self._current_delay = base_delay

        self.stats = self._empty_stats()

    def _empty_stats(self) -> Dict[str, int]:
        return {
            'messages_processed': 0,
            'files_found': 0,
            'files_downloaded': 0,
            'files_skipped': 0,
            'files_existed': 0,
            'errors': 0,
            'total_size': 0,
        }

    def reset_stats(self):
        self.stats = self._empty_stats()

    # ══════════════════════════════════════════════════════════════════
    #  ПОДКЛЮЧЕНИЕ / ОТКЛЮЧЕНИЕ
    # ══════════════════════════════════════════════════════════════════

    async def connect(self) -> bool:
        """Подключается к Telegram"""
        try:
            self._check_crypto()

            self.client = TelegramClient(
                self._session_path,
                self.api_id,
                self.api_hash,
            )

            await self.client.start(phone=self.phone)

            me = await self.client.get_me()
            logger.info(
                f"✅ Telegram: {me.first_name} "
                f"(@{me.username or 'нет username'})"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Telegram: {e}")
            return False

    async def disconnect(self):
        """Отключается и сохраняет трекер"""
        await self.tracker.flush()
        if self.client:
            await self.client.disconnect()
            logger.info("📴 Telegram: отключено")

    def _check_crypto(self):
        """Проверяет крипто-модули"""
        try:
            import cryptg  # noqa: F401
            logger.info("   🚀 cryptg — быстрое шифрование")
        except ImportError:
            try:
                from Crypto.Cipher import AES  # noqa: F401
                logger.info("   ⚡ pycryptodome — среднее шифрование")
            except ImportError:
                logger.warning("   ⚠️ Нет крипто-ускорителей — медленно!")

    async def _resolve_channel(self, channel_username: str):
        """Разрешает канал/чат по username"""
        try:
            entity = await self.client.get_entity(channel_username)
            return entity
        except UsernameNotOccupiedError:
            logger.error(f"❌ Канал @{channel_username} не найден!")
            return None
        except ChannelPrivateError:
            logger.error(f"❌ Канал @{channel_username} приватный!")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка @{channel_username}: {e}")
            return None

    # ══════════════════════════════════════════════════════════════════
    #  НОВОЕ: ИНФОРМАЦИЯ О КАНАЛЕ
    # ══════════════════════════════════════════════════════════════════

    async def get_channel_info(self, channel_username: str) -> Optional[Dict]:
        """
        Получает информацию о канале.

        Returns:
            {
                'title': 'Название',
                'username': 'username',
                'participants_count': 12345,
                'description': '...',
                'is_channel': True/False,
            }
        """
        if not self.client:
            raise RuntimeError("Не подключен к Telegram!")

        entity = await self._resolve_channel(channel_username)
        if not entity:
            return None

        info = {
            'title': getattr(entity, 'title', ''),
            'username': getattr(entity, 'username', ''),
            'id': entity.id,
            'is_channel': isinstance(entity, Channel) and entity.broadcast,
        }

        try:
            full = await self.client.get_entity(entity)
            if hasattr(full, 'participants_count'):
                info['participants_count'] = full.participants_count
        except Exception:
            pass

        return info

    # ══════════════════════════════════════════════════════════════════
    #  НОВОЕ: ПРОСМОТР СОДЕРЖИМОГО КАНАЛА
    # ══════════════════════════════════════════════════════════════════

    async def list_channel_files(
        self,
        channel_username: str,
        allowed_extensions: Optional[List[str]] = None,
        max_size_mb: int = 500,
        message_limit: Optional[int] = None,
        keywords_include: Optional[List[str]] = None,
        keywords_exclude: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[TelegramFileInfo]:
        """
        НОВЫЙ МЕТОД: Просматривает содержимое канала БЕЗ скачивания.

        Возвращает список ВСЕХ файлов с метаданными.
        Пользователь затем может выбрать нужные для скачивания.

        Args:
            channel_username:    @username канала
            allowed_extensions:  Фильтр расширений (None = все)
            max_size_mb:         Макс. размер файла
            message_limit:       Лимит сообщений (None = все)
            keywords_include:    Фильтр по словам (включить)
            keywords_exclude:    Фильтр по словам (исключить)
            progress_callback:   fn(processed_count, status_text)

        Returns:
            List[TelegramFileInfo] — список файлов с пометкой is_downloaded

        Пример:
            files = await dl.list_channel_files('@mychannel', ['.pdf'])
            for f in files:
                status = '✅' if f.is_downloaded else '⬜'
                print(f"{status} [{f.message_id}] {f.filename} ({f.size_str})")
        """
        if not self.client:
            raise RuntimeError("Не подключен к Telegram!")

        entity = await self._resolve_channel(channel_username)
        if not entity:
            return []

        title = getattr(entity, 'title', channel_username)
        logger.info(f"📋 Сканирование канала: {title}")

        files: List[TelegramFileInfo] = []
        processed = 0
        norm_exts = None
        if allowed_extensions:
            norm_exts = {
                ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
                for ext in allowed_extensions
            }

        try:
            async for message in self.client.iter_messages(
                entity, limit=message_limit
            ):
                processed += 1

                if processed % 200 == 0:
                    status = f"Обработано {processed} сообщений, найдено {len(files)} файлов..."
                    logger.info(f"   {status}")
                    if progress_callback:
                        progress_callback(processed, status)

                # Извлекаем информацию о файле
                file_info = self._extract_file_info(message, channel_username)
                if not file_info:
                    continue

                # Фильтр по расширению
                if norm_exts and file_info.extension not in norm_exts:
                    continue

                # Фильтр по размеру
                if file_info.size > max_size_mb * 1024 * 1024:
                    continue

                # Фильтр по ключевым словам
                search_text = f"{file_info.filename} {file_info.caption}".lower()
                if keywords_include:
                    if not any(kw.lower() in search_text for kw in keywords_include):
                        continue
                if keywords_exclude:
                    if any(kw.lower() in search_text for kw in keywords_exclude):
                        continue

                # Проверяем — уже скачан?
                safe_name = self._sanitize_filename(file_info.filename)
                file_info.filename = safe_name
                file_info.is_downloaded = self.tracker.is_downloaded(safe_name)

                # Проверка на диске
                if not file_info.is_downloaded:
                    channel_folder = self.download_path / channel_username
                    fp = channel_folder / safe_name
                    if fp.exists() and fp.stat().st_size > 100:
                        file_info.is_downloaded = True
                        file_info.local_path = str(fp)

                files.append(file_info)

        except FloodWaitError as e:
            logger.warning(f"⏳ FloodWait {e.seconds}s при сканировании")
            await asyncio.sleep(e.seconds + 1)
        except Exception as e:
            logger.error(f"❌ Ошибка сканирования: {e}")

        logger.info(
            f"📊 Найдено файлов: {len(files)} "
            f"(скачано: {sum(1 for f in files if f.is_downloaded)}, "
            f"новых: {sum(1 for f in files if not f.is_downloaded)})"
        )

        return files

    # ══════════════════════════════════════════════════════════════════
    #  НОВОЕ: СКАЧИВАНИЕ ВЫБРАННЫХ ФАЙЛОВ
    # ══════════════════════════════════════════════════════════════════

    async def download_selected_files(
        self,
        channel_username: str,
        message_ids: List[int],
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> List[Dict]:
        """
        НОВЫЙ МЕТОД: Скачивает только выбранные файлы по message_id.

        Args:
            channel_username:   @username канала
            message_ids:        Список message_id для скачивания
            progress_callback:  fn(filename, bytes_downloaded, total_bytes)

        Returns:
            List[Dict] — список скачанных файлов

        Пример:
            # Пользователь выбрал файлы с ID 100, 200, 300
            results = await dl.download_selected_files(
                '@mychannel', [100, 200, 300]
            )
        """
        if not self.client:
            raise RuntimeError("Не подключен к Telegram!")

        entity = await self._resolve_channel(channel_username)
        if not entity:
            return []

        channel_folder = self.download_path / channel_username
        channel_folder.mkdir(parents=True, exist_ok=True)

        downloaded = []
        total = len(message_ids)

        logger.info(f"📥 Скачивание {total} выбранных файлов из @{channel_username}")

        for idx, msg_id in enumerate(message_ids, 1):
            try:
                # Получаем конкретное сообщение
                message = await self.client.get_messages(entity, ids=msg_id)
                if not message:
                    logger.warning(f"   ⚠️ Сообщение #{msg_id} не найдено")
                    continue

                file_info = self._extract_file_info(message, channel_username)
                if not file_info:
                    logger.warning(f"   ⚠️ Сообщение #{msg_id} не содержит файла")
                    continue

                safe_name = self._sanitize_filename(file_info.filename)
                filepath = channel_folder / safe_name
                temp_path = filepath.with_suffix(filepath.suffix + '.tmp')

                # Пропуск если уже есть
                if filepath.exists() and filepath.stat().st_size > 100:
                    logger.info(f"   ⏭️ [{idx}/{total}] {safe_name} (уже есть)")
                    continue

                # Скачиваем в temp-файл
                logger.info(
                    f"   📄 [{idx}/{total}] {safe_name} "
                    f"({file_info.size_str})"
                )

                # Progress callback для Telethon
                def _make_progress_cb(fname, total_size):
                    last_report = [0]
                    def cb(current, total):
                        pct = int(current / total * 100) if total else 0
                        if pct - last_report[0] >= 10:
                            last_report[0] = pct
                            logger.info(f"      ↳ {pct}%")
                            if progress_callback:
                                progress_callback(fname, current, total)
                    return cb

                await self.client.download_media(
                    message,
                    file=str(temp_path),
                    progress_callback=_make_progress_cb(safe_name, file_info.size),
                )

                # Проверяем что скачалось
                if not temp_path.exists():
                    logger.error(f"   ❌ Temp-файл не создан: {safe_name}")
                    self.stats['errors'] += 1
                    continue

                dl_size = temp_path.stat().st_size
                if file_info.size > 0 and dl_size < file_info.size * 0.9:
                    logger.warning(
                        f"   ⚠️ Неполный: {safe_name} "
                        f"({dl_size}/{file_info.size})"
                    )
                    temp_path.unlink(missing_ok=True)
                    self.stats['errors'] += 1
                    continue

                # Rename temp → final
                temp_path.rename(filepath)

                # Регистрируем
                await self.tracker.mark_downloaded(
                    safe_name, file_info.size, channel_username, str(filepath)
                )

                self.stats['files_downloaded'] += 1
                self.stats['total_size'] += file_info.size

                downloaded.append({
                    'filepath': filepath,
                    'filename': safe_name,
                    'size': file_info.size,
                    'caption': file_info.caption,
                    'date': file_info.date,
                    'channel': channel_username,
                    'message_id': msg_id,
                })

                # Адаптивная задержка
                await asyncio.sleep(self._current_delay)

            except FloodWaitError as e:
                logger.warning(f"   ⏳ FloodWait {e.seconds}s")
                self._current_delay = min(
                    self._current_delay * 2, 10.0
                )
                await asyncio.sleep(e.seconds + 1)

            except asyncio.CancelledError:
                # Чистим temp
                if 'temp_path' in dir() and temp_path.exists():
                    temp_path.unlink(missing_ok=True)
                raise

            except Exception as e:
                logger.error(f"   ❌ Ошибка #{msg_id}: {e}")
                self.stats['errors'] += 1

        # Flush трекера
        await self.tracker.flush()

        logger.info(f"✅ Скачано: {len(downloaded)} из {total}")
        return downloaded

    # ══════════════════════════════════════════════════════════════════
    #  СКАЧИВАНИЕ ПО TELEGRAM-ССЫЛКАМ
    # ══════════════════════════════════════════════════════════════════

    async def download_by_link(
        self,
        link: str,
        save_folder: Optional[Path] = None,
    ) -> Optional[Dict]:
        """
        НОВЫЙ МЕТОД: Скачивание файла по Telegram-ссылке.

        Args:
            link: 'https://t.me/channel/12345'
            save_folder: куда сохранить (default: download_path)

        Returns:
            Dict с информацией о скачанном файле или None

        Пример:
            result = await dl.download_by_link('https://t.me/avtomanualy/1500')
        """
        if not self.client:
            raise RuntimeError("Не подключен к Telegram!")

        parsed = TelegramLinkParser.parse_link(link)
        if not parsed:
            logger.error(f"❌ Не удалось распознать ссылку: {link}")
            return None

        msg_id = parsed['message_id']

        # Определяем канал
        if 'channel' in parsed:
            channel = parsed['channel']
            entity = await self._resolve_channel(channel)
        elif 'channel_id' in parsed:
            try:
                entity = await self.client.get_entity(parsed['channel_id'])
                channel = getattr(entity, 'username', str(parsed['channel_id']))
            except Exception as e:
                logger.error(f"❌ Канал ID {parsed['channel_id']}: {e}")
                return None
        else:
            return None

        if not entity:
            return None

        # Получаем сообщение
        try:
            message = await self.client.get_messages(entity, ids=msg_id)
        except Exception as e:
            logger.error(f"❌ Сообщение #{msg_id}: {e}")
            return None

        if not message:
            logger.error(f"❌ Сообщение #{msg_id} не найдено")
            return None

        file_info = self._extract_file_info(message, channel)
        if not file_info:
            logger.error(f"❌ Сообщение #{msg_id} не содержит файла")
            return None

        # Скачиваем через существующий download_selected_files
        results = await self.download_selected_files(
            channel_username=channel,
            message_ids=[msg_id],
        )

        return results[0] if results else None

    async def download_by_links(
        self,
        links: List[str],
    ) -> List[Dict]:
        """
        НОВЫЙ МЕТОД: Пакетное скачивание по списку ссылок.

        Args:
            links: ['https://t.me/ch1/100', 'https://t.me/ch2/200', ...]

        Returns:
            Список скачанных файлов
        """
        # Группируем по каналам для одного подключения
        by_channel: Dict[str, List[int]] = {}

        for link in links:
            parsed = TelegramLinkParser.parse_link(link)
            if parsed:
                ch = parsed.get('channel', str(parsed.get('channel_id', '')))
                if ch not in by_channel:
                    by_channel[ch] = []
                by_channel[ch].append(parsed['message_id'])
            else:
                logger.warning(f"⚠️ Не распознана: {link}")

        all_results = []
        for channel, msg_ids in by_channel.items():
            logger.info(f"📥 @{channel}: {len(msg_ids)} файлов")
            results = await self.download_selected_files(channel, msg_ids)
            all_results.extend(results)

        return all_results

    # ══════════════════════════════════════════════════════════════════
    #  МАССОВОЕ СКАЧИВАНИЕ (УЛУЧШЕННОЕ)
    # ══════════════════════════════════════════════════════════════════

    async def download_from_channel(
        self,
        channel_username: str,
        allowed_extensions: List[str],
        max_size_mb: int = 500,
        message_limit: Optional[int] = None,
        keywords_include: Optional[List[str]] = None,
        keywords_exclude: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """
        Автоматически скачивает все подходящие файлы из канала.

        УЛУЧШЕНИЯ:
            - Temp-файл → rename (атомарность)
            - Адаптивная задержка (FloodWait protection)
            - Progress callback
            - Периодический flush трекера
        """
        if not self.client:
            raise RuntimeError("Не подключен к Telegram!")

        # Сброс статистики для этого канала
        self.reset_stats()
        downloaded_files = []

        entity = await self._resolve_channel(channel_username)
        if not entity:
            return downloaded_files

        title = getattr(entity, 'title', channel_username)
        logger.info(f"📢 Канал: {title}")

        channel_folder = self.download_path / channel_username
        channel_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"📂 Папка: {channel_folder}")
        logger.info(f"🗄️ В базе: {self.tracker.get_count()} файлов")
        logger.info("🔍 Сканирование...")

        norm_exts = {
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in allowed_extensions
        }

        flush_counter = 0

        try:
            async for message in self.client.iter_messages(
                entity, limit=message_limit
            ):
                self.stats['messages_processed'] += 1

                if self.stats['messages_processed'] % 100 == 0:
                    logger.info(
                        f"   Обработано: {self.stats['messages_processed']} "
                        f"сообщений, скачано: {self.stats['files_downloaded']}..."
                    )

                file_info = self._extract_file_info(message, channel_username)
                if not file_info:
                    continue

                self.stats['files_found'] += 1

                # Фильтры
                if file_info.extension not in norm_exts:
                    self.stats['files_skipped'] += 1
                    continue

                if file_info.size > max_size_mb * 1024 * 1024:
                    self.stats['files_skipped'] += 1
                    continue

                search_text = f"{file_info.filename} {file_info.caption}".lower()
                if keywords_include:
                    if not any(kw.lower() in search_text for kw in keywords_include):
                        self.stats['files_skipped'] += 1
                        continue
                if keywords_exclude:
                    if any(kw.lower() in search_text for kw in keywords_exclude):
                        self.stats['files_skipped'] += 1
                        continue

                safe_name = self._sanitize_filename(file_info.filename)

                # Проверка дубликатов
                if self.tracker.is_downloaded(safe_name):
                    self.stats['files_existed'] += 1
                    continue

                filepath = channel_folder / safe_name
                if filepath.exists() and filepath.stat().st_size > 100:
                    await self.tracker.mark_downloaded(
                        safe_name, filepath.stat().st_size,
                        channel_username, str(filepath)
                    )
                    self.stats['files_existed'] += 1
                    continue

                # ═══ СКАЧИВАНИЕ (с temp-файлом) ═══
                temp_path = filepath.with_suffix(filepath.suffix + '.tmp')

                try:
                    logger.info(
                        f"   📄 {safe_name} ({file_info.size_str})"
                    )

                    await self.client.download_media(
                        message,
                        file=str(temp_path),
                        progress_callback=None,
                    )

                    # Проверка
                    if temp_path.exists():
                        dl_size = temp_path.stat().st_size
                        if file_info.size > 0 and dl_size < file_info.size * 0.9:
                            logger.warning(
                                f"   ⚠️ Неполный ({dl_size}/{file_info.size})"
                            )
                            temp_path.unlink(missing_ok=True)
                            self.stats['errors'] += 1
                            continue

                        # Rename
                        temp_path.rename(filepath)
                    else:
                        logger.warning(f"   ⚠️ Не создан: {safe_name}")
                        self.stats['errors'] += 1
                        continue

                    # Регистрируем
                    await self.tracker.mark_downloaded(
                        safe_name, file_info.size,
                        channel_username, str(filepath)
                    )

                    self.stats['files_downloaded'] += 1
                    self.stats['total_size'] += file_info.size

                    downloaded_files.append({
                        'filepath': filepath,
                        'filename': safe_name,
                        'size': file_info.size,
                        'caption': file_info.caption,
                        'date': file_info.date,
                        'channel': channel_username,
                    })

                    # Адаптивная задержка
                    await asyncio.sleep(self._current_delay)

                    # Периодический flush
                    flush_counter += 1
                    if flush_counter % 10 == 0:
                        await self.tracker.flush()

                except FloodWaitError as e:
                    logger.warning(f"   ⏳ FloodWait {e.seconds}s")
                    self._current_delay = min(
                        self._current_delay * 2, 10.0
                    )
                    await asyncio.sleep(e.seconds + 1)

                except asyncio.CancelledError:
                    temp_path.unlink(missing_ok=True)
                    raise

                except Exception as e:
                    logger.error(f"   ❌ Ошибка: {e}")
                    self.stats['errors'] += 1
                    temp_path.unlink(missing_ok=True)

        except FloodWaitError as e:
            logger.warning(f"⏳ FloodWait при итерации: {e.seconds}s")
            await asyncio.sleep(e.seconds + 1)
        except Exception as e:
            logger.error(f"❌ Ошибка канала: {e}")
            self.stats['errors'] += 1

        # Flush
        await self.tracker.flush()

        # Итоги
        logger.info(f"✅ @{channel_username}:")
        logger.info(f"   Сообщений: {self.stats['messages_processed']}")
        logger.info(f"   Скачано: {len(downloaded_files)}")
        logger.info(f"   Пропущено: {self.stats['files_existed']}")

        return downloaded_files

    # ══════════════════════════════════════════════════════════════════
    #  УТИЛИТЫ
    # ══════════════════════════════════════════════════════════════════

    def _extract_file_info(
        self, message, channel: str = ''
    ) -> Optional[TelegramFileInfo]:
        """Извлекает информацию о файле из сообщения"""
        if not message.media:
            return None
        if not isinstance(message.media, MessageMediaDocument):
            return None

        doc = message.document
        if not doc:
            return None

        # Имя файла
        filename = None
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                filename = attr.file_name
                break

        if not filename:
            ext = self._mime_to_ext(doc.mime_type)
            filename = f"document_{message.id}{ext}"

        return TelegramFileInfo(
            message_id=message.id,
            filename=filename,
            size=doc.size or 0,
            mime_type=doc.mime_type or '',
            date=message.date,
            caption=message.message or '',
            channel=channel,
        )

    def _mime_to_ext(self, mime_type: str) -> str:
        mime_map = {
            'application/pdf': '.pdf',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'application/vnd.rar': '.rar',
            'application/x-7z-compressed': '.7z',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument'
            '.wordprocessingml.document': '.docx',
            'application/epub+zip': '.epub',
            'image/vnd.djvu': '.djvu',
            'application/x-bittorrent': '.torrent',
        }
        return mime_map.get(mime_type, '')

    def _sanitize_filename(self, filename: str) -> str:
        for c in '<>:"/\\|?*\n\r\t\x00':
            filename = filename.replace(c, '_')
        filename = re.sub(r'_+', '_', filename)
        filename = re.sub(r'\s+', ' ', filename).strip().strip('.')
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200 - len(ext)] + ext
        return filename if filename else 'unnamed'

    def get_stats(self) -> Dict:
        return {
            **self.stats,
            'total_size_formatted': TelegramFileInfo._format_size(
                self.stats['total_size']
            ),
            'tracked_files': self.tracker.get_count(),
        }
