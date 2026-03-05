"""
═══════════════════════════════════════════════════════════════════════════════
                        GITHUB DOWNLOADER (НОВЫЙ МОДУЛЬ)
═══════════════════════════════════════════════════════════════════════════════

ОПИСАНИЕ:
    Модуль для скачивания файлов из GitHub репозиториев через API

ВОЗМОЖНОСТИ:
    - Получение списка файлов из репозитория через GitHub API v3
    - Скачивание отдельных файлов без клонирования всего репо
    - Фильтрация по расширениям и ключевым словам
    - Работа с публичными репозиториями без токена
    - Поддержка rate limiting (ограничения запросов)

ПРЕИМУЩЕСТВА ПЕРЕД git clone:
    - Не нужен Git клиент
    - Скачиваются только нужные файлы (экономия трафика)
    - Быстрее для небольших коллекций файлов

GITHUB API:
    - Документация: https://docs.github.com/en/rest
    - Лимит без авторизации: 60 запросов в час
    - Лимит с токеном: 5000 запросов в час
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Dict, Optional
import logging
import json
from urllib.parse import urlparse


class GitHubDownloader:
    """
    КЛАСС: GitHubDownloader - Загрузчик файлов из GitHub

    МЕТОДЫ:
        - download_from_repo() - Скачать файлы из репозитория
        - get_repo_contents() - Получить список файлов из репо
        - download_file() - Скачать один файл
        - get_stats() - Получить статистику работы
    """

    def __init__(self, download_path: Path, delay: float = 1.0, token: Optional[str] = None):
        """
        КОМАНДА: Инициализация загрузчика

        ЧТО ДЕЛАЕТ:
            1. Сохраняет путь для скачивания
            2. Настраивает задержку между запросами
            3. Инициализирует счетчики статистики
            4. Настраивает GitHub token если есть

        ПАРАМЕТРЫ:
            download_path - папка для сохранения файлов
            delay - задержка между запросами в секундах
            token - GitHub Personal Access Token (опционально)

        ЗАЧЕМ token:
            - Увеличивает лимит API с 60 до 5000 запросов/час
            - Дает доступ к приватным репозиториям
            - Получить можно на: https://github.com/settings/tokens
        """
        # НАСТРОЙКА: Сохраняем параметры
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.token = token
        self.logger = logging.getLogger(__name__)

        # СТАТИСТИКА: Инициализируем счетчики
        self.stats = {
            'repos_processed': 0,      # Обработано репозиториев
            'files_found': 0,          # Найдено файлов
            'files_downloaded': 0,     # Скачано файлов
            'files_existed': 0,        # Уже существовало
            'total_size': 0,           # Общий размер в байтах
        }

        # API: Базовый URL GitHub API
        self.api_base = 'https://api.github.com'

        # ЗАГОЛОВКИ: Настраиваем headers для API запросов
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',  # Версия API
            'User-Agent': 'AutoManuals-Downloader/1.0'   # Идентификация клиента
        }

        # АВТОРИЗАЦИЯ: Добавляем токен если есть
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
            self.logger.info("✅ GitHub токен установлен (лимит: 5000 req/hour)")
        else:
            self.logger.warning("⚠️ GitHub токен не установлен (лимит: 60 req/hour)")

    def _parse_repo_url(self, repo_url: str) -> Dict[str, str]:
        """
        КОМАНДА: Парсит URL репозитория

        ЧТО ДЕЛАЕТ:
            Извлекает owner и repo_name из URL

        ПАРАМЕТРЫ:
            repo_url - URL вида https://github.com/owner/repo

        ВОЗВРАЩАЕТ:
            Dict с ключами 'owner' и 'repo'

        ПРИМЕР:
            'https://github.com/torvalds/linux' ->
            {'owner': 'torvalds', 'repo': 'linux'}
        """
        # ПАРСИНГ: Разбираем URL
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')

        # ПРОВЕРКА: Должно быть минимум 2 части (owner/repo)
        if len(path_parts) < 2:
            raise ValueError(f"Некорректный URL репозитория: {repo_url}")

        return {
            'owner': path_parts[0],
            'repo': path_parts[1]
        }

    async def get_repo_contents(
        self,
        owner: str,
        repo: str,
        path: str = '',
        extensions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        КОМАНДА: Получает список файлов из репозитория через API

        ЧТО ДЕЛАЕТ:
            1. Делает GET запрос к GitHub API
            2. Получает список файлов и папок
            3. Рекурсивно обходит подпапки
            4. Фильтрует по расширениям
            5. Возвращает список файлов

        ПАРАМЕТРЫ:
            owner - владелец репозитория
            repo - название репозитория
            path - путь внутри репо ('' для корня)
            extensions - список разрешенных расширений

        ВОЗВРАЩАЕТ:
            List[Dict] - список файлов с их параметрами

        API ENDPOINT:
            GET /repos/{owner}/{repo}/contents/{path}
        """
        files = []

        # URL: Формируем URL для API запроса
        url = f'{self.api_base}/repos/{owner}/{repo}/contents/{path}'

        try:
            # HTTP: Делаем асинхронный GET запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    # ПРОВЕРКА: Успешен ли запрос
                    if response.status != 200:
                        self.logger.error(f"❌ GitHub API ошибка: {response.status}")
                        return files

                    # ПАРСИНГ: Получаем JSON ответ
                    contents = await response.json()

                    # ОБХОД: Проходим по всем элементам
                    for item in contents:
                        # ФАЙЛ: Если это файл - проверяем расширение
                        if item['type'] == 'file':
                            file_path = item['path']
                            file_ext = Path(file_path).suffix.lower()

                            # ФИЛЬТР: Проверяем расширение
                            if not extensions or file_ext in extensions:
                                files.append({
                                    'name': item['name'],
                                    'path': item['path'],
                                    'url': item['download_url'],  # Прямая ссылка на скачивание
                                    'size': item['size'],
                                })
                                self.stats['files_found'] += 1

                        # ПАПКА: Если это папка - рекурсивно обходим
                        elif item['type'] == 'dir':
                            # РЕКУРСИЯ: Получаем файлы из подпапки
                            subfiles = await self.get_repo_contents(
                                owner, repo, item['path'], extensions
                            )
                            files.extend(subfiles)

                            # ЗАДЕРЖКА: Пауза чтобы не превысить rate limit
                            await asyncio.sleep(self.delay)

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения файлов: {e}")

        return files

    async def download_file(self, url: str, filepath: Path) -> bool:
        """
        КОМАНДА: Скачивает один файл

        ЧТО ДЕЛАЕТ:
            1. Проверяет существует ли файл
            2. Скачивает файл через HTTP
            3. Сохраняет на диск асинхронно
            4. Обновляет статистику

        ПАРАМЕТРЫ:
            url - URL файла для скачивания
            filepath - путь для сохранения

        ВОЗВРАЩАЕТ:
            bool - True если успешно, False если ошибка

        ОСОБЕННОСТИ:
            - Асинхронное чтение и запись
            - Проверка на существование
            - Обработка ошибок
        """
        try:
            # ПРОВЕРКА: Файл уже существует?
            if filepath.exists():
                self.logger.debug(f"⏭️ Файл существует: {filepath.name}")
                self.stats['files_existed'] += 1
                return False

            # СОЗДАНИЕ: Создаем папки если нужно
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # HTTP: Скачиваем файл
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.logger.error(f"❌ Ошибка скачивания: {response.status}")
                        return False

                    # СОХРАНЕНИЕ: Записываем файл асинхронно
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(await response.read())

            # СТАТИСТИКА: Обновляем счетчики
            file_size = filepath.stat().st_size
            self.stats['files_downloaded'] += 1
            self.stats['total_size'] += file_size

            self.logger.info(f"✅ Скачано: {filepath.name} ({self._format_size(file_size)})")
            return True

        except Exception as e:
            self.logger.error(f"❌ Ошибка скачивания {filepath.name}: {e}")
            return False

    async def download_from_repo(
        self,
        repo_url: str,
        repo_path: str = '',
        allowed_extensions: Optional[List[str]] = None,
        keywords_include: Optional[List[str]] = None,
        keywords_exclude: Optional[List[str]] = None,
    ) -> List[Path]:
        """
        КОМАНДА: Главная функция - скачивает файлы из репозитория

        ЧТО ДЕЛАЕТ:
            1. Парсит URL репозитория
            2. Получает список файлов через API
            3. Фильтрует по ключевым словам
            4. Скачивает каждый файл
            5. Возвращает список путей

        ПАРАМЕТРЫ:
            repo_url - URL репозитория
            repo_path - путь внутри репо
            allowed_extensions - разрешенные расширения
            keywords_include - ключевые слова для включения
            keywords_exclude - ключевые слова для исключения

        ВОЗВРАЩАЕТ:
            List[Path] - список путей к скачанным файлам

        ИСПОЛЬЗОВАНИЕ:
            downloader = GitHubDownloader(Path('./downloads'))
            files = await downloader.download_from_repo(
                'https://github.com/user/repo',
                allowed_extensions=['.pdf', '.docx']
            )
        """
        downloaded_files = []

        try:
            # ПАРСИНГ: Извлекаем owner и repo из URL
            repo_info = self._parse_repo_url(repo_url)
            owner = repo_info['owner']
            repo = repo_info['repo']

            self.logger.info(f"🔍 Сканирование репозитория: {owner}/{repo}")

            # API: Получаем список файлов
            files = await self.get_repo_contents(
                owner, repo, repo_path, allowed_extensions
            )

            self.logger.info(f"📊 Найдено файлов: {len(files)}")

            # ФИЛЬТРАЦИЯ: Применяем фильтры по ключевым словам
            if keywords_include or keywords_exclude:
                files = self._filter_files(files, keywords_include, keywords_exclude)
                self.logger.info(f"📊 После фильтрации: {len(files)}")

            # СКАЧИВАНИЕ: Скачиваем каждый файл
            for file_info in files:
                # ПУТЬ: Формируем путь для сохранения
                save_path = self.download_path / f"{owner}_{repo}" / file_info['path']

                # СКАЧИВАНИЕ: Загружаем файл
                if await self.download_file(file_info['url'], save_path):
                    downloaded_files.append(save_path)

                # ЗАДЕРЖКА: Пауза между запросами
                await asyncio.sleep(self.delay)

            # СТАТИСТИКА: Обновляем счетчик репозиториев
            self.stats['repos_processed'] += 1

        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки репозитория: {e}")

        return downloaded_files

    def _filter_files(
        self,
        files: List[Dict],
        keywords_include: Optional[List[str]],
        keywords_exclude: Optional[List[str]]
    ) -> List[Dict]:
        """
        КОМАНДА: Фильтрует файлы по ключевым словам

        ЧТО ДЕЛАЕТ:
            1. Проверяет каждый файл на наличие include слов
            2. Проверяет отсутствие exclude слов
            3. Возвращает отфильтрованный список

        ПАРАМЕТРЫ:
            files - список файлов
            keywords_include - слова для включения
            keywords_exclude - слова для исключения

        ВОЗВРАЩАЕТ:
            List[Dict] - отфильтрованный список
        """
        filtered = []

        for file_info in files:
            filename_lower = file_info['name'].lower()

            # ПРОВЕРКА ВКЛЮЧЕНИЯ: Должно содержать хотя бы одно слово из include
            if keywords_include:
                if not any(kw.lower() in filename_lower for kw in keywords_include):
                    continue

            # ПРОВЕРКА ИСКЛЮЧЕНИЯ: Не должно содержать слов из exclude
            if keywords_exclude:
                if any(kw.lower() in filename_lower for kw in keywords_exclude):
                    continue

            # ДОБАВЛЕНИЕ: Файл прошел фильтры
            filtered.append(file_info)

        return filtered

    def _format_size(self, size_bytes: int) -> str:
        """
        КОМАНДА: Форматирует размер в человекочитаемый вид

        ПРИМЕР:
            1024 -> "1.0 KB"
            1048576 -> "1.0 MB"
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def get_stats(self) -> Dict:
        """
        КОМАНДА: Возвращает статистику работы

        ВОЗВРАЩАЕТ:
            Dict со статистикой:
                - repos_processed: обработано репозиториев
                - files_found: найдено файлов
                - files_downloaded: скачано файлов
                - files_existed: уже существовало
                - total_size: общий размер
                - total_size_formatted: размер в читаемом виде
        """
        return {
            **self.stats,
            'total_size_formatted': self._format_size(self.stats['total_size'])
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """
    ПРИМЕР: Как использовать GitHubDownloader

    ЗАПУСК:
        python github_downloader.py
    """
    # НАСТРОЙКА ЛОГИРОВАНИЯ
    logging.basicConfig(level=logging.INFO)

    # СОЗДАНИЕ ЗАГРУЗЧИКА
    downloader = GitHubDownloader(
        download_path=Path('./downloads/github'),
        delay=1.0,
        # token='ghp_your_token_here'  # Опционально
    )

    # СКАЧИВАНИЕ ИЗ РЕПОЗИТОРИЯ
    files = await downloader.download_from_repo(
        repo_url='https://github.com/topics/car-manual',
        allowed_extensions=['.pdf', '.doc', '.docx'],
        keywords_include=['manual', 'guide', 'instruction'],
    )

    # СТАТИСТИКА
    stats = downloader.get_stats()
    print(f"\n📊 Статистика:")
    print(f"   Репозиториев: {stats['repos_processed']}")
    print(f"   Файлов найдено: {stats['files_found']}")
    print(f"   Файлов скачано: {stats['files_downloaded']}")
    print(f"   Общий размер: {stats['total_size_formatted']}")


if __name__ == '__main__':
    asyncio.run(main())
