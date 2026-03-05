#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                АВТОМАТИЧЕСКОЕ СКАЧИВАНИЕ АВТОМАНУАЛОВ v2.1
          С ПРОВЕРКОЙ ЦЕЛОСТНОСТИ И ПОВТОРНЫМ СКАЧИВАНИЕМ
═══════════════════════════════════════════════════════════════════════════════

НОВЫЕ ВОЗМОЖНОСТИ В v2.1:
    ✅ Проверка целостности файлов при запуске
    ✅ Автоматическое повторное скачивание недокачанных файлов
    ✅ Обнаружение пропущенных файлов
    ✅ Повторная проверка каналов в конце сессии
    ✅ База данных для отслеживания состояния файлов
    ✅ Детальная статистика по каждому источнику

ОПИСАНИЕ:
    Программа для автоматического скачивания автомобильных мануалов из различных
    источников с контролем целостности и возобновлением скачивания.

ОСНОВНЫЕ ФУНКЦИИ:
    - Скачивание файлов из Telegram-каналов с проверкой целостности
    - Парсинг и скачивание с веб-сайтов
    - Скачивание репозиториев с GitHub
    - Работа с торрент-трекерами (RuTracker)
    - Автоматическая сортировка файлов по маркам автомобилей
    - Фильтрация по расширениям и ключевым словам
    - Отслеживание состояния всех файлов в SQLite базе
    - Повторная проверка источников для поиска новых файлов

