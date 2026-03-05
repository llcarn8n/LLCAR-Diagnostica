# Ethernet-подключение: Ноутбук ↔ Рабочая станция

## Архитектура

```
┌─────────────────────┐    Ethernet CAT6    ┌──────────────────────────┐
│  НОУТБУК            │◄──────────────────►│  РАБОЧАЯ СТАНЦИЯ          │
│  192.168.50.1       │    120 МБ/с (1GbE)  │  192.168.50.2            │
│                     │                     │                          │
│  Claude Code        │  SSH (порт 22)      │  128 ГБ RAM              │
│  VS Code            │ ─────────────────►  │  2x RTX 3090 (48 ГБ)    │
└─────────────────────┘                     └──────────────────────────┘
```

## Задача

Подключиться к рабочей станции с GPU для запуска OCR 352 таблиц запчастей
через Qwen2.5-VL-7B → извлечение hotspot_id из каталога L9.

---

## Пошаговая настройка

### Шаг 1: Настроить IP на ноутбуке (от имени администратора)

```powershell
PowerShell -ExecutionPolicy Bypass -File "C:\Users\Петр\Downloads\scripts\infra\set-static-ip-laptop.ps1"
```
Результат: IP 192.168.50.1/24 на Ethernet-адаптере.

### Шаг 2: На рабочей станции

1. Скопировать папку `C:\Users\Петр\Downloads\scripts\infra\` на станцию (USB/сетевая папка)
2. Запустить от имени администратора:

```powershell
# Назначить IP
PowerShell -ExecutionPolicy Bypass -File set-static-ip-workstation.ps1

# Установить сервисы (OpenSSH, Python venv и др.)
PowerShell -ExecutionPolicy Bypass -File install-services-workstation.ps1
```

### Шаг 3: Настроить SSH на ноутбуке

```powershell
PowerShell -ExecutionPolicy Bypass -File "C:\Users\Петр\Downloads\scripts\infra\setup-mcp-ssh.ps1"
```
Создаст SSH-ключ, скопирует на станцию, настроит MCP SSH Manager.

### Шаг 4: Проверка

```powershell
ping 192.168.50.2
ssh llcar-ws "nvidia-smi"
ssh llcar-ws "python --version"
```

---

## Запуск OCR таблиц на рабочей станции

### Подготовка (на станции)

```bash
# Создать рабочую папку
mkdir -p D:\LLCAR\ocr-tables

# Скопировать с ноутбука (через SSH/SCP):
# 1. Скрипт OCR
scp llcar-ws:scripts/ocr_parts_tables.py D:\LLCAR\ocr-tables\

# 2. Изображения таблиц (352 файла)
scp -r llcar-ws:mineru-output/941362155-*/ocr/images/ D:\LLCAR\ocr-tables\images\

# 3. content_list.json (для маппинга page_idx)
scp llcar-ws:mineru-output/941362155-*/*_content_list.json D:\LLCAR\ocr-tables\

# 4. БД (для записи результатов)
scp llcar-ws:knowledge-base/kb.db D:\LLCAR\ocr-tables\
```

### Запуск OCR

```bash
cd D:\LLCAR\ocr-tables
python ocr_parts_tables.py
```

Ожидание: ~352 таблиц × 15 сек = ~1.5 часа на GPU.
Результат: таблица `parts` в kb.db с заполненными `hotspot_id`.

### Возврат результатов

```bash
# Скопировать обновлённую БД обратно на ноутбук
scp D:\LLCAR\ocr-tables\kb.db llcar-ws:knowledge-base/kb.db
```

---

## Скрипты (расположение)

| Скрипт | Путь |
|--------|------|
| IP ноутбука | `C:\Users\Петр\Downloads\scripts\infra\set-static-ip-laptop.ps1` |
| IP станции | `C:\Users\Петр\Downloads\scripts\infra\set-static-ip-workstation.ps1` |
| SSH + MCP | `C:\Users\Петр\Downloads\scripts\infra\setup-mcp-ssh.ps1` |
| Сервисы | `C:\Users\Петр\Downloads\scripts\infra\install-services-workstation.ps1` |
| OCR таблиц | `scripts/ocr_parts_tables.py` |

## Сетевые параметры

- Ноутбук: 192.168.50.1/24
- Станция: 192.168.50.2/24
- Шлюз: не нужен (прямое соединение)
- SSH Host alias: `llcar-ws`
- SSH ключ: `~/.ssh/llcar_workstation`
