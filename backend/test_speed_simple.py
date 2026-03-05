#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая проверка библиотек для ускорения
"""

print("\n" + "=" * 70)
print("  ПРОВЕРКА БИБЛИОТЕК УСКОРЕНИЯ")
print("=" * 70 + "\n")

# Проверка cryptg
print("1. Проверка cryptg...")
has_cryptg = False
try:
    import cryptg
    has_cryptg = True
    print("   [OK] cryptg установлен")
except ImportError:
    print("   [--] cryptg не установлен")

# Проверка pycryptodome
print("\n2. Проверка pycryptodome...")
has_pycrypto = False
try:
    from Crypto.Cipher import AES
    has_pycrypto = True
    print("   [OK] pycryptodome установлен")
except ImportError:
    print("   [--] pycryptodome не установлен")

# Итоговый результат
print("\n" + "=" * 70)
print("  ИТОГ")
print("=" * 70 + "\n")

if has_cryptg:
    print("STATUS: MAKSIMALNAYA SKOROST!")
    print("")
    print("Telethon budet ispolzovat cryptg")
    print("Ozhidaemaya skorost: 1-2 MB/s")
    print("Uskorenie: 10-20x ot bazovoy skorosti")
    print("")
    print("Eto LUCHSHAYA configuraciya!")
elif has_pycrypto:
    print("STATUS: SREDNYAYA SKOROST")
    print("")
    print("Telethon budet ispolzovat pycryptodome")
    print("Ozhidaemaya skorost: 200-500 KB/s")
    print("Uskorenie: 3-5x ot bazovoy skorosti")
    print("")
    print("Dlya uskore niya: pip install cryptg")
else:
    print("STATUS: MINIMALNAYA SKOROST")
    print("")
    print("Telethon ispolzuet chisty Python")
    print("Ozhidaemaya skorost: 50-100 KB/s")
    print("")
    print("REKOMENDACIYA: pip install pycryptodome")

print("\n" + "=" * 70 + "\n")