АВТОР: Улучшенная версия v2.1
ДАТА: 2026-01-24
"""

import sys
import asyncio
import logging
import warnings
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 0: НАСТРОЙКА КОДИРОВКИ ДЛЯ WINDOWS КОНСОЛИ
# ═══════════════════════════════════════════════════════════════════════════════

# Исправляем проблему с эмодзи в Windows консоли
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 1: ПОДАВЛЕНИЕ НЕКРИТИЧНЫХ ПРЕДУПРЕЖДЕНИЙ
# ═══════════════════════════════════════════════════════════════════════════════

warnings.filterwarnings('ignore', message='.*SSL.*')
warnings.filterwarnings('ignore', message='.*cryptg.*')
logging.getLogger('telethon').setLevel(logging.WARNING)

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 2: АВТОМАТИЧЕСКАЯ УСТАНОВКА ЗАВИСИМОСТЕЙ
# ═══════════════════════════════════════════════════════════════════════════════


def ensure_dependencies():
    """Проверяет и устанавливает критичные зависимости + проверка скорости"""
    required_packages = {
        'telethon': 'telethon',
        'aiohttp': 'aiohttp',
        'bs4': 'beautifulsoup4',
        'aiofiles': 'aiofiles',
    }

    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"⚠️ Устанавливаем недостающие пакеты: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            *missing, '--quiet', '--disable-pip-version-check'
        ])
        print("✅ Пакеты установлены!")

    # ═══════════════════════════════════════════════════════════════════════
    # ПРОВЕРКА СКОРОСТИ: Ускорители криптографии для Telethon
    # ═══════════════════════════════════════════════════════════════════════
    has_cryptg = False
    has_pycrypto = False

    # Проверка 1: cryptg (С-расширение, максимальная скорость)
    try:
        import cryptg  # noqa: F401
        has_cryptg = True
        print("🚀 cryptg обнаружен - МАКСИМАЛЬНАЯ скорость (10-20x)!")
    except ImportError:
        pass

    # Проверка 2: pycryptodome (Python, средняя скорость)
    if not has_cryptg:
        try:
            from Crypto.Cipher import AES  # noqa: F401
            has_pycrypto = True
            print("⚡ pycryptodome обнаружен - средняя скорость (3-5x)")
        except ImportError:
            pass

    # КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ: Если нет ускорителей
    if not has_cryptg and not has_pycrypto:
        print("\n" + "!" * 70)
        print("⚠️  ВНИМАНИЕ: Скачивание будет ОЧЕНЬ МЕДЛЕННЫМ!")
        print("!" * 70)
        print("Причина: Отсутствуют библиотеки для ускорения криптографии")
        print("         Telethon работает на чистом Python (в 10-20 раз медленнее)")
        print("\n🔥 СРОЧНО УСТАНОВИТЕ ОДНУ ИЗ БИБЛИОТЕК:")
        print("  1. pip install pycryptodome     (работает везде, ускорение 3-5x)")
        print("  2. pip install cryptg           (требует компилятор, ускорение 10-20x)")
        print("\n💡 Для диагностики и автоматической установки запустите:")
        print("  python speed_fix.py")
        print("\n📊 Сравнение скорости:")
        print("  Без ускорения: 50-100 КБ/с   (текущее)")
        print("  С pycryptodome: 200-500 КБ/с")
        print("  С cryptg: 1-2 МБ/с")
        print("!" * 70 + "\n")

        # Предлагаем установить pycryptodome прямо сейчас
        try:
            response = input("❓ Установить pycryptodome прямо сейчас? (y/n): ").lower()
            if response == 'y':
                print("\n📦 Устанавливаем pycryptodome...")
                import subprocess
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', 'pycryptodome'
                ])
                print("✅ pycryptodome установлен! Перезапустите программу.")
                sys.exit(0)
            else:
                # Даём 5 секунд подумать
                print("\n⏳ Продолжаем с медленной скоростью...")
                import time
                for i in range(5, 0, -1):
                    print(f"   Запуск через {i} сек (Ctrl+C для отмены)...", end='\r')
                    time.sleep(1)
                print(" " * 60)  # Очищаем строку
        except (EOFError, KeyboardInterrupt):
            # В неинтерактивном режиме просто продолжаем
            import time
            time.sleep(2)

    elif not has_cryptg and has_pycrypto:
        print("💡 Для максимальной скорости установите cryptg:")
        print("   pip install cryptg")
        print("   (требуется компилятор C/C++)")


ensure_dependencies()


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 3: ИСПРАВЛЕНИЕ ДЛЯ WINDOWS
# ═══════════════════════════════════════════════════════════════════════════════

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    import ssl
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 4: ИМПОРТ НАСТРОЕК И МОДУЛЕЙ
# ═══════════════════════════════════════════════════════════════════════════════

from config import (  # noqa: E402

    BASE_DOWNLOAD_PATH,
    TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE,
    TELEGRAM_CHANNELS, TELEGRAM_MESSAGE_LIMIT,
    GITHUB_SOURCES,
    ALLOWED_EXTENSIONS,
    KEYWORDS_INCLUDE, KEYWORDS_EXCLUDE,
    MAX_FILE_SIZE_MB,
    LOG_LEVEL,
    TORRENT_ENABLED,
)

# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 5: НАСТРОЙКА ЛОГИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════════════════════


def setup_logging() -> logging.Logger:
    """Настраивает систему логирования"""
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True)

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(
                log_dir / f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 6: ПРОВЕРКА ЦЕЛОСТНОСТИ ФАЙЛОВ ПРИ ЗАПУСКЕ (НОВОЕ!)
# ═══════════════════════════════════════════════════════════════════════════════

async def check_file_integrity(file_tracker, logger) -> Dict:
    """
    КОМАНДА: Проверяет целостность всех скачанных файлов

    ЧТО ДЕЛАЕТ:
        1. Получает список всех файлов из базы
        2. Проверяет существование каждого файла на диске
        3. Сравнивает размер с ожидаемым
        4. Находит недокачанные и отсутствующие файлы
        5. Помечает их для повторного скачивания

    ВОЗВРАЩАЕТ:
        Dict - статистика проверки
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ ФАЙЛОВ")
    logger.info("=" * 60)

    stats = {
        'total_checked': 0,
        'complete': 0,
        'incomplete': 0,
        'missing': 0,
        'marked_for_redownload': 0,
    }

    # ПОЛУЧЕНИЕ: Список всех файлов которые должны быть скачаны
    tracker_stats = file_tracker.get_stats()
    stats['total_checked'] = tracker_stats['total']

    logger.info(f"📊 Всего файлов в базе: {stats['total_checked']}")

    if stats['total_checked'] == 0:
        logger.info("✅ База пуста, это первый запуск")
        return stats

    # ПРОВЕРКА: Находим недокачанные файлы
    incomplete = file_tracker.get_incomplete_files()
    stats['incomplete'] = len(incomplete)

    if incomplete:
        logger.warning(f"⚠️ Найдено недокачанных файлов: {stats['incomplete']}")

        for file_info in incomplete[:5]:  # Показываем первые 5
            reason_text = {
                'incomplete': 'неполный размер',
                'missing': 'отсутствует на диске',
                'pending': 'не скачивался'
            }.get(file_info['reason'], 'неизвестная причина')

            logger.info(f"   📄 {file_info['filename']} - {reason_text}")

            # ПОМЕТКА: Помечаем для повторного скачивания
            file_tracker.mark_for_redownload(file_info['id'])
            stats['marked_for_redownload'] += 1

        if len(incomplete) > 5:
            logger.info(f"   ... и еще {len(incomplete) - 5} файлов")

    # ПРОВЕРКА: Находим отсутствующие файлы
    missing = file_tracker.get_missing_files()
    stats['missing'] = len(missing)

    if missing:
        logger.warning(f"⚠️ Файлы исчезли с диска: {stats['missing']}")
        for file_info in missing[:3]:
            logger.info(f"   📄 {file_info['filename']}")

    # СТАТИСТИКА: Полные файлы
    stats['complete'] = tracker_stats['complete']
    logger.info(f"✅ Полных файлов: {stats['complete']}")

    # ИТОГО
    if stats['incomplete'] > 0 or stats['missing'] > 0:
        logger.info(f"🔄 Будет повторно скачано: {stats['marked_for_redownload']}")
    else:
        logger.info("✅ Все файлы в порядке!")

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 7: СКАЧИВАНИЕ ИЗ TELEGRAM С ОТСЛЕЖИВАНИЕМ (УЛУЧШЕНО!)
# ═══════════════════════════════════════════════════════════════════════════════

