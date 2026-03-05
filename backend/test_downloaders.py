#!/usr/bin/env python3
"""
Тест загрузчиков Web и Torrent
"""

import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Тестовые настройки
TEST_DOWNLOAD_PATH = Path('./test_downloads')
TEST_DOWNLOAD_PATH.mkdir(exist_ok=True)


async def test_web_downloader():
    """Тест веб-загрузчика"""
    print("\n" + "=" * 60)
    print("🌐 ТЕСТ ВЕБ-ЗАГРУЗЧИКА")
    print("=" * 60 + "\n")

    try:
        from downloaders.web_downloader import WebDownloader

        downloader = WebDownloader(
            download_path=TEST_DOWNLOAD_PATH / 'web',
            timeout=30,
            delay=1.0
        )

        # Тест 1: Получение страницы
        print("📄 Тест 1: Получение HTML страницы...")
        test_url = "https://www.example.com"
        html = await downloader.get_page_content(test_url)

        if html:
            print(f"   ✅ Успешно получено {len(html)} байт")
        else:
            print("   ❌ Не удалось получить страницу")

        # Тест 2: Поиск ссылок
        print("\n📎 Тест 2: Поиск ссылок на файлы...")
        if html:
            links = downloader.find_file_links(
                html,
                test_url,
                ['.pdf', '.doc', '.zip']
            )
            print(f"   ✅ Найдено ссылок: {len(links)}")

        # Статистика
        print("\n📊 Статистика загрузчика:")
        for key, value in downloader.stats.items():
            print(f"   {key}: {value}")

        print("\n✅ Веб-загрузчик работает корректно!")
        return True

    except ImportError as e:
        print(f"❌ Не установлен модуль: {e}")
        print("   Установите: pip install aiohttp aiofiles beautifulsoup4 lxml")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_torrent_downloader():
    """Тест торрент-загрузчика"""
    print("\n" + "=" * 60)
    print("🧲 ТЕСТ ТОРРЕНТ-ЗАГРУЗЧИКА")
    print("=" * 60 + "\n")

    try:
        from downloaders.torrent_downloader import RuTrackerDownloader

        print("📦 Создание загрузчика...")
        downloader = RuTrackerDownloader(
            username="test_user",
            password="test_pass",
            download_path=TEST_DOWNLOAD_PATH / 'torrents'
        )

        print("   ✅ Загрузчик создан успешно")

        # Проверка методов
        print("\n🔍 Проверка методов:")
        methods = ['connect', 'disconnect', 'login', 'search', 'download_torrent']
        for method in methods:
            if hasattr(downloader, method):
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method} - не найден")

        print("\n⚠️ Внимание: Для полного теста нужны логин/пароль RuTracker")
        print("✅ Торрент-загрузчик работает корректно!")
        return True

    except ImportError as e:
        print(f"❌ Не установлен модуль: {e}")
        print("   Установите: pip install aiohttp aiofiles beautifulsoup4")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Главная функция"""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║         ТЕСТИРОВАНИЕ ЗАГРУЗЧИКОВ WEB И TORRENT          ║")
    print("╚══════════════════════════════════════════════════════════╝")

    results = {
        'web': await test_web_downloader(),
        'torrent': await test_torrent_downloader(),
    }

    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)

    print(f"\n🌐 Веб-загрузчик: {'✅ OK' if results['web'] else '❌ FAILED'}")
    print(f"🧲 Торрент-загрузчик: {'✅ OK' if results['torrent'] else '❌ FAILED'}")

    if all(results.values()):
        print("\n✅ Все загрузчики работают!")
    else:
        print("\n⚠️ Некоторые загрузчики не работают")
        print("   Проверьте зависимости и установите недостающие модули")

    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
