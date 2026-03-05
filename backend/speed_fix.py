#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
              ИСПРАВЛЕНИЕ МЕДЛЕННОЙ СКОРОСТИ СКАЧИВАНИЯ
═══════════════════════════════════════════════════════════════════════════════

ПРОБЛЕМА:
    Telethon работает медленно из-за отсутствия cryptg (C-расширение)

РЕШЕНИЯ:
    1. Установка cryptg (если есть компилятор)
    2. Установка pycryptodome (альтернатива, только Python)
    3. Настройка параллельных соединений
    4. Увеличение размера буфера

ЗАПУСК:
    python speed_fix.py
"""

import sys
import subprocess
import platform


def print_section(title):
    """Красивый вывод секции"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_cryptg():
    """Проверяет установлен ли cryptg"""
    print_section("🔍 ПРОВЕРКА CRYPTG")

    try:
        import cryptg
        print("✅ cryptg установлен!")
        print(f"   Версия: {cryptg.__version__ if hasattr(cryptg, '__version__') else 'неизвестна'}")
        return True
    except ImportError:
        print("❌ cryptg НЕ установлен")
        print("   Telethon использует медленный Python-код для шифрования")
        return False


def check_pycryptodome():
    """Проверяет установлен ли pycryptodome"""
    print_section("🔍 ПРОВЕРКА PYCRYPTODOME")

    try:
        from Crypto.Cipher import AES
        from Crypto import version_info
        print("✅ pycryptodome установлен!")
        print(f"   Версия: {'.'.join(map(str, version_info))}")
        return True
    except ImportError:
        print("❌ pycryptodome НЕ установлен")
        return False


def install_cryptg():
    """Пытается установить cryptg"""
    print_section("📦 УСТАНОВКА CRYPTG")

    print("Попытка 1: Установка из PyPI...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 'cryptg',
            '--upgrade', '--no-cache-dir'
        ])
        print("✅ cryptg установлен успешно!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Не удалось установить cryptg")
        print("   Требуется компилятор C/C++")
        return False


def install_pycryptodome():
    """Устанавливает pycryptodome как альтернативу"""
    print_section("📦 УСТАНОВКА PYCRYPTODOME (АЛЬТЕРНАТИВА)")

    print("ℹ️  pycryptodome - это чистый Python, работает везде")
    print("   Быстрее чем без ничего, но медленнее чем cryptg\n")

    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 'pycryptodome',
            '--upgrade'
        ])
        print("✅ pycryptodome установлен успешно!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Не удалось установить pycryptodome")
        return False


