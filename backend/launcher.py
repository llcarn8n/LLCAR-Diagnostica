"""
╔═══════════════════════════════════════════════════════════════════════════════
║  LLCAR AUTO MANUALS - УНИВЕРСАЛЬНЫЙ ЛАУНЧЕР
║  Один EXE файл для установки и запуска
╚═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
from pathlib import Path

# Настраиваем UTF-8 для Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def main():
    base_path = Path(__file__).parent

    # Проверяем, настроен ли config
    config_path = base_path / 'config.py'
    settings_path = base_path / 'data' / 'wizard_settings.json'

    # Если не настроено - запускаем мастер
    if not settings_path.exists():
        print("Первый запуск - запуск мастера настройки...\n")
        from setup_wizard import SetupWizard
        wizard = SetupWizard()
        wizard.run()
    else:
        # Уже настроено - показываем главное меню
        show_main_menu()


def show_main_menu():
    """Главное меню программы"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║                                                               ║")
        print("║       LLCAR Auto Manuals Downloader v2.1                      ║")
        print("║       LONG LIFE CAR MANUALS                                   ║")
        print("║                                                               ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        print("  Выберите режим работы:")
        print()
        print("  [1] 📋 Интерактивная консоль (полный функционал)")
        print("  [2] 🚀 Автоматическая загрузка (все источники)")
        print("  [3] 🔍 Просмотр конкретного канала")
        print("  [4] ⚙️  Настройка (изменить API ключи)")
        print("  [0] 🚪 Выход")
        print()

        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            launch_interactive()
        elif choice == '2':
            launch_auto()
        elif choice == '3':
            launch_browse()
        elif choice == '4':
            reconfigure()
        elif choice == '0':
            break
        else:
            input("\nНеверный выбор. Нажмите Enter...")


def launch_interactive():
    """Запуск интерактивной консоли"""
    try:
        from console_ui import ConsoleUI
        import asyncio

        ui = ConsoleUI()
        asyncio.run(ui.run())
    except ImportError as e:
        print(f"\n❌ Ошибка импорта: {e}")
        print("   Возможно, не установлены зависимости")
        input("\nНажмите Enter...")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        input("\nНажмите Enter...")


def launch_auto():
    """Автоматическая загрузка"""
    try:
        import asyncio
        import main_v2

        asyncio.run(main_v2.main())
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        input("\nНажмите Enter...")


def launch_browse():
    """Просмотр канала"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nВведите имя канала (без @):")
    print("Примеры: avtomanualy, autobook_original\n")
    channel = input("Канал: ").strip()

    if not channel:
        return

    try:
        import asyncio
        from downloaders.telegram_downloader import TelegramDownloader
        from config import (
            TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE,
            BASE_DOWNLOAD_PATH, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB,
            TELEGRAM_MESSAGE_LIMIT, KEYWORDS_INCLUDE, KEYWORDS_EXCLUDE
        )

        async def browse():
            dl = TelegramDownloader(
                api_id=TELEGRAM_API_ID,
                api_hash=TELEGRAM_API_HASH,
                phone=TELEGRAM_PHONE,
                download_path=BASE_DOWNLOAD_PATH / '_telegram_raw',
            )

            if not await dl.connect():
                print("\n❌ Не удалось подключиться к Telegram")
                input("\nНажмите Enter...")
                return

            try:
                files = await dl.list_channel_files(
                    channel_username=channel,
                    allowed_extensions=ALLOWED_EXTENSIONS,
                    max_size_mb=MAX_FILE_SIZE_MB,
                    message_limit=TELEGRAM_MESSAGE_LIMIT,
                    keywords_include=KEYWORDS_INCLUDE,
                    keywords_exclude=KEYWORDS_EXCLUDE,
                )

                print(f"\n{'='*70}")
                print(f"  📋 @{channel} — {len(files)} файлов")
                print(f"{'='*70}")

                for i, f in enumerate(files, 1):
                    status = '✅' if f.is_downloaded else '⬜'
                    print(
                        f"  {status} {i:>4}. [{f.message_id:>8}] "
                        f"{f.filename[:50]:<50} {f.size_str:>10}"
                    )

                new = [f for f in files if not f.is_downloaded]
                print(f"\n  Новых: {len(new)}, Скачано: {len(files) - len(new)}")

                if new:
                    answer = input("\nСкачать новые? (all/1,3,5/1-10/n): ").strip()

                    if answer.lower() != 'n':
                        if answer.lower() == 'all':
                            ids = [f.message_id for f in new]
                        else:
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
                            results = await dl.download_selected_files(channel, ids)
                            print(f"\n✅ Скачано: {len(results)}")
            finally:
                await dl.disconnect()

        asyncio.run(browse())
        input("\nНажмите Enter...")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        input("\nНажмите Enter...")


def reconfigure():
    """Повторная настройка"""
    from setup_wizard import SetupWizard

    wizard = SetupWizard()
    settings = wizard.configure_telegram()

    if settings:
        print("\n✅ Настройки обновлены!")

    input("\nНажмите Enter...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