async def download_from_telegram(
    organizer,
    logger,
    file_tracker,
    recheck_mode: bool = False
) -> Dict:
    """
    КОМАНДА: Скачивает файлы из Telegram с отслеживанием состояния

    ЧТО УЛУЧШЕНО:
        - Проверка каждого файла в базе перед скачиванием
        - Пропуск уже скачанных полных файлов
        - Повторное скачивание недокачанных
        - Регистрация всех файлов в базе
        - Полное сканирование канала (без ограничений)

    ПАРАМЕТРЫ:
        organizer - объект FileOrganizer
        logger - логгер
        file_tracker - объект FileTracker
        recheck_mode - режим повторной проверки (полная синхронизация)

    ВАЖНО:
        В режиме recheck_mode сканируются ВСЕ сообщения в канале,
        чтобы не пропустить файлы из разорванных сессий
    """
    stats = {
        'channels_processed': 0,
        'files_found': 0,
        'files_downloaded': 0,
        'files_skipped': 0,
        'files_redownloaded': 0,
        'total_size': 0,
        'errors': 0,
    }

    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH or not TELEGRAM_PHONE:
        logger.warning("⚠️ Telegram не настроен. Пропускаем.")
        return stats

    # ЗАГОЛОВОК
    logger.info("")
    logger.info("=" * 60)
    if recheck_mode:
        logger.info("🔄 ПОВТОРНАЯ ПРОВЕРКА TELEGRAM КАНАЛОВ")
    else:
        logger.info("📱 СКАЧИВАНИЕ ИЗ TELEGRAM")
    logger.info("=" * 60)

    try:
        from downloaders.telegram_downloader import TelegramDownloader

        downloader = TelegramDownloader(
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH,
            phone=TELEGRAM_PHONE,
            download_path=BASE_DOWNLOAD_PATH / '_telegram_raw'
        )

        if not await downloader.connect():
            logger.error("❌ Не удалось подключиться к Telegram")
            return stats

        try:
            # ЦИКЛ: Обрабатываем каждый канал
            for channel in TELEGRAM_CHANNELS:
                logger.info(f"\n{'🔄' if recheck_mode else '📢'} Канал: @{channel}")

                try:
                    # СКАЧИВАНИЕ: TelegramDownloader уже имеет встроенную систему
                    # отслеживания дубликатов и проверку существующих файлов
                    # ВАЖНО: При recheck_mode сканируем ВСЕ сообщения (message_limit=None)
                    downloaded_files = await downloader.download_from_channel(
                        channel_username=channel,
                        allowed_extensions=ALLOWED_EXTENSIONS,
                        max_size_mb=MAX_FILE_SIZE_MB,
                        message_limit=TELEGRAM_MESSAGE_LIMIT if not recheck_mode else None,  # None = ВСЕ сообщения!
                        keywords_include=KEYWORDS_INCLUDE,
                        keywords_exclude=KEYWORDS_EXCLUDE,
                    )

                    # СТАТИСТИКА: Обновляем счетчики
                    channel_stats = downloader.get_stats()
                    stats['files_found'] += channel_stats['files_found']
                    stats['files_downloaded'] += len(downloaded_files)
                    stats['files_skipped'] += channel_stats['files_existed']

                    if recheck_mode and downloaded_files:
                        logger.info(f"   ✅ Новых файлов: {len(downloaded_files)}")
                        for df in downloaded_files:
                            logger.info(f"      {df['filename']}")

                    # ОРГАНИЗАЦИЯ: Раскладываем файлы по папкам
                    for downloaded_file in downloaded_files:
                        try:
                            # РЕГИСТРАЦИЯ в FileTracker
                            if file_tracker:
                                file_tracker.add_file(
                                    source='telegram',
                                    source_id=f'@{channel}',
                                    file_id=str(downloaded_file.get('filename', '')),
                                    filename=downloaded_file['filename'],
                                    expected_size=downloaded_file.get('size', 0),
                                    filepath=Path(downloaded_file['filepath']),
                                    metadata={
                                        'caption': downloaded_file.get('caption', ''),
                                        'date': str(downloaded_file.get('date', '')),
                                    }
                                )

                            # СОРТИРОВКА по маркам автомобилей
                            stats['total_size'] += downloaded_file.get('size', 0)

                            organizer.organize_file(
                                source_path=downloaded_file['filepath'],
                                filename=downloaded_file['filename'],
                                description=downloaded_file.get('caption', '')
                            )

                        except Exception as e:
                            logger.error(f"   ❌ Ошибка организации файла: {e}")
                            stats['errors'] += 1

                    stats['channels_processed'] += 1

                except Exception as e:
                    logger.error(f"❌ Ошибка канала {channel}: {e}")
                    stats['errors'] += 1

            # СТАТИСТИКА
            logger.info("\n📊 Статистика Telegram:")
            logger.info(f"   Каналов обработано: {stats['channels_processed']}")
            logger.info(f"   Файлов найдено: {stats['files_found']}")
            logger.info(f"   Файлов скачано: {stats['files_downloaded']}")
            logger.info(f"   Файлов пропущено: {stats['files_skipped']}")
            if stats['files_redownloaded'] > 0:
                logger.info(f"   Повторно скачано: {stats['files_redownloaded']}")

        finally:
            await downloader.disconnect()

    except ImportError as e:
        logger.error(f"❌ Не установлен модуль: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка Telegram: {e}")
        stats['errors'] += 1

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 8: ПОВТОРНАЯ ПРОВЕРКА ВСЕХ ИСТОЧНИКОВ (НОВОЕ!)
# ═══════════════════════════════════════════════════════════════════════════════

