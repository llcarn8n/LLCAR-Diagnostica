"""
╔═══════════════════════════════════════════════════════════════════════════════
║  LLCAR AUTO MANUALS DOWNLOADER - МАСТЕР ПЕРВОЙ НАСТРОЙКИ
║  Автоматическая установка и конфигурация
╚═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Настраиваем UTF-8 для Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class SetupWizard:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_path = self.base_path / 'config.py'
        self.settings_path = self.base_path / 'data' / 'wizard_settings.json'
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, text):
        self.clear_screen()
        print("╔═══════════════════════════════════════════════════════════════╗")
        print(f"║  {text:^61}║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()

    def load_settings(self):
        """Загружает сохраненные настройки"""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_settings(self, settings):
        """Сохраняет настройки"""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Предупреждение: не удалось сохранить настройки: {e}")

    def check_python(self):
        """Проверка версии Python"""
        self.print_header("ШАГ 1: Проверка Python")

        version = sys.version_info
        print(f"Python версия: {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("\n❌ ОШИБКА: Требуется Python 3.8 или новее!")
            print("   Скачайте с: https://www.python.org/downloads/")
            input("\nНажмите Enter для выхода...")
            sys.exit(1)

        print("✅ Версия Python подходит")
        input("\nНажмите Enter для продолжения...")
        return True

    def install_dependencies(self):
        """Установка зависимостей"""
        self.print_header("ШАГ 2: Установка библиотек")

        required = {
            'telethon': 'Telegram API клиент',
            'aiohttp': 'Асинхронные HTTP запросы',
            'beautifulsoup4': 'Парсинг HTML',
            'aiofiles': 'Асинхронная работа с файлами',
            'rich': 'Красивый интерфейс консоли',
        }

        print("Проверка установленных модулей:\n")

        missing = []
        for package, description in required.items():
            module = package if package != 'beautifulsoup4' else 'bs4'
            try:
                __import__(module)
                print(f"  ✅ {package:20} - {description}")
            except ImportError:
                print(f"  ❌ {package:20} - НЕ УСТАНОВЛЕН")
                missing.append(package)

        if missing:
            print(f"\n📦 Необходимо установить: {', '.join(missing)}")
            response = input("\nУстановить сейчас? (y/n): ").lower()

            if response == 'y':
                print("\nУстановка...")
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install',
                        *missing, '--upgrade', '--quiet'
                    ])
                    print("\n✅ Библиотеки установлены!")
                except Exception as e:
                    print(f"\n❌ Ошибка установки: {e}")
                    input("\nНажмите Enter...")
                    return False
            else:
                print("\n⚠️ Без библиотек программа не будет работать!")
                input("\nНажмите Enter...")
                return False
        else:
            print("\n✅ Все основные библиотеки установлены!")

        # Проверка ускорителей
        print("\n" + "─" * 63)
        print("Проверка ускорителей криптографии (для Telegram):\n")

        has_cryptg = False
        has_pycrypto = False

        try:
            import cryptg
            has_cryptg = True
            print("  ✅ cryptg - МАКСИМАЛЬНАЯ скорость (10-20x)")
        except ImportError:
            print("  ❌ cryptg - не установлен")

        if not has_cryptg:
            try:
                from Crypto.Cipher import AES
                has_pycrypto = True
                print("  ✅ pycryptodome - средняя скорость (3-5x)")
            except ImportError:
                print("  ❌ pycryptodome - не установлен")

        if not has_cryptg and not has_pycrypto:
            print("\n⚠️ ВНИМАНИЕ: Без ускорителя загрузка будет ОЧЕНЬ медленной!")
            print("\nРекомендуется установить:")
            print("  1. pycryptodome (работает везде)")
            print("  2. cryptg (требует компилятор, но быстрее)")

            choice = input("\nУстановить pycryptodome? (y/n): ").lower()
            if choice == 'y':
                try:
                    print("\nУстановка pycryptodome...")
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install',
                        'pycryptodome', '--quiet'
                    ])
                    print("✅ pycryptodome установлен!")
                except Exception as e:
                    print(f"❌ Ошибка: {e}")

        input("\nНажмите Enter для продолжения...")
        return True

    def configure_telegram(self):
        """Настройка Telegram API"""
        self.print_header("ШАГ 3: Настройка Telegram API")

        saved = self.load_settings()

        print("Для работы с Telegram нужны API ключи.")
        print("Получить их можно на: https://my.telegram.org/apps")
        print("\nИнструкция:")
        print("  1. Откройте https://my.telegram.org/apps")
        print("  2. Войдите с вашим номером телефона")
        print("  3. Создайте приложение (App title: LLCAR, Short name: llcar)")
        print("  4. Скопируйте api_id и api_hash")
        print("\n" + "─" * 63)

        # API ID
        default_api_id = saved.get('api_id', '')
        if default_api_id:
            print(f"\nТекущий API ID: {default_api_id}")
            use_saved = input("Использовать сохраненный? (y/n): ").lower()
            if use_saved == 'y':
                api_id = default_api_id
            else:
                api_id = input("\nВведите API ID: ").strip()
        else:
            api_id = input("\nВведите API ID: ").strip()

        # API Hash
        default_api_hash = saved.get('api_hash', '')
        if default_api_hash:
            print(f"\nТекущий API Hash: {default_api_hash[:10]}...")
            use_saved = input("Использовать сохраненный? (y/n): ").lower()
            if use_saved == 'y':
                api_hash = default_api_hash
            else:
                api_hash = input("\nВведите API Hash: ").strip()
        else:
            api_hash = input("Введите API Hash: ").strip()

        # Phone
        default_phone = saved.get('phone', '')
        if default_phone:
            print(f"\nТекущий номер: {default_phone}")
            use_saved = input("Использовать сохраненный? (y/n): ").lower()
            if use_saved == 'y':
                phone = default_phone
            else:
                phone = input("\nВведите номер телефона (+7...): ").strip()
        else:
            phone = input("\nВведите номер телефона (+7...): ").strip()

        if not api_id or not api_hash or not phone:
            print("\n❌ Не все поля заполнены!")
            input("\nНажмите Enter...")
            return None

        # Сохраняем настройки
        settings = {
            'api_id': api_id,
            'api_hash': api_hash,
            'phone': phone,
            'configured': True
        }
        self.save_settings(settings)

        # Обновляем config.py
        self.update_config(api_id, api_hash, phone)

        print("\n✅ Настройки сохранены!")
        input("\nНажмите Enter для продолжения...")
        return settings

    def update_config(self, api_id, api_hash, phone):
        """Обновляет config.py"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Заменяем значения
                import re
                content = re.sub(
                    r"TELEGRAM_API_ID\s*=\s*\d+",
                    f"TELEGRAM_API_ID = {api_id}",
                    content
                )
                content = re.sub(
                    r"TELEGRAM_API_HASH\s*=\s*['\"].*?['\"]",
                    f"TELEGRAM_API_HASH = '{api_hash}'",
                    content
                )
                content = re.sub(
                    r"TELEGRAM_PHONE\s*=\s*['\"].*?['\"]",
                    f"TELEGRAM_PHONE = '{phone}'",
                    content
                )

                with open(self.config_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print("✅ config.py обновлен")
        except Exception as e:
            print(f"⚠️ Не удалось обновить config.py: {e}")

    def final_menu(self):
        """Финальное меню"""
        self.print_header("УСТАНОВКА ЗАВЕРШЕНА!")

        print("✅ Все готово к работе!\n")
        print("Выберите действие:\n")
        print("  [1] 🖥️  Запустить интерактивную консоль")
        print("  [2] 🚀 Запустить автоматическую загрузку")
        print("  [3] 📋 Открыть инструкцию (КАК_ЗАПУСКАТЬ.txt)")
        print("  [0] 🚪 Выход")
        print()

        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            self.launch_interactive()
        elif choice == '2':
            self.launch_auto()
        elif choice == '3':
            self.open_readme()
        else:
            print("\nДо встречи! 👋")
            sys.exit(0)

    def launch_interactive(self):
        """Запуск интерактивной консоли"""
        self.clear_screen()
        print("Запуск интерактивной консоли...\n")
        try:
            subprocess.run([sys.executable, str(self.base_path / 'main_v2.py'), '--interactive'])
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
        except Exception as e:
            print(f"\n❌ Ошибка запуска: {e}")
            input("\nНажмите Enter...")

    def launch_auto(self):
        """Запуск автоматической загрузки"""
        self.clear_screen()
        print("Запуск автоматической загрузки...\n")
        try:
            subprocess.run([sys.executable, str(self.base_path / 'main_v2.py')])
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
        except Exception as e:
            print(f"\n❌ Ошибка запуска: {e}")
            input("\nНажмите Enter...")

    def open_readme(self):
        """Открытие README"""
        readme = self.base_path / 'КАК_ЗАПУСКАТЬ.txt'
        if readme.exists():
            if sys.platform == 'win32':
                os.startfile(str(readme))
            else:
                subprocess.run(['xdg-open', str(readme)])
        else:
            print("\n❌ Файл КАК_ЗАПУСКАТЬ.txt не найден")
            input("\nНажмите Enter...")

    def run(self):
        """Главный цикл мастера"""
        saved = self.load_settings()

        if saved.get('configured'):
            # Уже настроено - показываем меню
            self.final_menu()
        else:
            # Первый запуск - проходим все шаги
            if not self.check_python():
                return

            if not self.install_dependencies():
                return

            settings = self.configure_telegram()
            if not settings:
                print("\n❌ Настройка не завершена")
                input("\nНажмите Enter для выхода...")
                return

            self.final_menu()


if __name__ == '__main__':
    try:
        wizard = SetupWizard()
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Установка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
