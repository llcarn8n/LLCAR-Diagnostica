"""
╔═══════════════════════════════════════════════════════════════════════════════
║  LLCAR AUTO MANUALS - УМНЫЙ УСТАНОВЩИК
║  Автоматически проверяет и устанавливает Python, если его нет
╚═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import subprocess
import urllib.request
import tempfile
from pathlib import Path

# Настройка кодировки для Windows
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class SmartInstaller:
    PYTHON_VERSION = "3.12.1"
    PYTHON_INSTALLER_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"

    def __init__(self):
        self.base_path = Path(__file__).parent

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, text):
        self.clear_screen()
        print("╔═══════════════════════════════════════════════════════════════╗")
        print(f"║  {text:^61}║")
        print("╚═══════════════════════════════════════════════════════════════╝\n")

    def check_python_installed(self):
        """Проверяет, установлен ли Python в системе"""
        try:
            # Пробуем запустить python
            result = subprocess.run(
                ['python', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"✅ {version_str} уже установлен")

                # Проверяем версию
                version = sys.version_info
                if version.major >= 3 and version.minor >= 8:
                    return True
                else:
                    print(f"⚠️ Версия слишком старая (нужна 3.8+)")
                    return False
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False

    def download_python_installer(self):
        """Скачивает установщик Python"""
        self.print_header("Скачивание Python")

        print(f"Скачивание Python {self.PYTHON_VERSION}...")
        print(f"Источник: {self.PYTHON_INSTALLER_URL}")
        print("\nЭто может занять 2-5 минут в зависимости от скорости интернета...")
        print("Размер: ~25 МБ\n")

        temp_dir = tempfile.gettempdir()
        installer_path = Path(temp_dir) / f"python-{self.PYTHON_VERSION}-installer.exe"

        try:
            # Показываем прогресс загрузки
            def reporthook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(100, downloaded * 100 // total_size)
                    bar_length = 40
                    filled = bar_length * percent // 100
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f'\r[{bar}] {percent}% ({downloaded // 1024 // 1024} МБ / {total_size // 1024 // 1024} МБ)', end='')

            urllib.request.urlretrieve(
                self.PYTHON_INSTALLER_URL,
                installer_path,
                reporthook=reporthook
            )
            print("\n\n✅ Python скачан успешно!")
            return installer_path

        except Exception as e:
            print(f"\n\n❌ Ошибка скачивания: {e}")
            print("\nВы можете:")
            print(f"  1. Скачать вручную с: https://www.python.org/downloads/")
            print(f"  2. Установить Python")
            print(f"  3. Перезапустить этот установщик")
            return None

    def install_python(self, installer_path):
        """Устанавливает Python"""
        self.print_header("Установка Python")

        print("Запуск установщика Python...")
        print("\n⚠️ ВАЖНО:")
        print("  • Отметьте галочку 'Add Python to PATH'")
        print("  • Выберите 'Install Now' (рекомендуется)")
        print("\nНажмите любую клавишу когда будете готовы...")
        input()

        try:
            # Запускаем установщик с параметрами
            # /quiet - тихая установка
            # InstallAllUsers=0 - для текущего пользователя
            # PrependPath=1 - добавить в PATH
            # Include_pip=1 - установить pip
            result = subprocess.run([
                str(installer_path),
                '/passive',  # Показывать прогресс, но не требовать взаимодействия
                'InstallAllUsers=0',
                'PrependPath=1',
                'Include_pip=1',
                'Include_test=0'
            ], timeout=600)  # 10 минут максимум

            if result.returncode == 0:
                print("\n✅ Python установлен успешно!")
                print("\n⚠️ ВАЖНО: Перезапустите эту программу для применения изменений!")
                input("\nНажмите Enter для выхода...")
                return True
            else:
                print(f"\n⚠️ Установщик вернул код: {result.returncode}")
                print("Возможно, нужно запустить установщик вручную с правами администратора")
                return False

        except subprocess.TimeoutExpired:
            print("\n⚠️ Превышено время ожидания установки")
            return False
        except Exception as e:
            print(f"\n❌ Ошибка установки: {e}")
            return False

    def install_dependencies(self):
        """Устанавливает зависимости Python"""
        self.print_header("Установка библиотек")

        required = [
            'telethon',
            'aiohttp',
            'beautifulsoup4',
            'aiofiles',
            'rich',
            'pycryptodome',
        ]

        print("Установка необходимых библиотек...")
        print(f"Список: {', '.join(required)}\n")

        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                *required,
                '--upgrade',
                '--quiet',
                '--disable-pip-version-check'
            ])
            print("\n✅ Все библиотеки установлены!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Ошибка установки библиотек: {e}")
            return False

    def launch_program(self):
        """Запускает основную программу"""
        self.print_header("Запуск программы")

        print("Запуск LLCAR Auto Manuals...\n")

        launcher = self.base_path / 'launcher.py'
        if launcher.exists():
            try:
                subprocess.run([sys.executable, str(launcher)])
            except Exception as e:
                print(f"\n❌ Ошибка запуска: {e}")
                input("\nНажмите Enter...")
        else:
            print("❌ launcher.py не найден!")
            print(f"Ожидается: {launcher}")
            input("\nНажмите Enter...")

    def run(self):
        """Главная логика установщика"""
        self.print_header("LLCAR Auto Manuals - Установщик")

        print("Добро пожаловать в установщик LLCAR Auto Manuals!\n")
        print("Этот установщик:")
        print("  ✅ Проверит наличие Python")
        print("  ✅ Установит Python, если его нет (автоматически)")
        print("  ✅ Установит все необходимые библиотеки")
        print("  ✅ Настроит программу")
        print("  ✅ Запустит LLCAR Auto Manuals\n")

        input("Нажмите Enter для начала установки...")

        # Шаг 1: Проверка Python
        self.print_header("ШАГ 1: Проверка Python")

        if not self.check_python_installed():
            print("\n❌ Python не найден или версия слишком старая\n")

            response = input("Автоматически скачать и установить Python? (y/n): ").lower()

            if response == 'y':
                # Скачиваем установщик
                installer_path = self.download_python_installer()

                if installer_path:
                    # Устанавливаем Python
                    if self.install_python(installer_path):
                        print("\n✅ Python установлен!")
                        print("\n⚠️ ПЕРЕЗАПУСТИТЕ эту программу для продолжения!")
                        input("\nНажмите Enter для выхода...")
                        sys.exit(0)
                    else:
                        print("\n❌ Не удалось установить Python автоматически")
                        print("\nПожалуйста:")
                        print("  1. Установите Python вручную с https://www.python.org/downloads/")
                        print("  2. При установке отметьте 'Add Python to PATH'")
                        print("  3. Перезапустите этот установщик")
                        input("\nНажмите Enter для выхода...")
                        sys.exit(1)
            else:
                print("\n⚠️ Установка прервана")
                print("\nДля работы программы необходим Python 3.8+")
                print("Установите Python с https://www.python.org/downloads/")
                input("\nНажмите Enter для выхода...")
                sys.exit(1)
        else:
            input("\nНажмите Enter для продолжения...")

        # Шаг 2: Установка зависимостей
        self.print_header("ШАГ 2: Установка библиотек")

        if not self.install_dependencies():
            print("\n❌ Не удалось установить библиотеки")
            input("\nНажмите Enter для выхода...")
            sys.exit(1)

        input("\nНажмите Enter для продолжения...")

        # Шаг 3: Запуск программы
        self.print_header("ШАГ 3: Запуск")

        print("✅ Установка завершена!\n")
        print("Сейчас будет запущена основная программа.")
        print("При первом запуске вам нужно будет указать:")
        print("  • Telegram API ID")
        print("  • Telegram API Hash")
        print("  • Номер телефона\n")
        print("Получить API ключи можно на: https://my.telegram.org/apps\n")

        input("Нажмите Enter для запуска...")

        self.launch_program()


if __name__ == '__main__':
    try:
        installer = SmartInstaller()
        installer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Установка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