async def recheck_all_sources(organizer, logger, file_tracker) -> Dict:
    """
    КОМАНДА: ПОЛНАЯ повторная проверка всех источников в конце сессии

    ЧТО ДЕЛАЕТ:
        1. ПОЛНОСТЬЮ сканирует все каналы (БЕЗ ОГРАНИЧЕНИЙ)
        2. Сравнивает с базой данных
        3. Находит новые файлы которые могли появиться
        4. Находит пропущенные файлы из разорванных сессий
        5. Скачивает только новое/пропущенное

    ЗАЧЕМ:
        - Новые файлы могли появиться за время работы программы
        - Файлы могли быть пропущены из-за сетевых ошибок
        - Файлы из старых сессий (2000+ сообщений назад) не пропадут
        - Финальная ПОЛНАЯ синхронизация

    ВАЖНО:
        Сканируются ВСЕ сообщения в каналах (message_limit=None),
        поэтому может занять время при большом количестве сообщений

    ВОЗВРАЩАЕТ:
        Dict - статистика повторной проверки
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("🔄 ПОЛНАЯ ПОВТОРНАЯ ПРОВЕРКА ИСТОЧНИКОВ")
    logger.info("=" * 60)
    logger.info("📊 Сканируем ВСЕ сообщения в каналах (без ограничений)")
    logger.info("⏱️ Это может занять время, но гарантирует полную синхронизацию...")

    total_stats = {
        'new_files_found': 0,
        'new_files_downloaded': 0,
    }

    # TELEGRAM: Повторная проверка каналов (только последние 100 сообщений)
    try:
        tg_stats = await download_from_telegram(
            organizer,
            logger,
            file_tracker,
            recheck_mode=True  # Режим повторной проверки
        )
        total_stats['new_files_downloaded'] += tg_stats.get('files_downloaded', 0)
    except Exception as e:
        logger.error(f"❌ Ошибка повторной проверки Telegram: {e}")

    # ИТОГО
    if total_stats['new_files_downloaded'] > 0:
        logger.info(f"\n✨ Найдено и скачано новых файлов: {total_stats['new_files_downloaded']}")
    else:
        logger.info("\n✅ Новых файлов не обнаружено")

    return total_stats


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 9: ОСТАЛЬНЫЕ ЗАГРУЗЧИКИ (WEB, GITHUB, TORRENTS)
# ═══════════════════════════════════════════════════════════════════════════════

async def download_from_web(organizer, logger) -> Dict:
    """Скачивает файлы с веб-сайтов (УЛУЧШЕНО: async context manager)"""
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
        from downloaders.web_downloader import WebDownloader
        from config import WEB_SOURCES, REQUEST_DELAY

        # ИСПРАВЛЕНО: Используем async with для автоматического закрытия сессии
        async with WebDownloader(
            download_path=BASE_DOWNLOAD_PATH / '_web_raw',
            delay=REQUEST_DELAY,
            verify_ssl=False,  # Отключаем проверку SSL для сайтов с самоподписанными сертификатами
        ) as downloader:

            # Обрабатываем каждый источник
            for source_name, source_config in WEB_SOURCES.items():
                if not source_config.get('enabled', False):
                    continue

                logger.info(f"\n🔗 Источник: {source_name}")

                try:
                    base_url = source_config.get('base_url')
                    encoding = source_config.get('encoding', None)  # Поддержка принудительной кодировки
                    follow_pagination = source_config.get('follow_pagination', True)
                    max_pages = source_config.get('max_pages', 10)

                    if base_url:
                        files = await downloader.download_from_page(
                            url=base_url,
                            file_extensions=ALLOWED_EXTENSIONS,
                            subfolder=source_name,
                            keywords_include=KEYWORDS_INCLUDE,
                            keywords_exclude=KEYWORDS_EXCLUDE,
                            encoding=encoding,  # Передаём настройку кодировки
                            follow_pagination=follow_pagination,
                            max_pages=max_pages,
                        )

                        stats['sites_processed'] += 1
                        stats['files_downloaded'] += len(files)

                        # Сортируем файлы
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

            # Статистика
            web_stats = downloader.stats
            logger.info("\n📊 Статистика веб-скачивания:")
            logger.info(f"   Страниц обработано: {web_stats['pages_processed']}")
            logger.info(f"   Ссылок найдено: {web_stats['links_found']}")
            logger.info(f"   Файлов скачано: {web_stats['files_downloaded']}")

    except ImportError as e:
        logger.error(f"❌ Не установлен модуль: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка веб-скачивания: {e}")
        stats['errors'] += 1

    return stats


async def download_from_github(organizer, logger) -> Dict:
    """Скачивает файлы с GitHub (без изменений)"""
    stats = {
        'repos_processed': 0,
        'files_downloaded': 0,
        'total_size': 0,
        'errors': 0,
    }

    if not GITHUB_SOURCES:
        return stats

    logger.info("")
    logger.info("=" * 60)
    logger.info("🐙 СКАЧИВАНИЕ С GITHUB")
    logger.info("=" * 60)

    logger.info("⚠️ GitHub загрузчик не реализован в этой версии")

    return stats


async def download_from_torrents(organizer, logger) -> Dict:
    """Скачивает файлы с торрент-трекеров"""
    stats = {
        'torrents_found': 0,
        'torrents_downloaded': 0,
        'errors': 0,
    }

    if not TORRENT_ENABLED:
        return stats

    logger.info("")
    logger.info("=" * 60)
    logger.info("🧲 СКАЧИВАНИЕ ТОРРЕНТОВ")
    logger.info("=" * 60)

    try:
        from config import (
            RUTRACKER_ENABLED, RUTRACKER_USERNAME, RUTRACKER_PASSWORD,
            RUTRACKER_SEARCH_QUERIES, RUTRACKER_MIN_SEEDS
        )

        if not RUTRACKER_ENABLED or not RUTRACKER_USERNAME or not RUTRACKER_PASSWORD:
            logger.warning("⚠️ RuTracker не настроен. Пропускаем.")
            return stats

        from downloaders.torrent_downloader import RuTrackerDownloader

        async with RuTrackerDownloader(
            username=RUTRACKER_USERNAME,
            password=RUTRACKER_PASSWORD,
            download_path=BASE_DOWNLOAD_PATH / '_torrents'
        ) as tracker:

            # Авторизация
            if not await tracker.login():
                logger.error("❌ Не удалось авторизоваться на RuTracker")
                return stats

            # Поиск по каждому запросу
            for query in RUTRACKER_SEARCH_QUERIES:
                logger.info(f"\n🔍 Поиск: {query}")

                results = await tracker.search(
                    query=query,
                    max_results=10,
                    min_seeds=RUTRACKER_MIN_SEEDS,
                )

                stats['torrents_found'] += len(results)

                # Скачиваем .torrent файлы
                for torrent in results[:5]:  # Ограничиваем 5 на запрос
                    logger.info(f"   📥 {torrent.title[:60]}...")

                    torrent_file = await tracker.download_torrent(torrent)
                    if torrent_file:
                        stats['torrents_downloaded'] += 1

                # Пауза между запросами
                await asyncio.sleep(2)

            logger.info("\n📊 Статистика торрентов:")
            logger.info(f"   Найдено раздач: {stats['torrents_found']}")
            logger.info(f"   Скачано .torrent файлов: {stats['torrents_downloaded']}")
            logger.info("\n⚠️ Для загрузки содержимого откройте .torrent файлы в qBittorrent")

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
    """Форматирует размер файла"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} ПБ"


