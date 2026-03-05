#!/usr/bin/env python3
"""
Быстрый тест скорости шифрования
"""

import time

print("\n" + "=" * 70)
print("  ТЕСТ СКОРОСТИ ШИФРОВАНИЯ")
print("=" * 70 + "\n")

# Тест 1: Базовая криптография Python
print("1. Тест базовой криптографии (hashlib)...")
import hashlib
data = b"test data" * 10000
start = time.time()
for _ in range(1000):
    hashlib.sha256(data).digest()
base_time = time.time() - start
print(f"   Время: {base_time:.3f} сек")

# Тест 2: pycryptodome
print("\n2. Тест pycryptodome...")
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes

    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_EAX)

    start = time.time()
    for _ in range(1000):
        ciphertext, tag = cipher.encrypt_and_digest(data)
    pycrypto_time = time.time() - start

    print(f"   Время: {pycrypto_time:.3f} сек")
    print(f"   Ускорение: {base_time/pycrypto_time:.1f}x")
except ImportError:
    print("   ❌ pycryptodome не установлен")
    pycrypto_time = None

# Тест 3: cryptg
print("\n3. Тест cryptg...")
try:
    import cryptg
    print("   ✅ cryptg установлен")
    print("   🚀 Telethon будет работать на максимальной скорости!")
except ImportError:
    print("   ❌ cryptg не установлен")

print("\n" + "=" * 70)
print("  ИТОГОВАЯ КОНФИГУРАЦИЯ")
print("=" * 70 + "\n")

# Проверка всех библиотек
has_cryptg = False
has_pycrypto = False

try:
    import cryptg
    has_cryptg = True
    print("🚀 cryptg: УСТАНОВЛЕН")
except ImportError:
    print("❌ cryptg: не установлен")

try:
    from Crypto.Cipher import AES
    has_pycrypto = True
    print("⚡ pycryptodome: УСТАНОВЛЕН")
except ImportError:
    print("❌ pycryptodome: не установлен")

print("\n" + "-" * 70 + "\n")

if has_cryptg:
    print("🎉 РЕЗУЛЬТАТ: МАКСИМАЛЬНАЯ СКОРОСТЬ")
    print("   Telethon будет использовать cryptg")
    print("   Ожидаемая скорость: 1-2 МБ/с")
    print("   Ускорение: 10-20x от базовой скорости")
elif has_pycrypto:
    print("⚡ РЕЗУЛЬТАТ: СРЕДНЯЯ СКОРОСТЬ")
    print("   Telethon будет использовать pycryptodome")
    print("   Ожидаемая скорость: 200-500 КБ/с")
    print("   Ускорение: 3-5x от базовой скорости")
else:
    print("🐌 РЕЗУЛЬТАТ: МИНИМАЛЬНАЯ СКОРОСТЬ")
    print("   Telethon использует чистый Python")
    print("   Ожидаемая скорость: 50-100 КБ/с")
    print("   РЕКОМЕНДАЦИЯ: pip install pycryptodome")

print("\n" + "=" * 70 + "\n")
