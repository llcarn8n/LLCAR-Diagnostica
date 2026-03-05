#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    АВТОМАТИЧЕСКОЕ СКАЧИВАНИЕ АВТОМАНУАЛОВ
                              Главный скрипт
═══════════════════════════════════════════════════════════════════════════════

ОПИСАНИЕ:
    Программа для автоматического скачивания автомобильных мануалов из различных
    источников: Telegram-каналы, веб-сайты, GitHub репозитории и торрент-трекеры.

ОСНОВНЫЕ ФУНКЦИИ:
    - Скачивание файлов из Telegram-каналов
    - Парсинг и скачивание с веб-сайтов
    - Скачивание репозиториев с GitHub
    - Работа с торрент-трекерами (RuTracker)
    - Автоматическая сортировка файлов по маркам автомобилей
    - Фильтрация по расширениям и ключевым словам

АВТОР: Улучшенная версия
ДАТА: 2026-01-24
"""

import os
import sys
import asyncio
import logging
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 1: ПОДАВЛЕНИЕ НЕКРИТИЧНЫХ ПРЕДУПРЕЖДЕНИЙ
# ═══════════════════════════════════════════════════════════════════════════════
# Этот блок отключает вывод предупреждений, которые не влияют на работу программы
# но могут загромождать консоль

# Подавляем предупреждения о SSL сертификатах (они не критичны для работы)
warnings.filterwarnings('ignore', message='.*SSL.*')

# Подавляем предупреждения о библиотеке cryptg (необязательная для Telethon)
warnings.filterwarnings('ignore', message='.*cryptg.*')

# Устанавливаем уровень логирования для Telethon чтобы не показывать INFO сообщения
logging.getLogger('telethon').setLevel(logging.WARNING)

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 2: АВТОМАТИЧЕСКАЯ УСТАНОВКА КРИТИЧНЫХ ЗАВИСИМОСТЕЙ
# ═══════════════════════════════════════════════════════════════════════════════
# Эта функция проверяет наличие необходимых библиотек и устанавливает их при
# отсутствии

def ensure_dependencies():
    """
    КОМАНДА: Проверяет и устанавливает критичные зависимости

    ЧТО ДЕЛАЕТ:
        1. Проверяет наличие обязательных библиотек (telethon, aiohttp, bs4, aiofiles)
        2. Если какие-то библиотеки отсутствуют, устанавливает их через pip
        3. Пытается установить необязательную библиотеку cryptg для ускорения

    ЗАЧЕМ:
        Автоматизирует процесс установки зависимостей, чтобы пользователь
        не делал это вручную
    """
    # Словарь обязательных пакетов: имя_модуля -> имя_пакета_для_pip
    required_packages = {
        'telethon': 'telethon',          # Для работы с Telegram API
        'aiohttp': 'aiohttp',            # Для асинхронных HTTP-запросов
        'bs4': 'beautifulsoup4',         # Для парсинга HTML страниц
        'aiofiles': 'aiofiles',          # Для асинхронной работы с файлами
    }

    # Необязательные пакеты, улучшающие производительность
    optional_packages = {
        'cryptg': 'cryptg',  # Для ускорения шифрования в Telegram
    }

    # Список отсутствующих пакетов
    missing = []

    # Проверяем каждый обязательный пакет
    for module, package in required_packages.items():
        try:
            # Пробуем импортировать модуль
            __import__(module)
        except ImportError:
            # Если не получилось - добавляем в список для установки
            missing.append(package)

    # Если есть отсутствующие пакеты - устанавливаем их
    if missing:
        print(f"⚠️ Устанавливаем недостающие пакеты: {', '.join(missing)}")
        import subprocess
        # Запускаем pip install для установки пакетов
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            *missing, '--quiet', '--disable-pip-version-check'
        ])
        print("✅ Пакеты установлены!")

    # Пробуем установить cryptg (не критично если не получится)
    try:
        import cryptg
    except ImportError:
        try:
            import subprocess
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                'cryptg', '--quiet', '--disable-pip-version-check'
            ], stderr=subprocess.DEVNULL)  # Подавляем вывод ошибок
        except:
            pass  # Не критично, продолжаем без cryptg

# ВЫЗОВ: Проверяем зависимости при импорте модуля
ensure_dependencies()

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 3: ИСПРАВЛЕНИЕ ДЛЯ WINDOWS
# ═══════════════════════════════════════════════════════════════════════════════
# Windows требует специальной настройки asyncio для корректной работы

if sys.platform == 'win32':
    # КОМАНДА: Используем SelectorEventLoop для совместимости на Windows
    # ЗАЧЕМ: Стандартный ProactorEventLoop может вызывать проблемы с некоторыми библиотеками
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # КОМАНДА: Исправление для SSL на Windows
    # ЗАЧЕМ: Позволяет обойти проблемы с SSL сертификатами на Windows
    import ssl
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 4: ИМПОРТ НАСТРОЕК ИЗ КОНФИГУРАЦИОННОГО ФАЙЛА
# ═══════════════════════════════════════════════════════════════════════════════
# Импортируем все настройки из файла config.py

from config import (
    BASE_DOWNLOAD_PATH,          # Папка для сохранения файлов
    TELEGRAM_API_ID,             # API ID для Telegram
    TELEGRAM_API_HASH,           # API Hash для Telegram
    TELEGRAM_PHONE,              # Номер телефона для Telegram
    TELEGRAM_CHANNELS,           # Список каналов для скачивания
    TELEGRAM_MESSAGE_LIMIT,      # Лимит сообщений на канал
    WEB_SOURCES,                 # Словарь веб-источников
    GITHUB_SOURCES,              # НОВОЕ: Список GitHub репозиториев
    ALLOWED_EXTENSIONS,          # Разрешенные расширения файлов
    KEYWORDS_INCLUDE,            # Ключевые слова для включения
    KEYWORDS_EXCLUDE,            # Ключевые слова для исключения
    MAX_FILE_SIZE_MB,            # Максимальный размер файла
    REQUEST_DELAY,               # Задержка между запросами
    LOG_LEVEL,                   # Уровень логирования
    TORRENT_ENABLED,             # Включены ли торренты
    RUTRACKER_ENABLED,           # Включен ли RuTracker
    RUTRACKER_USERNAME,          # Логин RuTracker
    RUTRACKER_PASSWORD,          # Пароль RuTracker
    RUTRACKER_SEARCH_QUERIES,    # Поисковые запросы для RuTracker
    RUTRACKER_MIN_SEEDS,         # Минимальное количество сидов
)


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 5: НАСТРОЙКА СИСТЕМЫ ЛОГИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════════════════════

def setup_logging() -> logging.Logger:
    """
    КОМАНДА: Настраивает систему логирования для программы

    ЧТО ДЕЛАЕТ:
        1. Создает папку ./logs если её нет
        2. Настраивает формат вывода логов (дата, уровень, сообщение)
        3. Создает два обработчика: вывод в файл и вывод в консоль
        4. Возвращает настроенный объект logger

    ЗАЧЕМ:
        Позволяет отслеживать работу программы и находить ошибки
        Все события сохраняются в файл с датой и временем

    ВОЗВРАЩАЕТ:
        logging.Logger - настроенный логгер для использования в программе
    """
    # Создаем папку для логов
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True)

    # Формат вывода логов: время - уровень - сообщение
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),  # Уровень из конфига
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Обработчик 1: Запись в файл с уникальным именем
            logging.FileHandler(
                log_dir / f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
                encoding='utf-8'
            ),
            # Обработчик 2: Вывод в консоль
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 6: СКАЧИВАНИЕ ИЗ TELEGRAM
# ═══════════════════════════════════════════════════════════════════════════════

async def download_from_telegram(organizer, logger) -> Dict:
    """
    КОМАНДА: Скачивает файлы из Telegram-каналов

    ЧТО ДЕЛАЕТ:
        1. Проверяет настройки Telegram (API ID, Hash, Phone)
        2. Создает TelegramDownloader и подключается к API
        3. Для каждого канала из списка:
           - Скачивает файлы с учетом фильтров
           - Сортирует файлы по папкам через FileOrganizer
        4. Выводит статистику скачивания

    ПАРАМЕТРЫ:
        organizer - объект FileOrganizer для сортировки файлов
        logger - объект Logger для вывода информации

    ВОЗВРАЩАЕТ:
        Dict - словарь со статистикой:
            - channels_processed: количество обработанных каналов
            - files_downloaded: количество скачанных файлов
            - total_size: общий размер в байтах
            - errors: количество ошибок
    """
    # Инициализация статистики
    stats = {
        'channels_processed': 0,
        'files_downloaded': 0,
        'total_size': 0,
        'errors': 0,
    }

    # ПРОВЕРКА: Настроен ли Telegram
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH or not TELEGRAM_PHONE:
        logger.warning("⚠️ Telegram не настроен. Пропускаем.")
        logger.info("   Для настройки укажите API_ID, API_HASH и PHONE в config.py")
        return stats

    # Вывод заголовка раздела
    logger.info("")
    logger.info("=" * 60)
    logger.info("📱 СКАЧИВАНИЕ ИЗ TELEGRAM")
    logger.info("=" * 60)

    try:
        # ИМПОРТ: Загружаем модуль для работы с Telegram
        from downloaders.telegram_downloader import TelegramDownloader

        # СОЗДАНИЕ: Инициализируем загрузчик с параметрами
        downloader = TelegramDownloader(
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH,
            phone=TELEGRAM_PHONE,
            download_path=BASE_DOWNLOAD_PATH / '_telegram_raw'  # Временная папка
        )

        # ПОДКЛЮЧЕНИЕ: Авторизуемся в Telegram
        if not await downloader.connect():
            logger.error("❌ Не удалось подключиться к Telegram")
            return stats

        try:
            # ЦИКЛ: Обрабатываем каждый канал из списка
            for channel in TELEGRAM_CHANNELS:
                logger.info(f"\n📢 Канал: @{channel}")

                try:
                    # СКАЧИВАНИЕ: Получаем файлы из канала с фильтрами
                    files = await downloader.download_from_channel(
                        channel_username=channel,
                        allowed_extensions=ALLOWED_EXTENSIONS,      # Какие форматы
                        max_size_mb=MAX_FILE_SIZE_MB,              # Макс. размер
                        message_limit=TELEGRAM_MESSAGE_LIMIT,       # Сколько сообщений
                        keywords_include=KEYWORDS_INCLUDE,          # Ключевые слова
                        keywords_exclude=KEYWORDS_EXCLUDE,
                    )

                    # СТАТИСТИКА: Обновляем счетчики
                    stats['channels_processed'] += 1
                    stats['files_downloaded'] += len(files)

                    # СОРТИРОВКА: Раскладываем скачанные файлы по папкам
                    for file_info in files:
                        try:
                            stats['total_size'] += file_info.get('size', 0)
                            # Вызываем органайзер для определения правильной папки
                            organizer.organize_file(
                                source_path=file_info['filepath'],
                                filename=file_info['filename'],
                                description=file_info.get('caption', '')
                            )
                        except Exception as e:
                            logger.error(f"Ошибка сортировки {file_info['filename']}: {e}")

                except Exception as e:
                    logger.error(f"❌ Ошибка канала {channel}: {e}")
                    stats['errors'] += 1

            # ВЫВОД СТАТИСТИКИ: Показываем результаты работы
            tg_stats = downloader.get_stats()
            logger.info(f"\n📊 Статистика Telegram:")
            logger.info(f"   Сообщений просмотрено: {tg_stats['messages_processed']}")
            logger.info(f"   Файлов найдено: {tg_stats['files_found']}")
            logger.info(f"   Файлов скачано: {tg_stats['files_downloaded']}")
            logger.info(f"   Уже существовало: {tg_stats['files_existed']}")
            logger.info(f"   Общий размер: {tg_stats['total_size_formatted']}")

        finally:
            # ОТКЛЮЧЕНИЕ: Всегда закрываем соединение
            await downloader.disconnect()

    except ImportError as e:
        logger.error(f"❌ Не установлен модуль: {e}")
        logger.info("   Выполните: pip install telethon")
    except Exception as e:
        logger.error(f"❌ Ошибка Telegram: {e}")
        stats['errors'] += 1

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 7: СКАЧИВАНИЕ С ВЕБ-САЙТОВ
# ═══════════════════════════════════════════════════════════════════════════════

async def download_from_web(organizer, logger) -> Dict:
    """
    КОМАНДА: Скачивает файлы с веб-сайтов

    ЧТО ДЕЛАЕТ:
        1. Создает WebDownloader для парсинга веб-страниц
        2. Для каждого включенного источника из WEB_SOURCES:
           - Парсит страницу и ищет ссылки на файлы
           - Скачивает файлы с учетом фильтров
           - Сортирует файлы по папкам
        3. Выводит статистику

    ПАРАМЕТРЫ:
        organizer - объект FileOrganizer для сортировки
        logger - объект Logger для логирования

    ВОЗВРАЩАЕТ:
        Dict - статистика скачивания

    ПРИНЦИП РАБОТЫ ПАРСИНГА:
        - Загружает HTML страницу
        - Ищет все ссылки (<a href="...">) на файлы с нужными расширениями
        - Фильтрует по ключевым словам
        - Скачивает файлы асинхронно
    """
    # Инициализация статистики
    stats = {
        'sites_processed': 0,
        'files_downloaded': 0,
        'total_size': 0,
        'errors': 0,
    }

    logger.info("")
    logger.info("=" * 60)
    logger.info("🌐 СКАЧИВАНИЕ С ВЕБ-САЙТОВ")
    logger.info("=" * 60)

    try:
        # ИМПОРТ: Загружаем модуль веб-загрузчика
        from downloaders.web_downloader import WebDownloader

        # СОЗДАНИЕ: Инициализируем загрузчик
        downloader = WebDownloader(
            download_path=BASE_DOWNLOAD_PATH / '_web_raw',  # Временная папка
            delay=REQUEST_DELAY,  # Пауза между запросами
        )

        # ЦИКЛ: Обрабатываем каждый источник
        for source_name, source_config in WEB_SOURCES.items():
            # ПРОВЕРКА: Включен ли этот источник
            if not source_config.get('enabled', False):
                continue

            logger.info(f"\n🔗 Источник: {source_name}")

            try:
                base_url = source_config.get('base_url')
                if base_url:
                    # ПАРСИНГ И СКАЧИВАНИЕ: Обрабатываем страницу
                    files = await downloader.download_from_page(
                        url=base_url,
                        file_extensions=ALLOWED_EXTENSIONS,
                        subfolder=source_name,
                        keywords_include=KEYWORDS_INCLUDE,
                        keywords_exclude=KEYWORDS_EXCLUDE,
                    )

                    # ОБНОВЛЕНИЕ СТАТИСТИКИ
                    stats['sites_processed'] += 1
                    stats['files_downloaded'] += len(files)

                    # СОРТИРОВКА: Раскладываем файлы по папкам
                    for filepath in files:
                        try:
                            if filepath and filepath.exists():
                                stats['total_size'] += filepath.stat().st_size
                                organizer.organize_file(
                                    source_path=filepath,
                                    filename=filepath.name,
                                )
                        except Exception as e:
                            logger.debug(f"Ошибка сортировки: {e}")

            except Exception as e:
                logger.error(f"❌ Ошибка источника {source_name}: {e}")
                stats['errors'] += 1

        # ВЫВОД СТАТИСТИКИ
        web_stats = downloader.get_stats()
        logger.info(f"\n📊 Статистика веб-скачивания:")
        logger.info(f"   Страниц обработано: {web_stats['pages_processed']}")
        logger.info(f"   Ссылок найдено: {web_stats['links_found']}")
        logger.info(f"   Файлов скачано: {web_stats['files_downloaded']}")
        logger.info(f"   Общий размер: {web_stats['total_size_formatted']}")

    except ImportError as e:
        logger.error(f"❌ Не установлен модуль: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка веб-скачивания: {e}")
        stats['errors'] += 1

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 8: СКАЧИВАНИЕ С GITHUB (НОВОЕ!)
# ═══════════════════════════════════════════════════════════════════════════════

async def download_from_github(organizer, logger) -> Dict:
    """
    КОМАНДА: Скачивает файлы из GitHub репозиториев

    ЧТО ДЕЛАЕТ:
        1. Для каждого репозитория из GITHUB_SOURCES:
           - Получает список файлов через GitHub API
           - Фильтрует файлы по расширению и ключевым словам
           - Скачивает подходящие файлы
           - Сортирует по папкам
        2. Выводит статистику

    ПАРАМЕТРЫ:
        organizer - объект FileOrganizer
        logger - объект Logger

    ВОЗВРАЩАЕТ:
        Dict - статистика скачивания

    ПРЕИМУЩЕСТВА GITHUB:
        - Много открытых репозиториев с документацией
        - Официальные мануалы от производителей
        - Структурированное хранение файлов
        - API для удобного доступа

    ОСОБЕННОСТИ:
        - Использует GitHub API v3
        - Не требует авторизации для публичных репозиториев
        - Может скачивать отдельные файлы без клонирования всего репо
    """
    # Инициализация статистики
    stats = {
        'repos_processed': 0,
        'files_downloaded': 0,
        'total_size': 0,
        'errors': 0,
    }

    # ПРОВЕРКА: Есть ли настроенные репозитории
    if not GITHUB_SOURCES:
        logger.info("⚠️ GitHub репозитории не настроены. Пропускаем.")
        return stats

    logger.info("")
    logger.info("=" * 60)
    logger.info("🐙 СКАЧИВАНИЕ С GITHUB")
    logger.info("=" * 60)

    try:
        # ИМПОРТ: Загружаем модуль GitHub-загрузчика
        from downloaders.github_downloader import GitHubDownloader

        # СОЗДАНИЕ: Инициализируем загрузчик
        downloader = GitHubDownloader(
            download_path=BASE_DOWNLOAD_PATH / '_github_raw',
            delay=REQUEST_DELAY,
        )

        # ЦИКЛ: Обрабатываем каждый репозиторий
        for repo_config in GITHUB_SOURCES:
            # ПРОВЕРКА: Включен ли репозиторий
            if not repo_config.get('enabled', True):
                continue

            repo_url = repo_config.get('url')
            repo_path = repo_config.get('path', '')  # Путь внутри репо

            logger.info(f"\n📦 Репозиторий: {repo_url}")
            if repo_path:
                logger.info(f"   Путь: {repo_path}")

            try:
                # СКАЧИВАНИЕ: Получаем файлы из репозитория
                files = await downloader.download_from_repo(
                    repo_url=repo_url,
                    repo_path=repo_path,
                    allowed_extensions=ALLOWED_EXTENSIONS,
                    keywords_include=KEYWORDS_INCLUDE,
                    keywords_exclude=KEYWORDS_EXCLUDE,
                )

                # ОБНОВЛЕНИЕ СТАТИСТИКИ
                stats['repos_processed'] += 1
                stats['files_downloaded'] += len(files)

                # СОРТИРОВКА: Раскладываем файлы по папкам
                for filepath in files:
                    try:
                        if filepath and filepath.exists():
                            stats['total_size'] += filepath.stat().st_size
                            organizer.organize_file(
                                source_path=filepath,
                                filename=filepath.name,
                            )
                    except Exception as e:
                        logger.debug(f"Ошибка сортировки: {e}")

            except Exception as e:
                logger.error(f"❌ Ошибка репозитория {repo_url}: {e}")
                stats['errors'] += 1

        # ВЫВОД СТАТИСТИКИ
        gh_stats = downloader.get_stats()
        logger.info(f"\n📊 Статистика GitHub:")
        logger.info(f"   Репозиториев обработано: {gh_stats['repos_processed']}")
        logger.info(f"   Файлов найдено: {gh_stats['files_found']}")
        logger.info(f"   Файлов скачано: {gh_stats['files_downloaded']}")
        logger.info(f"   Общий размер: {gh_stats['total_size_formatted']}")

    except ImportError as e:
        logger.error(f"❌ Не установлен модуль: {e}")
        logger.info("   GitHub downloader не найден")
    except Exception as e:
        logger.error(f"❌ Ошибка GitHub: {e}")
        stats['errors'] += 1

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 9: СКАЧИВАНИЕ ТОРРЕНТОВ
# ═══════════════════════════════════════════════════════════════════════════════

async def download_from_torrents(organizer, logger) -> Dict:
    """
    КОМАНДА: Скачивает .torrent файлы с торрент-трекеров

    ЧТО ДЕЛАЕТ:
        1. Авторизуется на RuTracker
        2. Для каждого поискового запроса:
           - Ищет раздачи
           - Фильтрует по количеству сидов
           - Скачивает .torrent файлы
        3. Выводит статистику

    ВАЖНО:
        Программа скачивает только .torrent файлы!
        Для скачивания содержимого нужен торрент-клиент (qBittorrent, uTorrent)

    ПАРАМЕТРЫ:
        organizer - объект FileOrganizer (не используется для торрентов)
        logger - объект Logger

    ВОЗВРАЩАЕТ:
        Dict - статистика

    ПРИНЦИП РАБОТЫ:
        1. Авторизация на трекере (cookies)
        2. POST запрос с поисковым запросом
        3. Парсинг результатов поиска (BeautifulSoup)
        4. Скачивание .torrent файлов по ID раздачи
    """
    # Инициализация статистики
    stats = {
        'torrents_found': 0,
        'torrents_downloaded': 0,
        'errors': 0,
    }

    # ПРОВЕРКА: Включены ли торренты
    if not TORRENT_ENABLED:
        return stats

    logger.info("")
    logger.info("=" * 60)
    logger.info("🧲 СКАЧИВАНИЕ ТОРРЕНТОВ")
    logger.info("=" * 60)

    # ПРОВЕРКА: Настроен ли RuTracker
    if not RUTRACKER_ENABLED or not RUTRACKER_USERNAME or not RUTRACKER_PASSWORD:
        logger.warning("⚠️ RuTracker не настроен. Пропускаем.")
        return stats

    try:
        # ИМПОРТ: Загружаем модуль торрент-загрузчика
        from downloaders.torrent_downloader import RuTrackerDownloader

        # КОНТЕКСТНЫЙ МЕНЕДЖЕР: Автоматически закрывает соединение
        async with RuTrackerDownloader(
            username=RUTRACKER_USERNAME,
            password=RUTRACKER_PASSWORD,
            download_path=BASE_DOWNLOAD_PATH / '_torrents'
        ) as tracker:

            # АВТОРИЗАЦИЯ: Логинимся на трекере
            if not await tracker.login():
                logger.error("❌ Не удалось авторизоваться на RuTracker")
                return stats

            # ЦИКЛ: Поиск по каждому запросу
            for query in RUTRACKER_SEARCH_QUERIES:
                logger.info(f"\n🔍 Поиск: {query}")

                # ПОИСК: Ищем раздачи по запросу
                results = await tracker.search(
                    query=query,
                    max_results=10,  # Ограничиваем количество результатов
                    min_seeds=RUTRACKER_MIN_SEEDS,  # Минимум сидов
                )

                stats['torrents_found'] += len(results)

                # СКАЧИВАНИЕ: Берем топ-5 раздач
                for torrent in results[:5]:
                    logger.info(f"   📥 {torrent.title[:60]}...")

                    # Скачиваем .torrent файл
                    torrent_file = await tracker.download_torrent(torrent)
                    if torrent_file:
                        stats['torrents_downloaded'] += 1

                # ПАУЗА: Между запросами чтобы не перегружать сервер
                await asyncio.sleep(2)

        # ВЫВОД СТАТИСТИКИ
        logger.info(f"\n📊 Статистика торрентов:")
        logger.info(f"   Найдено раздач: {stats['torrents_found']}")
        logger.info(f"   Скачано .torrent файлов: {stats['torrents_downloaded']}")
        logger.info(f"\n⚠️ Для загрузки содержимого откройте .torrent файлы в qBittorrent")

    except ImportError as e:
        logger.error(f"❌ Не установлен модуль: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка торрентов: {e}")
        stats['errors'] += 1

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 10: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

def format_size(size_bytes: int) -> str:
    """
    КОМАНДА: Форматирует размер файла в человекочитаемый вид

    ЧТО ДЕЛАЕТ:
        Преобразует байты в КБ, МБ, ГБ, ТБ с одним знаком после запятой

    ПАРАМЕТРЫ:
        size_bytes - размер в байтах

    ВОЗВРАЩАЕТ:
        str - отформатированная строка (например: "15.3 МБ")

    ПРИМЕР:
        format_size(1024) -> "1.0 КБ"
        format_size(1536) -> "1.5 КБ"
        format_size(1048576) -> "1.0 МБ"
    """
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} ПБ"


def print_banner():
    """
    КОМАНДА: Выводит красивый заголовок программы

    ЧТО ДЕЛАЕТ:
        Рисует ASCII-рамку с названием и иконками источников

    ЗАЧЕМ:
        Делает интерфейс программы более дружелюбным и понятным
    """
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "СКАЧИВАНИЕ АВТОМОБИЛЬНЫХ МАНУАЛОВ" + " " * 13 + "║")
    print("║" + " " * 58 + "║")
    print("║  📱 Telegram  🌐 Веб-сайты  🐙 GitHub  🧲 Торренты" + " " * 6 + "║")
    print("║  Автоматическая сортировка по маркам" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝")
    print()


def print_results(stats: Dict, folder_stats: Dict):
    """
    КОМАНДА: Выводит итоговую статистику работы программы

    ЧТО ДЕЛАЕТ:
        1. Показывает общее количество файлов в библиотеке
        2. Выводит статистику текущей сессии
        3. Показывает топ-5 марок автомобилей по количеству файлов

    ПАРАМЕТРЫ:
        stats - статистика текущей сессии
        folder_stats - статистика всей библиотеки

    ЗАЧЕМ:
        Дает пользователю полную картину результатов работы
    """
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 20 + "ИТОГОВАЯ СТАТИСТИКА" + " " * 19 + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Всего файлов в библиотеке: {folder_stats['total_files']:>26} ║")
    print(f"║  Общий размер: {format_size(folder_stats['total_size']):>39} ║")
    print("║" + " " * 58 + "║")
    print(f"║  Скачано за сессию: {stats['total_files']:>34} ║")
    print(f"║  Ошибок: {stats['total_errors']:>45} ║")
    print("╠" + "═" * 58 + "╣")
    print("║  ТОП-5 МАРОК ПО КОЛИЧЕСТВУ ФАЙЛОВ:" + " " * 21 + "║")

    # Сортируем марки по количеству файлов и берем топ-5
    sorted_brands = sorted(
        folder_stats['by_brand'].items(),
        key=lambda x: x[1]['files'],
        reverse=True
    )[:5]

    # Выводим каждую марку
    for brand, data in sorted_brands:
        if data['files'] > 0:
            size_str = format_size(data['size'])
            line = f"    {brand}: {data['files']} файлов ({size_str})"
            padding = 54 - len(line)
            print(f"║{line}{' ' * padding}║")

    print("╚" + "═" * 58 + "╝")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 11: ГЛАВНАЯ ФУНКЦИЯ ПРОГРАММЫ
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """
    КОМАНДА: Главная асинхронная функция - точка входа в программу

    ЧТО ДЕЛАЕТ:
        1. Настраивает логирование
        2. Выводит заголовок
        3. Создает FileOrganizer для сортировки файлов
        4. Последовательно запускает загрузчики:
           - Telegram
           - Веб-сайты
           - GitHub (НОВОЕ!)
           - Торренты
        5. Выводит итоговую статистику

    ПОРЯДОК ВЫПОЛНЕНИЯ:
        Каждый загрузчик работает независимо, если один падает с ошибкой,
        остальные продолжают работу

    ОБРАБОТКА ОШИБОК:
        try-except вокруг каждого загрузчика предотвращает полный крах программы
    """
    # 1. НАСТРОЙКА: Инициализируем логирование
    logger = setup_logging()

    # 2. ИНТЕРФЕЙС: Выводим красивый заголовок
    print_banner()

    # 3. ИНФОРМАЦИЯ: Выводим начальные данные
    logger.info(f"🚀 Начало работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📁 Папка для сохранения: {BASE_DOWNLOAD_PATH.absolute()}")

    # 4. ПОДГОТОВКА: Создаём организатор файлов (для структуры папок)
    try:
        from utils.file_organizer import FileOrganizer
        organizer = FileOrganizer(BASE_DOWNLOAD_PATH)
    except ImportError:
        logger.error("❌ Не найден модуль file_organizer")
        logger.info("   Проверьте наличие файла utils/file_organizer.py")
        return

    # 5. СТАТИСТИКА: Инициализируем общие счетчики
    total_stats = {
        'total_files': 0,      # Всего файлов скачано
        'total_errors': 0,     # Всего ошибок
    }

    # ═══════════════════════════════════════════════════════════════════════
    # ПОСЛЕДОВАТЕЛЬНЫЙ ЗАПУСК ВСЕХ ЗАГРУЗЧИКОВ
    # ═══════════════════════════════════════════════════════════════════════

    # 6. TELEGRAM: Скачиваем из Telegram-каналов
    try:
        logger.info("\n🔄 Запуск загрузчика Telegram...")
        tg_stats = await download_from_telegram(organizer, logger)
        total_stats['total_files'] += tg_stats.get('files_downloaded', 0)
        total_stats['total_errors'] += tg_stats.get('errors', 0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка Telegram: {e}")

    # 7. ВЕБ-САЙТЫ: Парсим и скачиваем с веб-источников
    try:
        logger.info("\n🔄 Запуск веб-загрузчика...")
        web_stats = await download_from_web(organizer, logger)
        total_stats['total_files'] += web_stats.get('files_downloaded', 0)
        total_stats['total_errors'] += web_stats.get('errors', 0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка веб-скачивания: {e}")

    # 8. GITHUB: Скачиваем из GitHub репозиториев (НОВОЕ!)
    try:
        logger.info("\n🔄 Запуск GitHub загрузчика...")
        github_stats = await download_from_github(organizer, logger)
        total_stats['total_files'] += github_stats.get('files_downloaded', 0)
        total_stats['total_errors'] += github_stats.get('errors', 0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка GitHub: {e}")

    # 9. ТОРРЕНТЫ: Скачиваем .torrent файлы
    try:
        logger.info("\n🔄 Запуск торрент-загрузчика...")
        torrent_stats = await download_from_torrents(organizer, logger)
        total_stats['total_files'] += torrent_stats.get('torrents_downloaded', 0)
        total_stats['total_errors'] += torrent_stats.get('errors', 0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка торрентов: {e}")

    # 10. РЕЗУЛЬТАТЫ: Получаем статистику всей библиотеки
    folder_stats = organizer.get_stats()

    # 11. ВЫВОД: Показываем итоговую статистику
    print_results(total_stats, folder_stats)

    # 12. ИНФОРМАЦИЯ: Путь к скачанным файлам
    print(f"📁 Файлы сохранены в: {BASE_DOWNLOAD_PATH.absolute()}")
    print()

    # 13. ЗАВЕРШЕНИЕ: Логируем окончание работы
    logger.info(f"✅ Завершено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 12: ТОЧКА ВХОДА В ПРОГРАММУ
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    """
    КОМАНДА: Точка входа при запуске скрипта

    ЧТО ПРОИСХОДИТ:
        1. Python проверяет: запущен ли файл напрямую (а не импортирован)
        2. Если да - запускает функцию main() в asyncio event loop
        3. asyncio.run() создает event loop, запускает main() и ждет завершения

    ЗАЧЕМ asyncio.run():
        Все наши функции асинхронные (async/await), для их работы нужен event loop
        asyncio.run() автоматически:
        - Создает новый event loop
        - Запускает главную корутину
        - Закрывает event loop после завершения

    КАК ЗАПУСТИТЬ:
        python main.py
    """
    asyncio.run(main())