def print_banner():
    """Выводит заголовок программы"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 8 + "СКАЧИВАНИЕ АВТОМОБИЛЬНЫХ МАНУАЛОВ v2.1" + " " * 11 + "║")
    print("║" + " " * 12 + "С ПРОВЕРКОЙ ЦЕЛОСТНОСТИ ФАЙЛОВ" + " " * 16 + "║")
    print("║" + " " * 58 + "║")
    print("║  📱 Telegram  🌐 Веб-сайты  🐙 GitHub  🧲 Торренты" + " " * 6 + "║")
    print("║  ✅ Проверка целостности  🔄 Повторное скачивание" + " " * 7 + "║")
    print("╚" + "═" * 58 + "╝")
    print()


def print_results(stats: Dict, folder_stats: Dict, integrity_stats: Dict):
    """Выводит итоговую статистику"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 20 + "ИТОГОВАЯ СТАТИСТИКА" + " " * 19 + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Всего файлов в библиотеке: {folder_stats['total_files']:>26} ║")
    print(f"║  Общий размер: {format_size(folder_stats['total_size']):>39} ║")
    print("║" + " " * 58 + "║")
    print(f"║  Скачано за сессию: {stats['total_files']:>34} ║")
    print(f"║  Повторно скачано: {stats.get('redownloaded', 0):>35} ║")
    print(f"║  Ошибок: {stats['total_errors']:>45} ║")
    print("╠" + "═" * 58 + "╣")
    print("║  ПРОВЕРКА ЦЕЛОСТНОСТИ:" + " " * 35 + "║")
    print(f"║  Проверено файлов: {integrity_stats.get('total_checked', 0):>35} ║")
    print(f"║  Полных: {integrity_stats.get('complete', 0):>47} ║")
    print(f"║  Недокачанных: {integrity_stats.get('incomplete', 0):>41} ║")
    print(f"║  Отсутствующих: {integrity_stats.get('missing', 0):>40} ║")
    print("╚" + "═" * 58 + "╝")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 11: ГЛАВНАЯ ФУНКЦИЯ (УЛУЧШЕННАЯ!)