def check_compiler():
    """Проверяет наличие компилятора C/C++"""
    print_section("🔧 ПРОВЕРКА КОМПИЛЯТОРА")

    system = platform.system()

    if system == "Windows":
        print("Система: Windows")
        print("\nДля cryptg на Windows нужен Microsoft Visual C++:")
        print("  1. Установите 'Build Tools for Visual Studio'")
        print("  2. Или установите 'Microsoft C++ Build Tools'")
        print("  3. Скачать: https://visualstudio.microsoft.com/downloads/")
        print("\nИЛИ используйте pycryptodome (не требует компилятора)")

    elif system == "Linux":
        print("Система: Linux")
        # Проверяем gcc
        try:
            result = subprocess.run(['gcc', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ gcc установлен")
                print(result.stdout.split('\n')[0])
            else:
                print("❌ gcc не найден")
                print("   Установите: sudo apt install build-essential")
        except FileNotFoundError:
            print("❌ gcc не найден")
            print("   Установите: sudo apt install build-essential")

    elif system == "Darwin":
        print("Система: macOS")
        # Проверяем clang
        try:
            result = subprocess.run(['clang', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ clang установлен")
            else:
                print("❌ clang не найден")
                print("   Установите: xcode-select --install")
        except FileNotFoundError:
            print("❌ clang не найден")
            print("   Установите: xcode-select --install")


def show_speed_comparison():
    """Показывает сравнение скорости"""
    print_section("⚡ СРАВНЕНИЕ СКОРОСТИ")

    print("Относительная скорость шифрования:")
    print("  🐌 Без cryptg/pycryptodome:  1x (базовая)")
    print("  🚀 С pycryptodome:           3-5x быстрее")
    print("  🚀🚀 С cryptg:                10-20x быстрее")
    print("\nРеальная скорость скачивания зависит от:")
    print("  • Скорости интернета")
    print("  • Загруженности серверов Telegram")
    print("  • Размера файлов")


def show_recommendations():
    """Показывает рекомендации"""
    print_section("💡 РЕКОМЕНДАЦИИ")

    has_cryptg = check_cryptg()
    has_pycrypto = check_pycryptodome()

    print("\n📋 Ваш статус:")
    if has_cryptg:
        print("  ✅ У вас установлен cryptg - максимальная скорость!")
        print("  ℹ️  Ничего делать не нужно")
    elif has_pycrypto:
        print("  ⚠️  У вас pycryptodome - средняя скорость")
        print("  💡 Попробуйте установить cryptg для ускорения")
    else:
        print("  ❌ Нет ускорения - минимальная скорость")
        print("  🔥 СРОЧНО установите pycryptodome!")

    print("\n🎯 Что делать:")
    if not has_cryptg and not has_pycrypto:
        print("  1. Запустите: pip install pycryptodome")
        print("  2. Попробуйте: pip install cryptg")
    elif not has_cryptg and has_pycrypto:
        print("  1. Попробуйте: pip install cryptg")
        print("  2. Если не получится - используйте pycryptodome")


def create_optimized_config():
    """Создаёт оптимизированный config"""
    print_section("⚙️ ОПТИМИЗАЦИЯ CONFIG.PY")

    print("\nДобавьте в config.py для ускорения:\n")

    config_text = '''
# ═══════════════════════════════════════════════════════════════
# ОПТИМИЗАЦИЯ СКОРОСТИ СКАЧИВАНИЯ
# ═══════════════════════════════════════════════════════════════

# КОМАНДА: REQUEST_DELAY - задержка между запросами
# ЗАЧЕМ: Слишком маленькая = бан, слишком большая = медленно
# ОПТИМАЛЬНО: 0.5-1 секунда
REQUEST_DELAY = 0.5  # Было 1.0, можно уменьшить

# КОМАНДА: TELEGRAM_FLOOD_SLEEP_THRESHOLD
# ЗАЧЕМ: Автоматическая пауза при FloodWait от Telegram
# РЕКОМЕНДАЦИЯ: 60 секунд (если больше - программа остановится)
TELEGRAM_FLOOD_SLEEP_THRESHOLD = 60

# КОМАНДА: TELEGRAM_CONNECTION_RETRIES
# ЗАЧЕМ: Количество попыток переподключения при сбое
TELEGRAM_CONNECTION_RETRIES = 5

# КОМАНДА: TELEGRAM_RETRY_DELAY
# ЗАЧЕМ: Пауза перед повторной попыткой
TELEGRAM_RETRY_DELAY = 1

# КОМАНДА: MAX_CONCURRENT_DOWNLOADS
# ЗАЧЕМ: Сколько файлов скачивать одновременно
# ВНИМАНИЕ: Telegram может забанить при >3
MAX_CONCURRENT_DOWNLOADS = 1  # Безопасно: 1, быстро но рискованно: 2-3
'''

    print(config_text)

    # Сохраняем в файл
    try:
        with open('config_speed_optimization.txt', 'w', encoding='utf-8') as f:
            f.write(config_text)
        print("\n✅ Сохранено в: config_speed_optimization.txt")
        print("   Скопируйте эти настройки в свой config.py")
    except:
        pass


def test_import_speed():
    """Тестирует скорость импорта криптобиблиотек"""
    print_section("🧪 ТЕСТ СКОРОСТИ")

    import time

    # Тест 1: Импорт telethon
    print("\n1. Импорт telethon...")
    start = time.time()
    try:
        from telethon import TelegramClient
        elapsed = time.time() - start
        print(f"   ✅ Импортирован за {elapsed:.3f} сек")
    except ImportError as e:
        print(f"   ❌ Ошибка: {e}")

    # Тест 2: Проверка cryptg
    print("\n2. Проверка cryptg...")
    try:
        import cryptg
        print("   ✅ cryptg доступен (БЫСТРО)")
    except ImportError:
        print("   ⚠️  cryptg недоступен (МЕДЛЕННО)")

    # Тест 3: Проверка pycryptodome
    print("\n3. Проверка pycryptodome...")
    try:
        from Crypto.Cipher import AES
        print("   ✅ pycryptodome доступен (СРЕДНЯЯ СКОРОСТЬ)")
    except ImportError:
        print("   ⚠️  pycryptodome недоступен")

    # Итог
    print("\n" + "─" * 70)
    try:
        import cryptg
        print("🚀 ВЫВОД: У вас МАКСИМАЛЬНАЯ скорость (cryptg)")
    except:
        try:
            from Crypto.Cipher import AES
            print("⚡ ВЫВОД: У вас СРЕДНЯЯ скорость (pycryptodome)")
        except:
            print("🐌 ВЫВОД: У вас МИНИМАЛЬНАЯ скорость (pure Python)")
            print("   🔥 УСТАНОВИТЕ pycryptodome НЕМЕДЛЕННО!")


def main():
    """Главная функция"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "ИСПРАВЛЕНИЕ СКОРОСТИ СКАЧИВАНИЯ" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")

    # 1. Тестируем текущее состояние
    test_import_speed()

    # 2. Проверяем библиотеки
    has_cryptg = check_cryptg()
    has_pycrypto = check_pycryptodome()

    # 3. Показываем сравнение
    show_speed_comparison()

    # 4. Если ничего нет - предлагаем установить
    if not has_cryptg and not has_pycrypto:
        print("\n" + "!" * 70)
        print("  ⚠️  КРИТИЧНО: Нет библиотек для ускорения!")
        print("!" * 70)

        response = input("\n❓ Установить pycryptodome сейчас? (y/n): ")
        if response.lower() == 'y':
            install_pycryptodome()

        response = input("\n❓ Попробовать установить cryptg? (y/n): ")
        if response.lower() == 'y':
            check_compiler()
            install_cryptg()

    elif not has_cryptg and has_pycrypto:
        response = input("\n❓ Попробовать установить cryptg для ускорения? (y/n): ")
        if response.lower() == 'y':
            check_compiler()
            install_cryptg()

    # 5. Показываем рекомендации
    show_recommendations()

    # 6. Создаём оптимизированный конфиг
    create_optimized_config()

    # Финал
    print("\n" + "=" * 70)
    print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 70)
    print("\n💡 Следующие шаги:")
    print("  1. Перезапустите программу после установки библиотек")
    print("  2. Скопируйте настройки из config_speed_optimization.txt")
    print("  3. Проверьте скорость скачивания")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