# ═══════════════════════════════════════════════════════════════════════════════

def load_temp_config():
    """Загрузить временный конфиг с выбранными источниками"""
    temp_config_path = Path('temp_config.json')
    if temp_config_path.exists():
        with open(temp_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


async def main(selected_sources: Optional[Dict] = None):
    """
    ГЛАВНАЯ ФУНКЦИЯ с проверкой целостности и повторным скачиванием

    ПОРЯДОК РАБОТЫ:
        1. Настройка логирования
        2. Инициализация FileTracker
        3. ПРОВЕРКА ЦЕЛОСТНОСТИ файлов из предыдущих сессий
        4. Скачивание из выбранных источников
        5. ПОВТОРНАЯ ПРОВЕРКА источников в конце
        6. Итоговая статистика

    Args:
        selected_sources: Словарь с выбранными источниками:
            {
                'telegram': ['avtomanualy', 'avtolit'],
                'web': ['manualslib'],
                'github': [0, 1]
            }
    """
    # 1. НАСТРОЙКА
    logger = setup_logging()
    print_banner()

    logger.info(f"🚀 Начало работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📁 Папка для сохранения: {BASE_DOWNLOAD_PATH.absolute()}")

    # Применяем фильтрацию источников если указано
    if selected_sources:
        logger.info("📋 Выбранные источники:")

        # Фильтруем Telegram каналы
        if selected_sources.get('telegram'):
            import config as cfg
            cfg.TELEGRAM_CHANNELS = selected_sources['telegram']
            logger.info(f"   📱 Telegram: {len(selected_sources['telegram'])} каналов")

        # Фильтруем Web сайты
        if selected_sources.get('web'):
            import config as cfg
            # Отключаем все сайты
            for key in cfg.WEB_SOURCES:
                cfg.WEB_SOURCES[key]['enabled'] = False
            # Включаем только выбранные
            for web_id in selected_sources['web']:
                if web_id in cfg.WEB_SOURCES:
                    cfg.WEB_SOURCES[web_id]['enabled'] = True
            logger.info(f"   🌐 Web: {len(selected_sources['web'])} сайтов")

        # Фильтруем GitHub репозитории
        if selected_sources.get('github'):
            import config as cfg
            # Отключаем все репо
            for repo in cfg.GITHUB_SOURCES:
                repo['enabled'] = False
            # Включаем только выбранные (по URL, а не по индексу!)
            for github_url in selected_sources['github']:
                for repo in cfg.GITHUB_SOURCES:
                    if repo['url'] == github_url:
                        repo['enabled'] = True
                        break
            logger.info(f"   🐙 GitHub: {len(selected_sources['github'])} репозиториев")

    # 2. ИНИЦИАЛИЗАЦИЯ: Создаём FileTracker для отслеживания
    try:
        from utils.file_tracker import FileTracker
        file_tracker = FileTracker(db_path=Path('./data/files_tracker.db'))
        logger.info("✅ FileTracker инициализирован")
    except ImportError:
        logger.error("❌ Не найден модуль file_tracker")
        logger.info("   Работа без отслеживания целостности")
        file_tracker = None

    # 3. ПРОВЕРКА ЦЕЛОСТНОСТИ: Проверяем файлы из прошлых сессий
    integrity_stats = {}
    if file_tracker:
        integrity_stats = await check_file_integrity(file_tracker, logger)

    # 4. ОРГАНИЗАТОР: Создаём FileOrganizer
    try:
        from utils.file_organizer import FileOrganizer
        organizer = FileOrganizer(BASE_DOWNLOAD_PATH)
    except ImportError:
        logger.error("❌ Не найден модуль file_organizer")
        return

    # 5. СТАТИСТИКА
    total_stats = {
        'total_files': 0,
        'redownloaded': 0,
        'total_errors': 0,
    }

    # 6. TELEGRAM: Скачивание с проверкой
    run_telegram = not selected_sources or (selected_sources and len(selected_sources.get('telegram', [])) > 0)
    if run_telegram:
        try:
            logger.info("\n🔄 Запуск Telegram загрузчика...")
            tg_stats = await download_from_telegram(organizer, logger, file_tracker)
            total_stats['total_files'] += tg_stats.get('files_downloaded', 0)
            total_stats['redownloaded'] += tg_stats.get('files_redownloaded', 0)
            total_stats['total_errors'] += tg_stats.get('errors', 0)
        except Exception as e:
            logger.error(f"❌ Критическая ошибка Telegram: {e}")
    else:
        logger.info("\n⏭️ Telegram пропущен (не выбран)")

    # 7. WEB: Скачивание с сайтов
    run_web = not selected_sources or (selected_sources and len(selected_sources.get('web', [])) > 0)
    if run_web:
        try:
            logger.info("\n🔄 Запуск веб-загрузчика...")
            web_stats = await download_from_web(organizer, logger)
            total_stats['total_files'] += web_stats.get('files_downloaded', 0)
            total_stats['total_errors'] += web_stats.get('errors', 0)
        except Exception as e:
            logger.error(f"❌ Критическая ошибка веб-скачивания: {e}")
    else:
        logger.info("\n⏭️ Web пропущен (не выбран)")

    # 8. GITHUB: Скачивание репозиториев
    run_github = not selected_sources or (selected_sources and len(selected_sources.get('github', [])) > 0)
    if run_github:
        try:
            logger.info("\n🔄 Запуск GitHub загрузчика...")
            github_stats = await download_from_github(organizer, logger)
            total_stats['total_files'] += github_stats.get('files_downloaded', 0)
            total_stats['total_errors'] += github_stats.get('errors', 0)
        except Exception as e:
            logger.error(f"❌ Критическая ошибка GitHub: {e}")
    else:
        logger.info("\n⏭️ GitHub пропущен (не выбран)")

    # 9. TORRENTS: Скачивание торрентов
    run_torrent = not selected_sources or (selected_sources and len(selected_sources.get('torrent', [])) > 0)
    if run_torrent:
        try:
            logger.info("\n🔄 Запуск торрент-загрузчика...")
            torrent_stats = await download_from_torrents(organizer, logger)
            total_stats['total_files'] += torrent_stats.get('torrents_downloaded', 0)
            total_stats['total_errors'] += torrent_stats.get('errors', 0)
        except Exception as e:
            logger.error(f"❌ Критическая ошибка торрентов: {e}")
    else:
        logger.info("\n⏭️ Torrent пропущен (не выбран)")

    # 10. ПОВТОРНАЯ ПРОВЕРКА: Ищем новые файлы
    if file_tracker:
        try:
            recheck_stats = await recheck_all_sources(organizer, logger, file_tracker)
            total_stats['total_files'] += recheck_stats.get('new_files_downloaded', 0)
        except Exception as e:
            logger.error(f"❌ Ошибка повторной проверки: {e}")

    # 11. ИТОГИ
    folder_stats = organizer.get_stats()
    print_results(total_stats, folder_stats, integrity_stats)

    print(f"📁 Файлы сохранены в: {BASE_DOWNLOAD_PATH.absolute()}")
    if file_tracker:
        print(f"📊 База данных: {file_tracker.db_path.absolute()}")
    print()

    # 12. ОЧИСТКА
    if file_tracker:
        file_tracker.cleanup_old_records(days=30)
        file_tracker.close()

    logger.info(f"✅ Завершено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ═══════════════════════════════════════════════════════════════════════════════
# БЛОК 12: ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='LLCAR Auto Manuals Downloader v2.1'
    )
    parser.add_argument(
        '--use-temp-config', action='store_true',
        help='Использовать temp_config.json',
    )
    parser.add_argument(
        '--interactive', '-i', action='store_true',
        help='Запустить интерактивную консоль (console_ui)',
    )
    parser.add_argument(
        '--browse', '-b', metavar='CHANNEL',
        help='Просмотреть содержимое канала (напр. --browse avtomanualy)',
    )
    args = parser.parse_args()

    # ── Режим 1: Интерактивная консоль ────────────────────────────
    if args.interactive:
        try:
            from console_ui import ConsoleUI
            ui = ConsoleUI()
            asyncio.run(ui.run())
        except ImportError:
            print("❌ console_ui.py не найден")
            print("   pip install rich")
            sys.exit(1)

    # ── Режим 2: Просмотр канала ──────────────────────────────────
    elif args.browse:
        async def browse_mode():
            from downloaders.telegram_downloader import TelegramDownloader

            dl = TelegramDownloader(
                api_id=TELEGRAM_API_ID,
                api_hash=TELEGRAM_API_HASH,
                phone=TELEGRAM_PHONE,
                download_path=BASE_DOWNLOAD_PATH / '_telegram_raw',
            )

            if not await dl.connect():
                print("❌ Не удалось подключиться к Telegram")
                return

            try:
                files = await dl.list_channel_files(
                    channel_username=args.browse,
                    allowed_extensions=ALLOWED_EXTENSIONS,
                    max_size_mb=MAX_FILE_SIZE_MB,
                    message_limit=TELEGRAM_MESSAGE_LIMIT,
                    keywords_include=KEYWORDS_INCLUDE,
                    keywords_exclude=KEYWORDS_EXCLUDE,
                )

                print(f"\n{'='*70}")
                print(f"  📋 @{args.browse} — {len(files)} файлов")
                print(f"{'='*70}")

                for i, f in enumerate(files, 1):
                    status = '✅' if f.is_downloaded else '⬜'
                    print(
                        f"  {status} {i:>4}. [{f.message_id:>8}] "
                        f"{f.filename[:50]:<50} {f.size_str:>10}"
                    )

                new = [f for f in files if not f.is_downloaded]
                print(f"\n  Новых: {len(new)}, "
                      f"Скачано: {len(files) - len(new)}")

                if new:
                    answer = input(
                        "\nСкачать новые? (all/1,3,5/1-10/n): "
                    ).strip()

                    if answer.lower() == 'n':
                        return

                    if answer.lower() == 'all':
                        ids = [f.message_id for f in new]
                    else:
                        # Парсим
                        indices = set()
                        for part in answer.split(','):
                            part = part.strip()
                            if '-' in part:
                                a, b = part.split('-', 1)
                                for idx in range(int(a), int(b) + 1):
                                    if 1 <= idx <= len(files):
                                        indices.add(idx - 1)
                            else:
                                idx = int(part)
                                if 1 <= idx <= len(files):
                                    indices.add(idx - 1)

                        ids = [
                            files[i].message_id
                            for i in sorted(indices)
                            if not files[i].is_downloaded
                        ]

                    if ids:
                        print(f"\n📥 Скачивание {len(ids)} файлов...\n")
                        results = await dl.download_selected_files(
                            args.browse, ids
                        )
                        print(f"\n✅ Скачано: {len(results)}")

            finally:
                await dl.disconnect()

        asyncio.run(browse_mode())

    # ── Режим 3: Автоматический (как раньше) ──────────────────────
    else:
        selected_sources = None
        if args.use_temp_config:
            selected_sources = load_temp_config()
            if not selected_sources:
                print("❌ temp_config.json не найден!")
                sys.exit(1)

        asyncio.run(main(selected_sources))
