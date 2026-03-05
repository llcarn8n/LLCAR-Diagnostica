
#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
        LLCAR WEB CONTROL PANEL v3 — ПОЛНЫЙ ФУНКЦИОНАЛ
═══════════════════════════════════════════════════════════════════════════════

ВОЗМОЖНОСТИ:
    ✅ Управление всеми 4 источниками (Telegram, Web, GitHub, Torrents)
    ✅ Просмотр файлов в Telegram-каналах БЕЗ скачивания
    ✅ Выбор и скачивание только нужных файлов
    ✅ Проверка целостности файлов
    ✅ Повторная проверка (recheck mode)
    ✅ Настройки конфигурации из интерфейса
    ✅ Просмотр скачанных файлов (файл-браузер)
    ✅ Статистика загрузок (по типам, по источникам)
    ✅ Прогресс-бар при скачивании
    ✅ Управление торрентами
    ✅ Редактирование фильтров (расширения, ключевые слова)
    ✅ Просмотр и скачивание логов
    ✅ Тёмная тема с неоновым дизайном
"""

import os
import sys
import json
import threading
import subprocess
import asyncio
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template_string, jsonify, request, send_file

# Импортируем config
import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 МБ


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response


# ═══════════════════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ═══════════════════════════════════════════════════════════════════════════

download_status = {
    'running': False,
    'phase': 'idle',  # idle, integrity_check, telegram, web, github, torrent, recheck, done
    'current_file': None,
    'progress': 0,
    'progress_total': 0,
    'speed': '',
    'eta': '',
    'stats': {
        'telegram': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
        'web': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
        'github': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
        'torrent': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
    },
    'integrity': {
        'total_checked': 0,
        'complete': 0,
        'incomplete': 0,
        'missing': 0,
    },
    'logs': [],
    'start_time': None,
    'end_time': None,
}

current_process = None
telegram_downloader = None

CUSTOM_SOURCES_FILE = Path('custom_sources.json')
WEB_CONFIG_FILE = Path('web_config.json')


# ═══════════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════

def format_size(size_bytes):
    """Форматирует размер файла"""
    if size_bytes == 0:
        return '0 Б'
    for unit in ('Б', 'КБ', 'МБ', 'ГБ', 'ТБ'):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} ПБ"


def format_duration(seconds):
    """Форматирует длительность"""
    if seconds < 60:
        return f"{int(seconds)} сек"
    elif seconds < 3600:
        return f"{int(seconds // 60)} мин {int(seconds % 60)} сек"
    else:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h} ч {m} мин"


def add_log(message, level='info'):
    """Добавить запись в лог"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'download': '📥',
        'progress': '🔄',
    }.get(level, 'ℹ️')

    entry = f'{timestamp} {prefix} {message}'
    download_status['logs'].append(entry)

    # Ограничиваем логи
    if len(download_status['logs']) > 500:
        download_status['logs'] = download_status['logs'][-500:]


# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

def load_web_config():
    """Загрузить веб-конфигурацию"""
    defaults = {
        'telegram_enabled': True,
        'web_enabled': True,
        'github_enabled': True,
        'torrent_enabled': False,
        'recheck_mode': True,
        'integrity_check': True,
        'max_file_size_mb': getattr(config, 'MAX_FILE_SIZE_MB', 500),
        'message_limit': getattr(config, 'TELEGRAM_MESSAGE_LIMIT', 1000),
        'allowed_extensions': list(getattr(config, 'ALLOWED_EXTENSIONS', [])),
        'keywords_include': list(getattr(config, 'KEYWORDS_INCLUDE', [])),
        'keywords_exclude': list(getattr(config, 'KEYWORDS_EXCLUDE', [])),
        'request_delay': getattr(config, 'REQUEST_DELAY', 2),
        'download_path': str(getattr(config, 'BASE_DOWNLOAD_PATH', './downloads')),
    }

    if WEB_CONFIG_FILE.exists():
        try:
            with open(WEB_CONFIG_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass

    return defaults


def save_web_config(cfg):
    """Сохранить веб-конфигурацию"""
    with open(WEB_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# ПОЛЬЗОВАТЕЛЬСКИЕ ИСТОЧНИКИ
# ═══════════════════════════════════════════════════════════════════════════

def load_custom_sources():
    if not CUSTOM_SOURCES_FILE.exists():
        return {'telegram': [], 'web': [], 'github': [], 'torrent': []}
    try:
        with open(CUSTOM_SOURCES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Гарантируем все ключи
            for key in ('telegram', 'web', 'github', 'torrent'):
                if key not in data:
                    data[key] = []
            return data
    except Exception:
        return {'telegram': [], 'web': [], 'github': [], 'torrent': []}


def save_custom_sources(custom_sources):
    with open(CUSTOM_SOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(custom_sources, f, ensure_ascii=False, indent=2)


def add_custom_source(source_type, source_data):
    custom = load_custom_sources()
    custom[source_type].append(source_data)
    save_custom_sources(custom)
    return True


def delete_custom_source(source_type, source_id):
    custom = load_custom_sources()
    if source_type == 'telegram':
        custom['telegram'] = [s for s in custom['telegram'] if s != source_id]
    elif source_type == 'web':
        custom['web'] = [s for s in custom['web'] if s.get('id') != source_id]
    elif source_type == 'github':
        custom['github'] = [s for s in custom['github'] if s.get('url') != source_id]
    elif source_type == 'torrent':
        custom['torrent'] = [s for s in custom['torrent'] if s.get('query') != source_id]
    save_custom_sources(custom)
    return True


# ═══════════════════════════════════════════════════════════════════════════
# TELEGRAM DOWNLOADER
# ═══════════════════════════════════════════════════════════════════════════

def init_telegram_downloader():
    global telegram_downloader
    if telegram_downloader is not None:
        return telegram_downloader

    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH or not config.TELEGRAM_PHONE:
        return None

    try:
        from downloaders.telegram_downloader import TelegramDownloader
        telegram_downloader = TelegramDownloader(
            api_id=config.TELEGRAM_API_ID,
            api_hash=config.TELEGRAM_API_HASH,
            phone=config.TELEGRAM_PHONE,
            download_path=config.BASE_DOWNLOAD_PATH / '_telegram_raw',
        )
        return telegram_downloader
    except Exception as e:
        print(f"Ошибка инициализации TelegramDownloader: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


# ---------- SOURCES ----------

@app.route('/api/sources')
def get_sources():
    """Получить список всех источников"""
    custom = load_custom_sources()

    # Telegram
    telegram_sources = [
        {'id': ch, 'name': f'@{ch}', 'enabled': True, 'custom': False}
        for ch in config.TELEGRAM_CHANNELS
    ]
    telegram_sources += [
        {'id': ch, 'name': f'@{ch} (custom)', 'enabled': True, 'custom': True}
        for ch in custom.get('telegram', [])
    ]

    # Web
    web_sources = []
    for key, data in getattr(config, 'WEB_SOURCES', {}).items():
        web_sources.append({
            'id': key,
            'name': f'{key} — {data.get("base_url", "N/A")}',
            'url': data.get('base_url', ''),
            'enabled': data.get('enabled', True),
            'custom': False,
        })
    web_sources += [
        {
            'id': src['id'],
            'name': f'{src["id"]} — {src["url"]} (custom)',
            'url': src['url'],
            'enabled': True,
            'custom': True,
        }
        for src in custom.get('web', [])
    ]

    # GitHub
    github_sources = [
        {
            'id': src['url'],
            'name': f'{src["url"]}' + (f' ({src.get("description", "")})' if src.get('description') else ''),
            'path': src.get('path', ''),
            'enabled': src.get('enabled', True),
            'custom': False,
        }
        for src in getattr(config, 'GITHUB_SOURCES', [])
    ]
    github_sources += [
        {
            'id': src['url'],
            'name': f'{src["url"]} (custom)',
            'path': src.get('path', ''),
            'enabled': True,
            'custom': True,
        }
        for src in custom.get('github', [])
    ]

    # Torrent
    torrent_sources = []
    if getattr(config, 'TORRENT_ENABLED', False):
        for query in getattr(config, 'RUTRACKER_SEARCH_QUERIES', []):
            torrent_sources.append({
                'id': query,
                'name': f'🔍 "{query}"',
                'enabled': True,
                'custom': False,
            })
    torrent_sources += [
        {
            'id': src['query'],
            'name': f'🔍 "{src["query"]}" (custom)',
            'enabled': True,
            'custom': True,
        }
        for src in custom.get('torrent', [])
    ]

    return jsonify({
        'telegram': telegram_sources,
        'web': web_sources,
        'github': github_sources,
        'torrent': torrent_sources,
    })


@app.route('/api/sources/add', methods=['POST'])
def api_add_source():
    try:
        data = request.json
        source_type = data.get('type')
        source_data = data.get('data')

        if source_type == 'telegram':
            channel_name = source_data.get('name', '').strip().lstrip('@')
            if not channel_name:
                return jsonify({'success': False, 'error': 'Имя канала не может быть пустым'})
            add_custom_source('telegram', channel_name)

        elif source_type == 'web':
            source_id = source_data.get('id', '').strip()
            url = source_data.get('url', '').strip()
            if not source_id or not url:
                return jsonify({'success': False, 'error': 'ID и URL обязательны'})
            add_custom_source('web', {
                'id': source_id,
                'url': url,
                'enabled': True,
                'encoding': source_data.get('encoding', ''),
                'max_pages': int(source_data.get('max_pages', 10)),
            })

        elif source_type == 'github':
            url = source_data.get('url', '').strip()
            if not url:
                return jsonify({'success': False, 'error': 'URL репозитория обязателен'})
            add_custom_source('github', {
                'enabled': True,
                'url': url,
                'path': source_data.get('path', ''),
                'description': source_data.get('description', ''),
            })

        elif source_type == 'torrent':
            query = source_data.get('query', '').strip()
            if not query:
                return jsonify({'success': False, 'error': 'Поисковый запрос обязателен'})
            add_custom_source('torrent', {
                'query': query,
                'max_results': int(source_data.get('max_results', 10)),
                'min_seeds': int(source_data.get('min_seeds', 1)),
            })

        else:
            return jsonify({'success': False, 'error': 'Неизвестный тип источника'})

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sources/delete', methods=['POST'])
def api_delete_source():
    try:
        data = request.json
        delete_custom_source(data.get('type'), data.get('id'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ---------- CONFIGURATION ----------

@app.route('/api/config', methods=['GET'])
def api_get_config():
    return jsonify(load_web_config())


@app.route('/api/config', methods=['POST'])
def api_update_config():
    try:
        cfg = request.json
        save_web_config(cfg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ---------- STATUS ----------

@app.route('/api/status')
def api_get_status():
    result = dict(download_status)

    # Вычисляем uptime
    if result.get('start_time'):
        elapsed = (datetime.now() - datetime.fromisoformat(result['start_time'])).total_seconds()
        result['elapsed'] = format_duration(elapsed)
    else:
        result['elapsed'] = '—'

    return jsonify(result)


# ---------- STATISTICS ----------

@app.route('/api/statistics')
def api_get_statistics():
    try:
        stats = {
            'total_files': 0,
            'total_size': 0,
            'total_size_str': '0 Б',
            'by_extension': [],
            'by_folder': [],
            'recent_files': [],
        }

        download_path = config.BASE_DOWNLOAD_PATH
        if not download_path.exists():
            return jsonify(stats)

        ext_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        folder_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        recent = []

        for filepath in download_path.rglob('*'):
            if filepath.is_file():
                stats['total_files'] += 1
                size = filepath.stat().st_size
                mtime = filepath.stat().st_mtime
                stats['total_size'] += size

                ext = filepath.suffix.lower() or '(без расширения)'
                ext_stats[ext]['count'] += 1
                ext_stats[ext]['size'] += size

                # Относительная папка (первый уровень)
                try:
                    rel = filepath.relative_to(download_path)
                    folder = rel.parts[0] if len(rel.parts) > 1 else '(корень)'
                except ValueError:
                    folder = '(другое)'

                folder_stats[folder]['count'] += 1
                folder_stats[folder]['size'] += size

                # Последние файлы
                recent.append({
                    'name': filepath.name,
                    'size': format_size(size),
                    'folder': folder,
                    'modified': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M'),
                    'mtime': mtime,
                })

        stats['total_size_str'] = format_size(stats['total_size'])

        # По расширениям
        stats['by_extension'] = sorted(
            [{'ext': k, 'count': v['count'], 'size_str': format_size(v['size']), 'size': v['size']}
             for k, v in ext_stats.items()],
            key=lambda x: x['count'], reverse=True
        )[:20]

        # По папкам
        stats['by_folder'] = sorted(
            [{'folder': k, 'count': v['count'], 'size_str': format_size(v['size']), 'size': v['size']}
             for k, v in folder_stats.items()],
            key=lambda x: x['count'], reverse=True
        )[:20]

        # Последние 20 файлов
        recent.sort(key=lambda x: x['mtime'], reverse=True)
        stats['recent_files'] = recent[:20]
        for r in stats['recent_files']:
            del r['mtime']

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)})


# ---------- FILE BROWSER ----------

@app.route('/api/files')
def api_browse_files():
    """Файловый браузер скачанных файлов"""
    try:
        rel_path = request.args.get('path', '')
        base = config.BASE_DOWNLOAD_PATH
        target = (base / rel_path).resolve()

        # Проверка безопасности — не выходим за пределы base
        if not str(target).startswith(str(base.resolve())):
            return jsonify({'success': False, 'error': 'Доступ запрещён'})

        if not target.exists():
            return jsonify({'success': False, 'error': 'Путь не найден'})

        items = []
        if target.is_dir():
            for item in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                entry = {
                    'name': item.name,
                    'is_dir': item.is_dir(),
                    'path': str(item.relative_to(base)),
                }
                if item.is_file():
                    stat = item.stat()
                    entry['size'] = stat.st_size
                    entry['size_str'] = format_size(stat.st_size)
                    entry['modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    entry['extension'] = item.suffix.lower()
                elif item.is_dir():
                    # Подсчёт файлов в директории
                    try:
                        count = sum(1 for _ in item.rglob('*') if _.is_file())
                        entry['file_count'] = count
                    except Exception:
                        entry['file_count'] = 0

                items.append(entry)

        # Хлебные крошки
        breadcrumbs = [{'name': '📁 Корень', 'path': ''}]
        if rel_path:
            parts = Path(rel_path).parts
            for i, part in enumerate(parts):
                breadcrumbs.append({
                    'name': part,
                    'path': str(Path(*parts[:i + 1])),
                })

        return jsonify({
            'success': True,
            'path': rel_path,
            'breadcrumbs': breadcrumbs,
            'items': items,
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/files/download')
def api_download_file():
    """Скачать конкретный файл"""
    try:
        rel_path = request.args.get('path', '')
        base = config.BASE_DOWNLOAD_PATH
        target = (base / rel_path).resolve()

        if not str(target).startswith(str(base.resolve())):
            return jsonify({'success': False, 'error': 'Доступ запрещён'})

        if not target.is_file():
            return jsonify({'success': False, 'error': 'Файл не найден'})

        return send_file(target, as_attachment=True)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/files/delete', methods=['POST'])
def api_delete_file():
    """Удалить файл или папку"""
    try:
        data = request.json
        rel_path = data.get('path', '')
        base = config.BASE_DOWNLOAD_PATH
        target = (base / rel_path).resolve()

        if not str(target).startswith(str(base.resolve())):
            return jsonify({'success': False, 'error': 'Доступ запрещён'})

        if target == base.resolve():
            return jsonify({'success': False, 'error': 'Нельзя удалить корневую папку'})

        if target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)
        else:
            return jsonify({'success': False, 'error': 'Объект не найден'})

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ---------- TELEGRAM BROWSE ----------

@app.route('/api/telegram/browse/<channel>')
def api_browse_telegram(channel):
    """Просмотр файлов в Telegram-канале"""
    dl = init_telegram_downloader()
    if not dl:
        return jsonify({'success': False, 'error': 'Telegram не настроен'})

    async def _browse():
        try:
            if not dl.client or not dl.client.is_connected():
                connected = await dl.connect()
                if not connected:
                    return {'success': False, 'error': 'Не удалось подключиться к Telegram'}

            files = await dl.list_channel_files(
                channel_username=channel,
                allowed_extensions=config.ALLOWED_EXTENSIONS,
                max_size_mb=config.MAX_FILE_SIZE_MB,
                message_limit=config.TELEGRAM_MESSAGE_LIMIT,
            )

            files_data = []
            for f in files:
                files_data.append({
                    'message_id': f.message_id,
                    'filename': f.filename,
                    'size': f.size,
                    'size_str': f.size_str,
                    'extension': f.extension,
                    'date': f.date.isoformat() if f.date else None,
                    'is_downloaded': f.is_downloaded,
                    'caption': getattr(f, 'caption', '') or '',
                })

            total_new = sum(1 for f in files_data if not f['is_downloaded'])
            total_size = sum(f['size'] for f in files_data if not f['is_downloaded'])

            return {
                'success': True,
                'files': files_data,
                'total': len(files_data),
                'new_count': total_new,
                'new_size': format_size(total_size),
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_browse())
        loop.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка: {str(e)}'})


@app.route('/api/telegram/download_selected', methods=['POST'])
def api_download_selected():
    """Скачивание выбранных файлов из Telegram-канала"""
    data = request.json
    channel = data.get('channel')
    message_ids = data.get('message_ids', [])

    if not channel or not message_ids:
        return jsonify({'success': False, 'error': 'Не указан канал или файлы'})

    thread = threading.Thread(
        target=_run_download_selected,
        args=(channel, message_ids),
        daemon=True
    )
    thread.start()

    download_status['running'] = True
    download_status['phase'] = 'telegram'
    download_status['start_time'] = datetime.now().isoformat()
    add_log(f'Скачивание {len(message_ids)} файлов из @{channel}', 'download')

    return jsonify({'success': True})


def _run_download_selected(channel, message_ids):
    async def _download():
        try:
            dl = init_telegram_downloader()
            if not dl:
                add_log('Telegram не настроен', 'error')
                return

            if not dl.client or not dl.client.is_connected():
                connected = await dl.connect()
                if not connected:
                    add_log('Не удалось подключиться к Telegram', 'error')
                    return

            downloaded_count = 0

            def progress_cb(filename, bytes_dl, total_bytes):
                if total_bytes > 0:
                    pct = int(bytes_dl / total_bytes * 100)
                    download_status['current_file'] = filename
                    download_status['progress'] = pct

            results = await dl.download_selected_files(
                channel_username=channel,
                message_ids=message_ids,
                progress_callback=progress_cb,
            )

            downloaded_count = len(results) if results else 0

            # Организуем скачанные файлы
            try:
                from utils.file_organizer import FileOrganizer
                organizer = FileOrganizer(config.BASE_DOWNLOAD_PATH)

                for downloaded_file in (results or []):
                    try:
                        organizer.organize_file(
                            source_path=downloaded_file['filepath'],
                            filename=downloaded_file['filename'],
                            description=downloaded_file.get('caption', ''),
                        )
                    except Exception as e:
                        add_log(f'Ошибка сортировки {downloaded_file["filename"]}: {e}', 'warning')
            except ImportError:
                add_log('FileOrganizer не найден, файлы в _telegram_raw', 'warning')

            add_log(f'Скачано: {downloaded_count} файлов', 'success')

            download_status['stats']['telegram']['downloaded'] += downloaded_count

        except Exception as e:
            add_log(f'Ошибка: {e}', 'error')
        finally:
            download_status['running'] = False
            download_status['phase'] = 'done'
            download_status['current_file'] = None
            download_status['progress'] = 0
            download_status['end_time'] = datetime.now().isoformat()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_download())
        loop.close()
    except Exception as e:
        add_log(f'Критическая ошибка: {e}', 'error')
        download_status['running'] = False


# ---------- MAIN DOWNLOAD ----------

@app.route('/api/start', methods=['POST'])
def api_start_download():
    """Запустить полную загрузку"""
    global current_process

    if download_status['running']:
        return jsonify({'success': False, 'error': 'Уже запущено'})

    selected = request.json
    web_cfg = load_web_config()

    # Создаём временный конфиг для main_v2.py
    temp_config = {
        'telegram': selected.get('telegram', []),
        'web': selected.get('web', []),
        'github': selected.get('github', []),
        'torrent': selected.get('torrent', []),
    }

    with open('temp_config.json', 'w', encoding='utf-8') as f:
        json.dump(temp_config, f, ensure_ascii=False, indent=2)

    # Сброс статистики
    download_status['running'] = True
    download_status['phase'] = 'starting'
    download_status['current_file'] = None
    download_status['progress'] = 0
    download_status['start_time'] = datetime.now().isoformat()
    download_status['end_time'] = None
    download_status['logs'] = [f'{datetime.now().strftime("%H:%M:%S")} ℹ️ Загрузка запущена']
    download_status['stats'] = {
        'telegram': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
        'web': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
        'github': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
        'torrent': {'downloaded': 0, 'skipped': 0, 'errors': 0, 'size': 0},
    }
    download_status['integrity'] = {
        'total_checked': 0, 'complete': 0, 'incomplete': 0, 'missing': 0,
    }

    thread = threading.Thread(target=_run_download_process, daemon=True)
    thread.start()

    return jsonify({'success': True})


@app.route('/api/stop', methods=['POST'])
def api_stop_download():
    global current_process

    if current_process:
        current_process.terminate()
        current_process = None

    download_status['running'] = False
    download_status['phase'] = 'stopped'
    download_status['end_time'] = datetime.now().isoformat()
    add_log('Загрузка остановлена пользователем', 'warning')

    return jsonify({'success': True})


# ---------- INTEGRITY CHECK ----------

@app.route('/api/integrity/check', methods=['POST'])
def api_integrity_check():
    """Запустить проверку целостности файлов"""
    if download_status['running']:
        return jsonify({'success': False, 'error': 'Дождитесь завершения текущей операции'})

    thread = threading.Thread(target=_run_integrity_check, daemon=True)
    thread.start()

    download_status['running'] = True
    download_status['phase'] = 'integrity_check'
    add_log('Запуск проверки целостности файлов...', 'progress')

    return jsonify({'success': True})


def _run_integrity_check():
    """Проверка целостности в фоне"""
    try:
        from utils.file_tracker import FileTracker

        tracker = FileTracker(db_path=Path('./data/files_tracker.db'))
        tracker_stats = tracker.get_stats()

        download_status['integrity']['total_checked'] = tracker_stats.get('total', 0)
        download_status['integrity']['complete'] = tracker_stats.get('complete', 0)

        incomplete = tracker.get_incomplete_files()
        download_status['integrity']['incomplete'] = len(incomplete)

        missing = tracker.get_missing_files()
        download_status['integrity']['missing'] = len(missing)

        for file_info in incomplete:
            tracker.mark_for_redownload(file_info['id'])
            add_log(f'Помечен для повторного скачивания: {file_info["filename"]}', 'warning')

        for file_info in missing:
            add_log(f'Файл исчез с диска: {file_info["filename"]}', 'error')

        if len(incomplete) == 0 and len(missing) == 0:
            add_log(f'Все {tracker_stats.get("total", 0)} файлов в порядке!', 'success')
        else:
            add_log(
                f'Проверено: {tracker_stats.get("total", 0)}, '
                f'Неполных: {len(incomplete)}, '
                f'Отсутствующих: {len(missing)}',
                'warning'
            )

        tracker.close()

    except ImportError:
        add_log('Модуль FileTracker не найден', 'error')
    except Exception as e:
        add_log(f'Ошибка проверки целостности: {e}', 'error')
    finally:
        download_status['running'] = False
        download_status['phase'] = 'done'


# ---------- LOGS ----------

@app.route('/api/logs')
def api_get_logs():
    """Получить файлы логов"""
    log_dir = Path('./logs')
    if not log_dir.exists():
        return jsonify({'logs': []})

    log_files = []
    for f in sorted(log_dir.glob('*.log'), reverse=True):
        log_files.append({
            'name': f.name,
            'size': format_size(f.stat().st_size),
            'modified': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
        })

    return jsonify({'logs': log_files[:20]})


@app.route('/api/logs/download/<filename>')
def api_download_log(filename):
    """Скачать конкретный лог-файл"""
    log_path = Path('./logs') / filename
    if not log_path.exists() or not log_path.is_file():
        return jsonify({'error': 'Файл не найден'}), 404
    return send_file(log_path, as_attachment=True)


@app.route('/api/logs/view/<filename>')
def api_view_log(filename):
    """Просмотреть содержимое лог-файла"""
    log_path = Path('./logs') / filename
    if not log_path.exists() or not log_path.is_file():
        return jsonify({'error': 'Файл не найден'}), 404

    try:
        # Читаем последние 200 строк
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        return jsonify({
            'filename': filename,
            'lines': [line.rstrip() for line in lines[-200:]],
            'total_lines': len(lines),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- SYSTEM INFO ----------

@app.route('/api/system')
def api_system_info():
    """Информация о системе"""
    try:
        disk = shutil.disk_usage(str(config.BASE_DOWNLOAD_PATH))

        # Проверяем наличие модулей
        modules = {}
        for mod_name in ('telethon', 'aiohttp', 'bs4', 'aiofiles', 'cryptg'):
            try:
                __import__(mod_name)
                modules[mod_name] = True
            except ImportError:
                modules[mod_name] = False

        # Проверяем pycryptodome
        try:
            from Crypto.Cipher import AES  # noqa
            modules['pycryptodome'] = True
        except ImportError:
            modules['pycryptodome'] = False

        return jsonify({
            'python_version': sys.version,
            'platform': sys.platform,
            'download_path': str(config.BASE_DOWNLOAD_PATH.absolute()),
            'disk_total': format_size(disk.total),
            'disk_used': format_size(disk.used),
            'disk_free': format_size(disk.free),
            'disk_percent': round(disk.used / disk.total * 100, 1),
            'modules': modules,
            'telegram_configured': bool(config.TELEGRAM_API_ID and config.TELEGRAM_API_HASH),
            'torrent_configured': getattr(config, 'TORRENT_ENABLED', False),
        })
    except Exception as e:
        return jsonify({'error': str(e)})


# ═══════════════════════════════════════════════════════════════════════════
# ФОНОВЫЙ ПРОЦЕСС ЗАГРУЗКИ
# ═══════════════════════════════════════════════════════════════════════════

def _run_download_process():
    """Запуск main_v2.py как subprocess"""
    global current_process

    try:
        cmd = [sys.executable, '-X', 'utf8', 'main_v2.py', '--use-temp-config']

        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
        )

        for line in iter(current_process.stdout.readline, ''):
            if not download_status['running']:
                break

            line = line.strip()
            if not line:
                continue

            # Определяем фазу по ключевым словам
            if 'ПРОВЕРКА ЦЕЛОСТНОСТИ' in line:
                download_status['phase'] = 'integrity_check'
            elif 'СКАЧИВАНИЕ ИЗ TELEGRAM' in line:
                download_status['phase'] = 'telegram'
            elif 'СКАЧИВАНИЕ С ВЕБ-САЙТОВ' in line:
                download_status['phase'] = 'web'
            elif 'СКАЧИВАНИЕ С GITHUB' in line:
                download_status['phase'] = 'github'
            elif 'СКАЧИВАНИЕ ТОРРЕНТОВ' in line:
                download_status['phase'] = 'torrent'
            elif 'ПОВТОРНАЯ ПРОВЕРКА' in line:
                download_status['phase'] = 'recheck'

            # Парсим текущий файл
            if '📄' in line or '📥' in line:
                parts = line.split('📄' if '📄' in line else '📥')
                if len(parts) > 1:
                    download_status['current_file'] = parts[1].strip()[:80]

            # Парсим статистику из вывода
            if 'Файлов скачано:' in line:
                try:
                    count = int(line.split('Файлов скачано:')[1].strip().split()[0])
                    phase = download_status['phase']
                    if phase in download_status['stats']:
                        download_status['stats'][phase]['downloaded'] = count
                except (ValueError, IndexError):
                    pass

            # Добавляем в лог
            download_status['logs'].append(
                f'{datetime.now().strftime("%H:%M:%S")} - {line}'
            )

            if len(download_status['logs']) > 500:
                download_status['logs'] = download_status['logs'][-500:]

        current_process.wait()
        download_status['phase'] = 'done'
        add_log('Загрузка завершена', 'success')

    except Exception as e:
        add_log(f'Ошибка процесса: {e}', 'error')

    finally:
        download_status['running'] = False
        download_status['current_file'] = None
        download_status['end_time'] = datetime.now().isoformat()
        current_process = None


# ═══════════════════════════════════════════════════════════════════════════
# HTML TEMPLATE — ПОЛНЫЙ ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════════════════

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLCAR Control Panel v3</title>
    <style>
        :root {
            --cyan: #00FFFF;
            --cyan-dim: #00CCCC;
            --cyan-bg: rgba(0, 255, 255, 0.05);
            --cyan-border: rgba(0, 255, 255, 0.3);
            --green: #00FF50;
            --red: #FF0050;
            --orange: #FF8800;
            --purple: #AA00FF;
            --bg: #000;
            --bg-card: rgba(10, 10, 10, 0.8);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #000 0%, #050510 50%, #0a0a0a 100%);
            color: var(--cyan);
            min-height: 100vh;
        }

        /* ── NAVBAR ─────────────────────────────────────────── */
        .navbar {
            background: rgba(0, 0, 0, 0.9);
            border-bottom: 2px solid var(--cyan);
            padding: 15px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .navbar-brand {
            font-size: 1.6em;
            font-weight: bold;
            text-shadow: 0 0 15px var(--cyan);
        }

        .navbar-tabs {
            display: flex;
            gap: 5px;
        }

        .nav-tab {
            padding: 10px 20px;
            background: transparent;
            border: 2px solid transparent;
            border-radius: 8px 8px 0 0;
            color: var(--cyan-dim);
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.3s;
        }

        .nav-tab:hover {
            background: var(--cyan-bg);
            border-color: var(--cyan-border);
        }

        .nav-tab.active {
            background: var(--cyan-bg);
            border-color: var(--cyan);
            color: var(--cyan);
            font-weight: bold;
            text-shadow: 0 0 10px var(--cyan);
        }

        .navbar-status {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #333;
        }

        .status-dot.idle { background: #666; }
        .status-dot.running { background: var(--green); animation: pulse 1s infinite; }
        .status-dot.error { background: var(--red); }

        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 5px var(--green); }
            50% { opacity: 0.5; box-shadow: 0 0 15px var(--green); }
        }

        /* ── PAGES (TABS) ─────────────────────────────────── */
        .page {
            display: none;
            padding: 25px;
            max-width: 1600px;
            margin: 0 auto;
        }

        .page.active { display: block; }

        /* ── CARDS ─────────────────────────────────────────── */
        .card {
            background: var(--bg-card);
            border: 2px solid var(--cyan-border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }

        .card:hover { border-color: var(--cyan); }

        .card-title {
            font-size: 1.4em;
            color: var(--cyan);
            margin-bottom: 15px;
            text-shadow: 0 0 8px var(--cyan);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* ── GRID ──────────────────────────────────────────── */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }

        @media (max-width: 1200px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
            .grid-3 { grid-template-columns: 1fr 1fr; }
        }

        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
            .navbar { flex-direction: column; gap: 10px; }
            .navbar-tabs { flex-wrap: wrap; justify-content: center; }
        }

        /* ── SOURCE ITEMS ──────────────────────────────────── */
        .source-item {
            background: var(--cyan-bg);
            border: 1px solid var(--cyan-border);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .source-item:hover {
            background: rgba(0, 255, 255, 0.1);
            border-color: var(--cyan);
        }

        .source-item.checked {
            background: rgba(0, 255, 255, 0.15);
            border-color: var(--cyan);
        }

        .source-item.checked label {
            color: var(--cyan);
            font-weight: bold;
        }

        .source-item input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: var(--cyan);
        }

        .source-item label {
            flex: 1;
            cursor: pointer;
            color: var(--cyan-dim);
            font-size: 0.95em;
            word-break: break-all;
        }

        /* ── BUTTONS ───────────────────────────────────────── */
        .btn {
            padding: 12px 24px;
            font-size: 1em;
            border: 2px solid var(--cyan);
            background: rgba(0, 255, 255, 0.1);
            color: var(--cyan);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }

        .btn:hover:not(:disabled) {
            background: rgba(0, 255, 255, 0.2);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
            transform: translateY(-1px);
        }

        .btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        .btn-large {
            padding: 16px 32px;
            font-size: 1.2em;
            width: 100%;
        }

        .btn-green {
            border-color: var(--green);
            color: var(--green);
            background: rgba(0, 255, 80, 0.1);
        }

        .btn-green:hover:not(:disabled) {
            background: rgba(0, 255, 80, 0.2);
            box-shadow: 0 0 20px rgba(0, 255, 80, 0.4);
        }

        .btn-red {
            border-color: var(--red);
            color: var(--red);
            background: rgba(255, 0, 80, 0.1);
        }

        .btn-red:hover:not(:disabled) {
            background: rgba(255, 0, 80, 0.2);
            box-shadow: 0 0 20px rgba(255, 0, 80, 0.4);
        }

        .btn-orange {
            border-color: var(--orange);
            color: var(--orange);
            background: rgba(255, 136, 0, 0.1);
        }

        .btn-orange:hover:not(:disabled) {
            background: rgba(255, 136, 0, 0.2);
            box-shadow: 0 0 20px rgba(255, 136, 0, 0.4);
        }

        .btn-purple {
            border-color: var(--purple);
            color: var(--purple);
            background: rgba(170, 0, 255, 0.1);
        }

        .btn-small {
            padding: 6px 14px;
            font-size: 0.85em;
        }

        .btn-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .btn-group .btn { flex: 1; min-width: 200px; }

        .add-source-btn {
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            background: rgba(0, 255, 80, 0.05);
            border: 2px dashed var(--green);
            color: var(--green);
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }

        .add-source-btn:hover {
            background: rgba(0, 255, 80, 0.15);
            box-shadow: 0 0 15px rgba(0, 255, 80, 0.3);
        }

        .select-all-btn {
            padding: 8px 16px;
            margin-bottom: 12px;
            background: var(--cyan-bg);
            border: 1px solid var(--cyan);
            border-radius: 6px;
            color: var(--cyan);
            cursor: pointer;
            font-size: 0.9em;
            display: inline-block;
        }

        .select-all-btn:hover { background: rgba(0, 255, 255, 0.15); }

        .browse-btn {
            padding: 5px 12px;
            background: rgba(0, 255, 80, 0.15);
            border: 1px solid var(--green);
            color: var(--green);
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.3s;
            white-space: nowrap;
        }

        .browse-btn:hover {
            background: rgba(0, 255, 80, 0.3);
        }

        .delete-btn {
            padding: 5px 12px;
            background: rgba(255, 0, 80, 0.15);
            border: 1px solid var(--red);
            color: var(--red);
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85em;
        }

        .delete-btn:hover { background: rgba(255, 0, 80, 0.3); }

        /* ── STATUS BAR ────────────────────────────────────── */
        .status-bar {
            background: var(--cyan-bg);
            border: 2px solid var(--cyan-border);
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
            flex-wrap: wrap;
        }

        .status-bar.running {
            border-color: var(--green);
            animation: glowGreen 2s infinite;
        }

        @keyframes glowGreen {
            0%, 100% { box-shadow: 0 0 10px rgba(0, 255, 80, 0.2); }
            50% { box-shadow: 0 0 25px rgba(0, 255, 80, 0.5); }
        }

        .status-text { font-size: 1.1em; }
        .status-phase {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .phase-idle { background: rgba(100,100,100,0.3); color: #888; }
        .phase-integrity_check { background: rgba(170,0,255,0.2); color: var(--purple); }
        .phase-telegram { background: rgba(0,136,255,0.2); color: #0088FF; }
        .phase-web { background: rgba(0,255,80,0.2); color: var(--green); }
        .phase-github { background: rgba(255,255,255,0.15); color: #fff; }
        .phase-torrent { background: rgba(255,136,0,0.2); color: var(--orange); }
        .phase-recheck { background: rgba(0,255,255,0.2); color: var(--cyan); }
        .phase-done { background: rgba(0,255,80,0.3); color: var(--green); }
        .phase-stopped { background: rgba(255,0,80,0.2); color: var(--red); }
        .phase-starting { background: rgba(0,255,255,0.2); color: var(--cyan); }

        /* ── PROGRESS BAR ──────────────────────────────────── */
        .progress-container {
            width: 100%;
            height: 6px;
            background: rgba(0,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--cyan), var(--green));
            border-radius: 3px;
            transition: width 0.3s;
            width: 0%;
        }

        .current-file-display {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: var(--cyan-dim);
            padding: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* ── STATS GRID ────────────────────────────────────── */
        .stat-card {
            background: var(--cyan-bg);
            border: 1px solid var(--cyan-border);
            border-radius: 8px;
            padding: 18px;
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--cyan);
            text-shadow: 0 0 10px rgba(0,255,255,0.5);
        }

        .stat-label {
            color: var(--cyan-dim);
            margin-top: 5px;
            font-size: 0.9em;
        }

        /* ── TABLE ─────────────────────────────────────────── */
        .table-container {
            overflow-x: auto;
            border: 1px solid var(--cyan-border);
            border-radius: 8px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead {
            background: rgba(0,255,255,0.15);
            position: sticky;
            top: 0;
        }

        th {
            padding: 12px 10px;
            text-align: left;
            color: var(--cyan);
            font-weight: bold;
            border-bottom: 2px solid var(--cyan);
            white-space: nowrap;
        }

        td {
            padding: 10px;
            border-bottom: 1px solid rgba(0,255,255,0.1);
            color: var(--cyan-dim);
        }

        tbody tr:hover { background: rgba(0,255,255,0.05); }

        tbody tr.downloaded { opacity: 0.5; }

        .file-checkbox {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--cyan);
        }

        /* ── LOGS ──────────────────────────────────────────── */
        .logs-container {
            background: rgba(0,0,0,0.5);
            border: 2px solid var(--cyan-border);
            border-radius: 8px;
            padding: 15px;
            height: 350px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }

        .log-entry {
            padding: 3px 0;
            color: var(--cyan-dim);
            word-break: break-all;
        }

        /* ── MODAL ─────────────────────────────────────────── */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: flex-start;
            overflow-y: auto;
            padding: 30px;
        }

        .modal.active { display: flex; }

        .modal-content {
            background: linear-gradient(135deg, #0a0a0a, #000);
            border: 2px solid var(--cyan);
            border-radius: 15px;
            padding: 30px;
            max-width: 550px;
            width: 100%;
            box-shadow: 0 0 40px rgba(0,255,255,0.4);
            margin: auto;
        }

        .modal-content.large {
            max-width: 1200px;
        }

        .modal-header {
            font-size: 1.5em;
            color: var(--cyan);
            margin-bottom: 20px;
            text-shadow: 0 0 10px var(--cyan);
        }

        .modal-buttons {
            display: flex;
            gap: 15px;
            margin-top: 25px;
        }

        .modal-buttons .btn { flex: 1; }

        /* ── FORM ──────────────────────────────────────────── */
        .form-group {
            margin-bottom: 18px;
        }

        .form-group label {
            display: block;
            color: var(--cyan-dim);
            margin-bottom: 8px;
            font-size: 1em;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px;
            background: var(--cyan-bg);
            border: 1px solid var(--cyan-border);
            border-radius: 6px;
            color: var(--cyan);
            font-size: 1em;
            font-family: inherit;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--cyan);
            box-shadow: 0 0 10px rgba(0,255,255,0.3);
        }

        .form-group textarea { resize: vertical; min-height: 60px; }

        .form-group select option {
            background: #111;
            color: var(--cyan);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        /* ── FILE BROWSER ──────────────────────────────────── */
        .breadcrumbs {
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .breadcrumb {
            padding: 5px 10px;
            background: var(--cyan-bg);
            border: 1px solid var(--cyan-border);
            border-radius: 4px;
            color: var(--cyan);
            cursor: pointer;
            font-size: 0.9em;
        }

        .breadcrumb:hover { background: rgba(0,255,255,0.15); }
        .breadcrumb-sep { color: #555; }

        .file-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            border-bottom: 1px solid rgba(0,255,255,0.1);
            cursor: pointer;
            transition: background 0.2s;
        }

        .file-item:hover { background: rgba(0,255,255,0.05); }

        .file-icon { font-size: 1.3em; width: 30px; text-align: center; }
        .file-name { flex: 1; color: var(--cyan-dim); word-break: break-all; }
        .file-info { color: #666; font-size: 0.85em; white-space: nowrap; }

        /* ── LOADING ───────────────────────────────────────── */
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--cyan-dim);
        }

        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid var(--cyan-border);
            border-top-color: var(--cyan);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── BADGE ─────────────────────────────────────────── */
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: bold;
        }

        .badge-green { background: rgba(0,255,80,0.2); color: var(--green); }
        .badge-red { background: rgba(255,0,80,0.2); color: var(--red); }
        .badge-orange { background: rgba(255,136,0,0.2); color: var(--orange); }
        .badge-cyan { background: rgba(0,255,255,0.2); color: var(--cyan); }

        /* ── TAG ───────────────────────────────────────────── */
        .tag-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }

        .tag {
            padding: 4px 10px;
            background: var(--cyan-bg);
            border: 1px solid var(--cyan-border);
            border-radius: 15px;
            font-size: 0.8em;
            color: var(--cyan-dim);
        }

        /* ── DISK USAGE BAR ────────────────────────────────── */
        .disk-bar {
            height: 20px;
            background: rgba(0,255,255,0.1);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }

        .disk-bar-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s;
        }

        .disk-bar-fill.ok { background: linear-gradient(90deg, var(--green), var(--cyan)); }
        .disk-bar-fill.warning { background: linear-gradient(90deg, var(--orange), var(--red)); }

        /* ── SCROLLBAR ─────────────────────────────────────── */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
        ::-webkit-scrollbar-thumb { background: var(--cyan-border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--cyan); }

        /* ── TABLE FILES in modal ──────────────────────────── */
        .file-table-scroll {
            max-height: 500px;
            overflow-y: auto;
        }
    </style>
</head>
<body>

<!-- ═══════════ NAVBAR ═══════════ -->
<nav class="navbar">
    <div class="navbar-brand">⚡ LLCAR v3</div>
    <div class="navbar-tabs">
        <button class="nav-tab active" onclick="showPage('dashboard')">🏠 Панель</button>
        <button class="nav-tab" onclick="showPage('sources')">📡 Источники</button>
        <button class="nav-tab" onclick="showPage('files')">📁 Файлы</button>
        <button class="nav-tab" onclick="showPage('settings')">⚙️ Настройки</button>
        <button class="nav-tab" onclick="showPage('logs')">📜 Логи</button>
        <button class="nav-tab" onclick="showPage('system')">🖥️ Система</button>
    </div>
    <div class="navbar-status">
        <div class="status-dot" id="nav-status-dot"></div>
        <span id="nav-status-text" style="font-size: 0.85em;">Готов</span>
    </div>
</nav>

<!-- ═══════════ PAGE: DASHBOARD ═══════════ -->
<div class="page active" id="page-dashboard">

    <!-- Status bar -->
    <div class="status-bar" id="status-bar">
        <div>
            <span class="status-text" id="status-text">⏸️ Готов к запуску</span>
        </div>
        <span class="status-phase phase-idle" id="status-phase">IDLE</span>
        <span id="status-elapsed" style="color: #888;">—</span>
    </div>

    <!-- Progress -->
    <div class="card" id="progress-card" style="display: none;">
        <div class="current-file-display" id="current-file">—</div>
        <div class="progress-container" style="margin-top: 10px;">
            <div class="progress-bar" id="progress-bar"></div>
        </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid-4" style="margin-bottom: 20px;">
        <div class="stat-card">
            <div class="stat-value" id="dash-total-files">0</div>
            <div class="stat-label">Всего файлов</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="dash-total-size">0 Б</div>
            <div class="stat-label">Общий размер</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="dash-session-dl">0</div>
            <div class="stat-label">Скачано за сессию</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="dash-session-err">0</div>
            <div class="stat-label">Ошибок</div>
        </div>
    </div>

    <!-- Source stats -->
    <div class="grid-4" style="margin-bottom: 20px;">
        <div class="stat-card" style="border-color: #0088FF;">
            <div class="stat-value" style="color: #0088FF;" id="dash-tg-dl">0</div>
            <div class="stat-label">📱 Telegram</div>
        </div>
        <div class="stat-card" style="border-color: var(--green);">
            <div class="stat-value" style="color: var(--green);" id="dash-web-dl">0</div>
            <div class="stat-label">🌐 Web</div>
        </div>
        <div class="stat-card" style="border-color: #fff;">
            <div class="stat-value" style="color: #fff;" id="dash-gh-dl">0</div>
            <div class="stat-label">🐙 GitHub</div>
        </div>
        <div class="stat-card" style="border-color: var(--orange);">
            <div class="stat-value" style="color: var(--orange);" id="dash-tor-dl">0</div>
            <div class="stat-label">🧲 Torrent</div>
        </div>
    </div>

    <!-- Integrity -->
    <div class="card">
        <div class="card-title">🔍 Целостность файлов</div>
        <div class="grid-4">
            <div class="stat-card">
                <div class="stat-value" id="int-checked">0</div>
                <div class="stat-label">Проверено</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--green);" id="int-complete">0</div>
                <div class="stat-label">Полных</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--orange);" id="int-incomplete">0</div>
                <div class="stat-label">Недокачанных</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--red);" id="int-missing">0</div>
                <div class="stat-label">Отсутствующих</div>
            </div>
        </div>
        <div style="margin-top: 15px;">
            <button class="btn btn-purple btn-small" onclick="runIntegrityCheck()">🔍 Проверить целостность</button>
        </div>
    </div>

    <!-- Controls -->
    <div class="btn-group" style="margin-bottom: 20px;">
        <button class="btn btn-green btn-large" id="start-btn" onclick="showPage('sources')">
            🚀 НАСТРОИТЬ И ЗАПУСТИТЬ
        </button>
        <button class="btn btn-red btn-large" id="stop-btn" onclick="stopDownload()" disabled>
            ⏹️ ОСТАНОВИТЬ
        </button>
    </div>

    <!-- Logs preview -->
    <div class="card">
        <div class="card-title">📜 Последние логи</div>
        <div class="logs-container" id="dash-logs">
            <div class="log-entry">Ожидание команды...</div>
        </div>
    </div>
</div>

<!-- ═══════════ PAGE: SOURCES ═══════════ -->
<div class="page" id="page-sources">
    <div class="grid-2">
        <!-- Telegram -->
        <div class="card">
            <div class="card-title">📱 Telegram Каналы</div>
            <div class="select-all-btn" onclick="toggleAll('telegram')">Выбрать/Снять все</div>
            <div id="telegram-sources"></div>
            <button class="add-source-btn" onclick="showAddModal('telegram')">➕ Добавить Telegram канал</button>
        </div>

        <!-- Web -->
        <div class="card">
            <div class="card-title">🌐 Web Сайты</div>
            <div class="select-all-btn" onclick="toggleAll('web')">Выбрать/Снять все</div>
            <div id="web-sources"></div>
            <button class="add-source-btn" onclick="showAddModal('web')">➕ Добавить веб-сайт</button>
        </div>

        <!-- GitHub -->
        <div class="card">
            <div class="card-title">🐙 GitHub Репозитории</div>
            <div class="select-all-btn" onclick="toggleAll('github')">Выбрать/Снять все</div>
            <div id="github-sources"></div>
            <button class="add-source-btn" onclick="showAddModal('github')">➕ Добавить GitHub репозиторий</button>
        </div>

        <!-- Torrent -->
        <div class="card">
            <div class="card-title">🧲 Торрент поисковые запросы</div>
            <div class="select-all-btn" onclick="toggleAll('torrent')">Выбрать/Снять все</div>
            <div id="torrent-sources"></div>
            <button class="add-source-btn" onclick="showAddModal('torrent')">➕ Добавить поисковый запрос</button>
        </div>
    </div>

    <!-- Launch button -->
    <div class="btn-group" style="margin-top: 20px;">
        <button class="btn btn-green btn-large" id="launch-btn" onclick="startDownload()">
            🚀 ЗАПУСТИТЬ ЗАГРУЗКУ ВЫБРАННЫХ ИСТОЧНИКОВ
        </button>
    </div>
</div>

<!-- ═══════════ PAGE: FILES ═══════════ -->
<div class="page" id="page-files">
    <div class="card">
        <div class="card-title">📁 Файловый браузер</div>
        <div class="breadcrumbs" id="breadcrumbs"></div>
        <div id="file-list" style="max-height: 600px; overflow-y: auto;"></div>
    </div>

    <div class="grid-2" style="margin-top: 20px;">
        <!-- By extension -->
        <div class="card">
            <div class="card-title">📊 По расширениям</div>
            <div id="ext-stats"></div>
        </div>

        <!-- Recent files -->
        <div class="card">
            <div class="card-title">🕐 Последние файлы</div>
            <div id="recent-files" style="max-height: 400px; overflow-y: auto;"></div>
        </div>
    </div>
</div>

<!-- ═══════════ PAGE: SETTINGS ═══════════ -->
<div class="page" id="page-settings">
    <div class="grid-2">
        <div class="card">
            <div class="card-title">⚙️ Основные настройки</div>

            <div class="form-group">
                <label>📁 Путь для сохранения:</label>
                <input type="text" id="cfg-download-path" placeholder="./downloads">
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>📏 Макс. размер файла (МБ):</label>
                    <input type="number" id="cfg-max-size" min="1" max="10000" value="500">
                </div>
                <div class="form-group">
                    <label>📨 Лимит сообщений Telegram:</label>
                    <input type="number" id="cfg-msg-limit" min="10" max="100000" value="1000">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>⏱️ Задержка между запросами (сек):</label>
                    <input type="number" id="cfg-delay" min="0" max="60" step="0.5" value="2">
                </div>
                <div class="form-group">
                    <label>&nbsp;</label>
                    <div>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                            <input type="checkbox" id="cfg-recheck" style="width: 20px; height: 20px; accent-color: var(--cyan);">
                            Повторная проверка (recheck)
                        </label>
                    </div>
                    <div style="margin-top: 10px;">
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                            <input type="checkbox" id="cfg-integrity" style="width: 20px; height: 20px; accent-color: var(--cyan);">
                            Проверка целостности при старте
                        </label>
                    </div>
                </div>
            </div>

            <button class="btn btn-green" onclick="saveSettings()">💾 Сохранить настройки</button>
        </div>

        <div class="card">
            <div class="card-title">🔎 Фильтры</div>

            <div class="form-group">
                <label>📄 Разрешённые расширения (через запятую):</label>
                <textarea id="cfg-extensions" rows="3" placeholder=".pdf, .djvu, .doc, .docx"></textarea>
            </div>

            <div class="form-group">
                <label>✅ Ключевые слова (включить):</label>
                <textarea id="cfg-keywords-include" rows="3" placeholder="manual, repair, service"></textarea>
            </div>

            <div class="form-group">
                <label>❌ Ключевые слова (исключить):</label>
                <textarea id="cfg-keywords-exclude" rows="3" placeholder="catalog, price"></textarea>
            </div>

            <button class="btn btn-green" onclick="saveSettings()">💾 Сохранить фильтры</button>
        </div>
    </div>
</div>

<!-- ═══════════ PAGE: LOGS ═══════════ -->
<div class="page" id="page-logs">
    <div class="card">
        <div class="card-title">📜 Текущая сессия</div>
        <div class="logs-container" id="page-logs-container" style="height: 400px;"></div>
    </div>

    <div class="card">
        <div class="card-title">📂 Файлы логов</div>
        <div id="log-files-list"></div>
    </div>
</div>

<!-- ═══════════ PAGE: SYSTEM ═══════════ -->
<div class="page" id="page-system">
    <div class="grid-2">
        <div class="card">
            <div class="card-title">🖥️ Информация о системе</div>
            <div id="system-info">
                <div class="loading"><span class="spinner"></span>Загрузка...</div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">📦 Установленные модули</div>
            <div id="modules-info">
                <div class="loading"><span class="spinner"></span>Загрузка...</div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">💾 Место на диске</div>
        <div id="disk-info"></div>
    </div>
</div>

<!-- ═══════════ MODALS ═══════════ -->

<!-- Modal: Add Telegram -->
<div id="modal-telegram" class="modal">
    <div class="modal-content">
        <div class="modal-header">➕ Добавить Telegram канал</div>
        <div class="form-group">
            <label>Имя канала (без @):</label>
            <input type="text" id="add-tg-name" placeholder="avtomanualy">
        </div>
        <div class="modal-buttons">
            <button class="btn btn-green" onclick="addSource('telegram')">Добавить</button>
            <button class="btn btn-red" onclick="closeModals()">Отмена</button>
        </div>
    </div>
</div>

<!-- Modal: Add Web -->
<div id="modal-web" class="modal">
    <div class="modal-content">
        <div class="modal-header">➕ Добавить веб-сайт</div>
        <div class="form-group">
            <label>ID сайта:</label>
            <input type="text" id="add-web-id" placeholder="my_manuals">
        </div>
        <div class="form-group">
            <label>URL:</label>
            <input type="text" id="add-web-url" placeholder="https://example.com/manuals">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Кодировка (опц.):</label>
                <input type="text" id="add-web-encoding" placeholder="utf-8">
            </div>
            <div class="form-group">
                <label>Макс. страниц:</label>
                <input type="number" id="add-web-pages" value="10" min="1">
            </div>
        </div>
        <div class="modal-buttons">
            <button class="btn btn-green" onclick="addSource('web')">Добавить</button>
            <button class="btn btn-red" onclick="closeModals()">Отмена</button>
        </div>
    </div>
</div>

<!-- Modal: Add GitHub -->
<div id="modal-github" class="modal">
    <div class="modal-content">
        <div class="modal-header">➕ Добавить GitHub репозиторий</div>
        <div class="form-group">
            <label>URL репозитория:</label>
            <input type="text" id="add-gh-url" placeholder="https://github.com/user/repo">
        </div>
        <div class="form-group">
            <label>Путь (опц.):</label>
            <input type="text" id="add-gh-path" placeholder="docs">
        </div>
        <div class="form-group">
            <label>Описание (опц.):</label>
            <textarea id="add-gh-desc" rows="2" placeholder="Описание"></textarea>
        </div>
        <div class="modal-buttons">
            <button class="btn btn-green" onclick="addSource('github')">Добавить</button>
            <button class="btn btn-red" onclick="closeModals()">Отмена</button>
        </div>
    </div>
</div>

<!-- Modal: Add Torrent Query -->
<div id="modal-torrent" class="modal">
    <div class="modal-content">
        <div class="modal-header">➕ Добавить торрент-запрос</div>
        <div class="form-group">
            <label>Поисковый запрос:</label>
            <input type="text" id="add-tor-query" placeholder="руководство по ремонту BMW">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Макс. результатов:</label>
                <input type="number" id="add-tor-max" value="10" min="1">
            </div>
            <div class="form-group">
                <label>Мин. сидеров:</label>
                <input type="number" id="add-tor-seeds" value="1" min="0">
            </div>
        </div>
        <div class="modal-buttons">
            <button class="btn btn-green" onclick="addSource('torrent')">Добавить</button>
            <button class="btn btn-red" onclick="closeModals()">Отмена</button>
        </div>
    </div>
</div>

<!-- Modal: Browse Telegram Channel -->
<div id="modal-browse" class="modal">
    <div class="modal-content large">
        <div class="modal-header">📋 Файлы: <span id="browse-ch-name"></span>
            <span class="badge badge-cyan" id="browse-total" style="margin-left: 10px;"></span>
            <span class="badge badge-green" id="browse-new" style="margin-left: 5px;"></span>
        </div>
        <div class="file-table-scroll" style="max-height: 500px; overflow-y: auto;">
            <table>
                <thead>
                    <tr>
                        <th style="width: 40px;"><input type="checkbox" id="select-all-ch-files" class="file-checkbox"></th>
                        <th style="width: 70px;">ID</th>
                        <th>Имя файла</th>
                        <th style="width: 90px;">Размер</th>
                        <th style="width: 70px;">Тип</th>
                        <th style="width: 100px;">Дата</th>
                        <th style="width: 55px;">⬇️</th>
                    </tr>
                </thead>
                <tbody id="browse-tbody">
                    <tr><td colspan="7" class="loading"><span class="spinner"></span>Загрузка...</td></tr>
                </tbody>
            </table>
        </div>
        <div class="modal-buttons">
            <button class="btn btn-green" onclick="downloadSelectedFiles()">📥 Скачать выбранные</button>
            <button class="btn btn-red" onclick="closeModals()">Закрыть</button>
        </div>
    </div>
</div>

<!-- Modal: View log file -->
<div id="modal-log-view" class="modal">
    <div class="modal-content large">
        <div class="modal-header" id="log-view-title">📄 Лог</div>
        <div class="logs-container" id="log-view-content" style="height: 500px;"></div>
        <div class="modal-buttons">
            <button class="btn" onclick="closeModals()">Закрыть</button>
        </div>
    </div>
</div>


<!-- ═══════════ JAVASCRIPT ═══════════ -->
<script>

// ═══════════════════════════════════════
// STATE
// ═══════════════════════════════════════
let sourcesData = {telegram: [], web: [], github: [], torrent: []};
let statusInterval = null;
let currentBrowseChannel = null;

// ═══════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));

    document.getElementById('page-' + pageId).classList.add('active');
    event.target.classList.add('active');

    // Lazy-load page data
    if (pageId === 'files') loadFiles('');
    if (pageId === 'settings') loadSettings();
    if (pageId === 'logs') loadLogFiles();
    if (pageId === 'system') loadSystemInfo();
}

// ═══════════════════════════════════════
// SOURCES
// ═══════════════════════════════════════
async function loadSources() {
    try {
        const r = await fetch('/api/sources');
        sourcesData = await r.json();

        // Enable all by default
        for (const type of ['telegram', 'web', 'github', 'torrent']) {
            (sourcesData[type] || []).forEach(s => {
                if (s.enabled === undefined) s.enabled = true;
            });
        }

        renderAllSources();
    } catch (e) {
        console.error('Error loading sources:', e);
    }
}

function renderAllSources() {
    renderSourceList('telegram', 'telegram-sources');
    renderSourceList('web', 'web-sources');
    renderSourceList('github', 'github-sources');
    renderSourceList('torrent', 'torrent-sources');
}

function renderSourceList(type, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    const sources = sourcesData[type] || [];
    if (sources.length === 0) {
        container.innerHTML = '<div style="color: #555; padding: 10px;">Нет источников</div>';
        return;
    }

    sources.forEach((source, idx) => {
        const div = document.createElement('div');
        div.className = 'source-item' + (source.enabled ? ' checked' : '');
        div.onclick = () => {
            source.enabled = !source.enabled;
            renderSourceList(type, containerId);
        };

        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = source.enabled;
        cb.onclick = e => e.stopPropagation();
        cb.onchange = () => { source.enabled = cb.checked; renderSourceList(type, containerId); };

        const lbl = document.createElement('label');
        lbl.textContent = source.name;
        lbl.style.cursor = 'pointer';

        div.appendChild(cb);
        div.appendChild(lbl);

        // Browse button for Telegram
        if (type === 'telegram') {
            const browseBtn = document.createElement('button');
            browseBtn.className = 'browse-btn';
            browseBtn.textContent = '🔍';
            browseBtn.title = 'Просмотр файлов';
            browseBtn.onclick = e => { e.stopPropagation(); browseChannel(source.id); };
            div.appendChild(browseBtn);
        }

        // Delete button for custom
        if (source.custom) {
            const delBtn = document.createElement('button');
            delBtn.className = 'delete-btn';
            delBtn.textContent = '✕';
            delBtn.title = 'Удалить';
            delBtn.onclick = e => { e.stopPropagation(); deleteSource(type, source.id); };
            div.appendChild(delBtn);
        }

        container.appendChild(div);
    });
}

function toggleAll(type) {
    const sources = sourcesData[type] || [];
    const allOn = sources.every(s => s.enabled);
    sources.forEach(s => s.enabled = !allOn);
    renderAllSources();
}

// ═══════════════════════════════════════
// ADD / DELETE SOURCE
// ═══════════════════════════════════════
function showAddModal(type) {
    closeModals();
    document.getElementById('modal-' + type).classList.add('active');
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
    document.querySelectorAll('.modal input, .modal textarea').forEach(el => {
        if (el.type !== 'checkbox') el.value = '';
    });
}

document.addEventListener('click', e => { if (e.target.classList.contains('modal')) closeModals(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModals(); });

async function addSource(type) {
    let data = {};

    if (type === 'telegram') {
        const name = document.getElementById('add-tg-name').value.trim();
        if (!name) return alert('Введите имя канала');
        data = {name};
    } else if (type === 'web') {
        const id = document.getElementById('add-web-id').value.trim();
        const url = document.getElementById('add-web-url').value.trim();
        if (!id || !url) return alert('Заполните ID и URL');
        data = {id, url, encoding: document.getElementById('add-web-encoding').value.trim(), max_pages: document.getElementById('add-web-pages').value};
    } else if (type === 'github') {
        const url = document.getElementById('add-gh-url').value.trim();
        if (!url) return alert('Введите URL');
        data = {url, path: document.getElementById('add-gh-path').value.trim(), description: document.getElementById('add-gh-desc').value.trim()};
    } else if (type === 'torrent') {
        const query = document.getElementById('add-tor-query').value.trim();
        if (!query) return alert('Введите запрос');
        data = {query, max_results: document.getElementById('add-tor-max').value, min_seeds: document.getElementById('add-tor-seeds').value};
    }

    try {
        const r = await fetch('/api/sources/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type, data})
        });
        const res = await r.json();
        if (res.success) { closeModals(); await loadSources(); }
        else alert('Ошибка: ' + res.error);
    } catch (e) { alert('Ошибка: ' + e); }
}

async function deleteSource(type, id) {
    if (!confirm('Удалить этот источник?')) return;
    try {
        const r = await fetch('/api/sources/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type, id})
        });
        const res = await r.json();
        if (res.success) await loadSources();
        else alert('Ошибка: ' + res.error);
    } catch (e) { alert('Ошибка: ' + e); }
}

// ═══════════════════════════════════════
// DOWNLOAD CONTROL
// ═══════════════════════════════════════
async function startDownload() {
    const selected = {
        telegram: (sourcesData.telegram || []).filter(s => s.enabled).map(s => s.id),
        web: (sourcesData.web || []).filter(s => s.enabled).map(s => s.id),
        github: (sourcesData.github || []).filter(s => s.enabled).map(s => s.id),
        torrent: (sourcesData.torrent || []).filter(s => s.enabled).map(s => s.id),
    };

    const total = selected.telegram.length + selected.web.length + selected.github.length + selected.torrent.length;
    if (total === 0) return alert('Выберите хотя бы один источник!');

    try {
        const r = await fetch('/api/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(selected)
        });
        const res = await r.json();
        if (res.success) {
            document.getElementById('stop-btn').disabled = false;
            document.getElementById('launch-btn').disabled = true;
            // Switch to dashboard
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-dashboard').classList.add('active');
            document.querySelectorAll('.nav-tab').forEach(t => {
                t.classList.toggle('active', t.textContent.includes('Панель'));
            });
            startStatusUpdates();
        } else {
            alert('Ошибка: ' + res.error);
        }
    } catch (e) { alert('Ошибка: ' + e); }
}

async function stopDownload() {
    try {
        await fetch('/api/stop', {method: 'POST'});
        document.getElementById('stop-btn').disabled = true;
        document.getElementById('launch-btn').disabled = false;
    } catch (e) { alert('Ошибка: ' + e); }
}

// ═══════════════════════════════════════
// STATUS UPDATES
// ═══════════════════════════════════════
function startStatusUpdates() {
    if (statusInterval) clearInterval(statusInterval);
    statusInterval = setInterval(updateStatus, 1000);
}

async function updateStatus() {
    try {
        const r = await fetch('/api/status');
        const s = await r.json();

        // Nav status
        const dot = document.getElementById('nav-status-dot');
        const navText = document.getElementById('nav-status-text');
        dot.className = 'status-dot ' + (s.running ? 'running' : 'idle');
        navText.textContent = s.running ? 'Загрузка...' : (s.phase === 'done' ? 'Завершено' : 'Готов');

        // Status bar
        const statusBar = document.getElementById('status-bar');
        statusBar.className = 'status-bar' + (s.running ? ' running' : '');

        const statusText = document.getElementById('status-text');
        const phaseNames = {
            idle: '⏸️ Готов к запуску',
            starting: '🔄 Запуск...',
            integrity_check: '🔍 Проверка целостности',
            telegram: '📱 Telegram загрузка',
            web: '🌐 Web загрузка',
            github: '🐙 GitHub загрузка',
            torrent: '🧲 Торрент загрузка',
            recheck: '🔄 Повторная проверка',
            done: '✅ Завершено',
            stopped: '⏹️ Остановлено',
        };
        statusText.textContent = phaseNames[s.phase] || s.phase;

        const phaseEl = document.getElementById('status-phase');
        phaseEl.className = 'status-phase phase-' + (s.phase || 'idle');
        phaseEl.textContent = (s.phase || 'idle').toUpperCase();

        document.getElementById('status-elapsed').textContent = s.elapsed || '—';

        // Progress
        const progressCard = document.getElementById('progress-card');
        if (s.running && s.current_file) {
            progressCard.style.display = 'block';
            document.getElementById('current-file').textContent = '📄 ' + (s.current_file || '—');
            document.getElementById('progress-bar').style.width = (s.progress || 0) + '%';
        } else {
            progressCard.style.display = 'none';
        }

        // Session stats
        let sessionDl = 0, sessionErr = 0;
        for (const key of ['telegram', 'web', 'github', 'torrent']) {
            const st = s.stats[key] || {};
            sessionDl += st.downloaded || 0;
            sessionErr += st.errors || 0;
        }
        document.getElementById('dash-session-dl').textContent = sessionDl;
        document.getElementById('dash-session-err').textContent = sessionErr;

        document.getElementById('dash-tg-dl').textContent = (s.stats.telegram || {}).downloaded || 0;
        document.getElementById('dash-web-dl').textContent = (s.stats.web || {}).downloaded || 0;
        document.getElementById('dash-gh-dl').textContent = (s.stats.github || {}).downloaded || 0;
        document.getElementById('dash-tor-dl').textContent = (s.stats.torrent || {}).downloaded || 0;

        // Integrity
        const integ = s.integrity || {};
        document.getElementById('int-checked').textContent = integ.total_checked || 0;
        document.getElementById('int-complete').textContent = integ.complete || 0;
        document.getElementById('int-incomplete').textContent = integ.incomplete || 0;
        document.getElementById('int-missing').textContent = integ.missing || 0;

        // Logs
        if (s.logs && s.logs.length > 0) {
            const logsHtml = s.logs.slice(-80).map(l => '<div class="log-entry">' + escHtml(l) + '</div>').join('');
            document.getElementById('dash-logs').innerHTML = logsHtml;
            document.getElementById('dash-logs').scrollTop = 999999;
            document.getElementById('page-logs-container').innerHTML = logsHtml;
            document.getElementById('page-logs-container').scrollTop = 999999;
        }

        // Buttons
        document.getElementById('stop-btn').disabled = !s.running;
        document.getElementById('launch-btn').disabled = s.running;

        // Stop interval when done
        if (!s.running && statusInterval) {
            // Keep updating for a few more seconds then stop
            setTimeout(() => {
                if (!download_status_running) {
                    clearInterval(statusInterval);
                    statusInterval = null;
                }
            }, 3000);
            loadStatistics(); // Final stat update
        }

    } catch (e) {
        console.error('Status update error:', e);
    }
}

let download_status_running = false;

function escHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

// ═══════════════════════════════════════
// STATISTICS
// ═══════════════════════════════════════
async function loadStatistics() {
    try {
        const r = await fetch('/api/statistics');
        const s = await r.json();

        document.getElementById('dash-total-files').textContent = s.total_files || 0;
        document.getElementById('dash-total-size').textContent = s.total_size_str || '0 Б';

        // Extension stats
        const extDiv = document.getElementById('ext-stats');
        if (extDiv && s.by_extension) {
            extDiv.innerHTML = s.by_extension.map(e =>
                `<div class="file-item">
                    <div class="file-icon">📄</div>
                    <div class="file-name"><strong>${escHtml(e.ext)}</strong></div>
                    <div class="file-info">${e.count} файлов — ${e.size_str}</div>
                </div>`
            ).join('') || '<div style="color: #555; padding: 10px;">Нет данных</div>';
        }

        // Recent files
        const recentDiv = document.getElementById('recent-files');
        if (recentDiv && s.recent_files) {
            recentDiv.innerHTML = s.recent_files.map(f =>
                `<div class="file-item">
                    <div class="file-icon">📄</div>
                    <div class="file-name">${escHtml(f.name)}</div>
                    <div class="file-info">${f.size} — ${f.modified}</div>
                </div>`
            ).join('') || '<div style="color: #555; padding: 10px;">Нет файлов</div>';
        }

    } catch (e) {
        console.error('Stats error:', e);
    }
}

// ═══════════════════════════════════════
// FILE BROWSER
// ═══════════════════════════════════════
async function loadFiles(path) {
    try {
        const r = await fetch('/api/files?path=' + encodeURIComponent(path));
        const data = await r.json();

        if (!data.success) {
            document.getElementById('file-list').innerHTML = '<div style="color: var(--red); padding: 20px;">Ошибка: ' + escHtml(data.error) + '</div>';
            return;
        }

        // Breadcrumbs
        const bcDiv = document.getElementById('breadcrumbs');
        bcDiv.innerHTML = data.breadcrumbs.map((b, i) =>
            (i > 0 ? '<span class="breadcrumb-sep">›</span>' : '') +
            `<span class="breadcrumb" onclick="loadFiles('${escHtml(b.path)}')">${escHtml(b.name)}</span>`
        ).join('');

        // File list
        const listDiv = document.getElementById('file-list');
        if (data.items.length === 0) {
            listDiv.innerHTML = '<div style="color: #555; padding: 20px; text-align: center;">Пустая папка</div>';
            return;
        }

        listDiv.innerHTML = data.items.map(item => {
            if (item.is_dir) {
                return `<div class="file-item" onclick="loadFiles('${escHtml(item.path)}')">
                    <div class="file-icon">📁</div>
                    <div class="file-name">${escHtml(item.name)}</div>
                    <div class="file-info">${item.file_count || 0} файлов</div>
                </div>`;
            } else {
                return `<div class="file-item">
                    <div class="file-icon">${getFileIcon(item.extension)}</div>
                    <div class="file-name">${escHtml(item.name)}</div>
                    <div class="file-info">${item.size_str} — ${item.modified}</div>
                    <a href="/api/files/download?path=${encodeURIComponent(item.path)}" class="btn btn-small" title="Скачать" style="text-decoration:none;">⬇️</a>
                    <button class="delete-btn" onclick="event.stopPropagation(); deleteFile('${escHtml(item.path)}')">✕</button>
                </div>`;
            }
        }).join('');

    } catch (e) {
        document.getElementById('file-list').innerHTML = '<div style="color: var(--red); padding: 20px;">Ошибка: ' + e + '</div>';
    }
}

function getFileIcon(ext) {
    const icons = {'.pdf': '📕', '.djvu': '📘', '.doc': '📄', '.docx': '📄', '.xls': '📊', '.xlsx': '📊', '.zip': '📦', '.rar': '📦', '.7z': '📦', '.torrent': '🧲'};
    return icons[ext] || '📄';
}

async function deleteFile(path) {
    if (!confirm('Удалить ' + path + '?')) return;
    try {
        const r = await fetch('/api/files/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path})
        });
        const res = await r.json();
        if (res.success) {
            const parentPath = path.split('/').slice(0, -1).join('/');
            loadFiles(parentPath);
            loadStatistics();
        } else { alert('Ошибка: ' + res.error); }
    } catch (e) { alert('Ошибка: ' + e); }
}

// ═══════════════════════════════════════
// BROWSE TELEGRAM CHANNEL
// ═══════════════════════════════════════
async function browseChannel(channel) {
    currentBrowseChannel = channel;
    document.getElementById('browse-ch-name').textContent = '@' + channel;
    document.getElementById('browse-total').textContent = '';
    document.getElementById('browse-new').textContent = '';
    document.getElementById('modal-browse').classList.add('active');

    const tbody = document.getElementById('browse-tbody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading"><span class="spinner"></span>Загрузка файлов...</td></tr>';

    try {
        const r = await fetch('/api/telegram/browse/' + encodeURIComponent(channel));
        const data = await r.json();

        if (!data.success) {
            tbody.innerHTML = `<tr><td colspan="7" style="color: var(--red); text-align: center; padding: 20px;">${escHtml(data.error)}</td></tr>`;
            return;
        }

        document.getElementById('browse-total').textContent = 'Всего: ' + data.total;
        document.getElementById('browse-new').textContent = 'Новых: ' + data.new_count + ' (' + data.new_size + ')';

        if (data.files.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px; color: #555;">Файлы не найдены</td></tr>';
            return;
        }

        tbody.innerHTML = data.files.map(f => {
            const date = f.date ? new Date(f.date).toLocaleDateString('ru-RU') : '—';
            const status = f.is_downloaded ? '✅' : '⬜';
            const cls = f.is_downloaded ? ' class="downloaded"' : '';

            return `<tr${cls}>
                <td><input type="checkbox" class="file-checkbox" data-id="${f.message_id}" ${f.is_downloaded ? 'disabled' : ''}></td>
                <td>${f.message_id}</td>
                <td title="${escHtml(f.caption)}">${escHtml(f.filename)}</td>
                <td>${f.size_str}</td>
                <td>${f.extension}</td>
                <td>${date}</td>
                <td style="text-align:center;">${status}</td>
            </tr>`;
        }).join('');

    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" style="color: var(--red); text-align: center; padding: 20px;">${e}</td></tr>`;
    }
}

document.getElementById('select-all-ch-files').addEventListener('change', function() {
    document.querySelectorAll('#browse-tbody .file-checkbox:not(:disabled)').forEach(cb => cb.checked = this.checked);
});

async function downloadSelectedFiles() {
    const cbs = document.querySelectorAll('#browse-tbody .file-checkbox:checked');
    const ids = Array.from(cbs).map(cb => parseInt(cb.dataset.id));

    if (ids.length === 0) return alert('Выберите файлы!');
    if (!confirm('Скачать ' + ids.length + ' файлов из @' + currentBrowseChannel + '?')) return;

    try {
        const r = await fetch('/api/telegram/download_selected', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({channel: currentBrowseChannel, message_ids: ids})
        });
        const res = await r.json();
        if (res.success) {
            closeModals();
            startStatusUpdates();
            // Switch to dashboard
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-dashboard').classList.add('active');
            document.querySelectorAll('.nav-tab').forEach(t => {
                t.classList.toggle('active', t.textContent.includes('Панель'));
            });
        } else { alert('Ошибка: ' + res.error); }
    } catch (e) { alert('Ошибка: ' + e); }
}

// ═══════════════════════════════════════
// SETTINGS
// ═══════════════════════════════════════
async function loadSettings() {
    try {
        const r = await fetch('/api/config');
        const cfg = await r.json();

        document.getElementById('cfg-download-path').value = cfg.download_path || '';
        document.getElementById('cfg-max-size').value = cfg.max_file_size_mb || 500;
        document.getElementById('cfg-msg-limit').value = cfg.message_limit || 1000;
        document.getElementById('cfg-delay').value = cfg.request_delay || 2;
        document.getElementById('cfg-recheck').checked = cfg.recheck_mode !== false;
        document.getElementById('cfg-integrity').checked = cfg.integrity_check !== false;

        document.getElementById('cfg-extensions').value = (cfg.allowed_extensions || []).join(', ');
        document.getElementById('cfg-keywords-include').value = (cfg.keywords_include || []).join(', ');
        document.getElementById('cfg-keywords-exclude').value = (cfg.keywords_exclude || []).join(', ');

    } catch (e) { console.error('Config load error:', e); }
}

async function saveSettings() {
    const cfg = {
        download_path: document.getElementById('cfg-download-path').value.trim(),
        max_file_size_mb: parseInt(document.getElementById('cfg-max-size').value) || 500,
        message_limit: parseInt(document.getElementById('cfg-msg-limit').value) || 1000,
        request_delay: parseFloat(document.getElementById('cfg-delay').value) || 2,
        recheck_mode: document.getElementById('cfg-recheck').checked,
        integrity_check: document.getElementById('cfg-integrity').checked,
        allowed_extensions: document.getElementById('cfg-extensions').value.split(',').map(s => s.trim()).filter(Boolean),
        keywords_include: document.getElementById('cfg-keywords-include').value.split(',').map(s => s.trim()).filter(Boolean),
        keywords_exclude: document.getElementById('cfg-keywords-exclude').value.split(',').map(s => s.trim()).filter(Boolean),
    };

    try {
        const r = await fetch('/api/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(cfg)
        });
        const res = await r.json();
        if (res.success) alert('✅ Настройки сохранены!');
        else alert('Ошибка: ' + res.error);
    } catch (e) { alert('Ошибка: ' + e); }
}

// ═══════════════════════════════════════
// INTEGRITY CHECK
// ═══════════════════════════════════════
async function runIntegrityCheck() {
    try {
        const r = await fetch('/api/integrity/check', {method: 'POST'});
        const res = await r.json();
        if (res.success) {
            startStatusUpdates();
        } else { alert('Ошибка: ' + res.error); }
    } catch (e) { alert('Ошибка: ' + e); }
}

// ═══════════════════════════════════════
// LOGS
// ═══════════════════════════════════════
async function loadLogFiles() {
    try {
        const r = await fetch('/api/logs');
        const data = await r.json();

        const div = document.getElementById('log-files-list');
        if (!data.logs || data.logs.length === 0) {
            div.innerHTML = '<div style="color: #555; padding: 10px;">Нет лог-файлов</div>';
            return;
        }

        div.innerHTML = data.logs.map(l =>
            `<div class="file-item">
                <div class="file-icon">📄</div>
                <div class="file-name">${escHtml(l.name)}</div>
                <div class="file-info">${l.size} — ${l.modified}</div>
                <button class="btn btn-small" onclick="viewLog('${escHtml(l.name)}')">👁️</button>
                <a href="/api/logs/download/${encodeURIComponent(l.name)}" class="btn btn-small" style="text-decoration:none;">⬇️</a>
            </div>`
        ).join('');

    } catch (e) { console.error('Log files error:', e); }
}

async function viewLog(filename) {
    try {
        const r = await fetch('/api/logs/view/' + encodeURIComponent(filename));
        const data = await r.json();

        document.getElementById('log-view-title').textContent = '📄 ' + filename + ' (' + data.total_lines + ' строк)';
        document.getElementById('log-view-content').innerHTML =
            (data.lines || []).map(l => '<div class="log-entry">' + escHtml(l) + '</div>').join('');
        document.getElementById('modal-log-view').classList.add('active');

    } catch (e) { alert('Ошибка: ' + e); }
}

// ═══════════════════════════════════════
// SYSTEM
// ═══════════════════════════════════════
async function loadSystemInfo() {
    try {
        const r = await fetch('/api/system');
        const s = await r.json();

        document.getElementById('system-info').innerHTML = `
            <div class="file-item"><div class="file-icon">🐍</div><div class="file-name">Python</div><div class="file-info">${escHtml(s.python_version)}</div></div>
            <div class="file-item"><div class="file-icon">💻</div><div class="file-name">Платформа</div><div class="file-info">${escHtml(s.platform)}</div></div>
            <div class="file-item"><div class="file-icon">📁</div><div class="file-name">Путь загрузок</div><div class="file-info">${escHtml(s.download_path)}</div></div>
            <div class="file-item"><div class="file-icon">📱</div><div class="file-name">Telegram</div><div class="file-info">${s.telegram_configured ? '<span class="badge badge-green">Настроен</span>' : '<span class="badge badge-red">Не настроен</span>'}</div></div>
            <div class="file-item"><div class="file-icon">🧲</div><div class="file-name">Торренты</div><div class="file-info">${s.torrent_configured ? '<span class="badge badge-green">Включены</span>' : '<span class="badge badge-red">Выключены</span>'}</div></div>
        `;

        // Modules
        const modHtml = Object.entries(s.modules || {}).map(([name, ok]) =>
            `<div class="file-item">
                <div class="file-icon">${ok ? '✅' : '❌'}</div>
                <div class="file-name">${escHtml(name)}</div>
                <div class="file-info">${ok ? '<span class="badge badge-green">Установлен</span>' : '<span class="badge badge-red">Не установлен</span>'}</div>
            </div>`
        ).join('');
        document.getElementById('modules-info').innerHTML = modHtml;

        // Disk
        const pct = s.disk_percent || 0;
        const cls = pct > 85 ? 'warning' : 'ok';
        document.getElementById('disk-info').innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>Использовано: ${s.disk_used}</span>
                <span>Свободно: ${s.disk_free}</span>
                <span>Всего: ${s.disk_total}</span>
            </div>
            <div class="disk-bar"><div class="disk-bar-fill ${cls}" style="width: ${pct}%;"></div></div>
            <div style="text-align: center; color: #888;">${pct}% использовано</div>
        `;

    } catch (e) { console.error('System info error:', e); }
}

// ═══════════════════════════════════════
// INIT
// ═══════════════════════════════════════
loadSources();
loadStatistics();

// Periodic status check (every 2s)
setInterval(async () => {
    try {
        const r = await fetch('/api/status');
        const s = await r.json();
        download_status_running = s.running;

        // Update nav dot
        const dot = document.getElementById('nav-status-dot');
        dot.className = 'status-dot ' + (s.running ? 'running' : (s.phase === 'done' ? 'idle' : 'idle'));

        if (s.running && !statusInterval) {
            startStatusUpdates();
        }
    } catch (e) {}
}, 3000);

// Periodic stats refresh (every 30s)
setInterval(loadStatistics, 30000);

</script>
</body>
</html>
'''


# ═══════════════════════════════════════════════════════════════════════════
# СКРАПИНГ СТАТЕЙ (Article Content Scrapers)
# ═══════════════════════════════════════════════════════════════════════════

import sqlite3

SCRAPERS_DIR = Path(__file__).parent / 'scrapers'
SCRAPERS_DB = Path(__file__).parent / 'data' / 'scraped_articles.db'

ALL_SCRAPERS = [
    "lixiang", "autohome", "ru", "drom", "drom_reviews",
    "drive2", "liforum", "dongchedi", "carnewschina",
    "wikipedia", "electrek", "ru_auto", "autoreview", "news",
    "getcar", "autochina_blog", "ev_forums", "autonews",
]

_scraper_runs = {}
_scraper_lock = threading.Lock()


def _run_scraper_background(name: str):
    """Run scraper as subprocess, store result in _scraper_runs."""
    import time as _time
    started = _time.time()
    with _scraper_lock:
        _scraper_runs[name] = {'status': 'running', 'started': started}
    try:
        result = subprocess.run(
            [sys.executable, str(SCRAPERS_DIR / 'run_scrapers.py'), '--sources', name],
            capture_output=True, text=True, timeout=600, cwd=str(SCRAPERS_DIR)
        )
        with _scraper_lock:
            _scraper_runs[name] = {
                'status': 'done' if result.returncode == 0 else 'error',
                'started': started,
                'finished': _time.time(),
                'result': result.stdout[-2000:] if result.stdout else '',
                'error': result.stderr[-1000:] if result.stderr else '',
                'returncode': result.returncode,
            }
    except subprocess.TimeoutExpired:
        with _scraper_lock:
            _scraper_runs[name] = {'status': 'timeout', 'started': started,
                                    'finished': _time.time()}
    except Exception as e:
        with _scraper_lock:
            _scraper_runs[name] = {'status': 'error', 'started': started,
                                    'finished': _time.time(), 'error': str(e)}


@app.route('/api/scrapers/list')
def scrapers_list():
    """List all scrapers with DB stats."""
    scrapers = []
    if SCRAPERS_DB.exists():
        try:
            with sqlite3.connect(str(SCRAPERS_DB)) as conn:
                rows = conn.execute("""
                    SELECT source_name, lang, COUNT(*) total,
                           SUM(CASE WHEN imported=1 THEN 1 ELSE 0 END) imported,
                           AVG(relevance) avg_relevance,
                           MAX(scraped_at) last_scraped,
                           AVG(LENGTH(content)) avg_length
                    FROM scraped_content
                    GROUP BY source_name
                """).fetchall()
                for r in rows:
                    with _scraper_lock:
                        run_info = _scraper_runs.get(r[0], {})
                    scrapers.append({
                        'name': r[0], 'lang': r[1], 'total': r[2],
                        'imported': r[3] or 0,
                        'avg_relevance': round(r[4] or 0, 2),
                        'last_scraped': r[5],
                        'avg_length': int(r[6] or 0),
                        'status': run_info.get('status', 'idle'),
                    })
        except Exception:
            pass

    known_names = {s['name'] for s in scrapers}
    for name in ALL_SCRAPERS:
        if name not in known_names:
            with _scraper_lock:
                run_info = _scraper_runs.get(name, {})
            scrapers.append({
                'name': name, 'lang': '?', 'total': 0, 'imported': 0,
                'avg_relevance': 0, 'last_scraped': None, 'avg_length': 0,
                'status': run_info.get('status', 'idle'),
            })

    return jsonify({'scrapers': scrapers})


@app.route('/api/scrapers/run/<name>', methods=['POST'])
def scrapers_run(name):
    """Start scraper in background thread."""
    if name != 'all' and name not in ALL_SCRAPERS:
        return jsonify({'error': f'Unknown scraper: {name}'}), 404

    with _scraper_lock:
        existing = _scraper_runs.get(name, {})
        if existing.get('status') == 'running':
            return jsonify({'status': 'already_running', 'name': name})

    if name == 'all':
        for s in ALL_SCRAPERS:
            t = threading.Thread(target=_run_scraper_background, args=(s,), daemon=True)
            t.start()
    else:
        t = threading.Thread(target=_run_scraper_background, args=(name,), daemon=True)
        t.start()

    return jsonify({'status': 'started', 'name': name})


@app.route('/api/scrapers/status/<name>')
def scrapers_status(name):
    """Check status of running scraper."""
    with _scraper_lock:
        info = _scraper_runs.get(name, {'status': 'idle'})
    return jsonify({'name': name, **info})


@app.route('/api/scrapers/content')
def scrapers_content():
    """Browse scraped content (paginated, filtered)."""
    if not SCRAPERS_DB.exists():
        return jsonify({'items': [], 'total': 0, 'page': 1, 'pages': 0})

    source = request.args.get('source', '')
    imported = request.args.get('imported', '')
    sort = request.args.get('sort', 'newest')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    where_clauses = []
    params = []
    if source:
        where_clauses.append("source_name LIKE ?")
        params.append(f"%{source}%")
    if imported in ('0', '1'):
        where_clauses.append("imported = ?")
        params.append(int(imported))

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    order_map = {
        'newest': 'scraped_at DESC',
        'oldest': 'scraped_at ASC',
        'relevance': 'relevance DESC',
        'length': 'LENGTH(content) DESC',
    }
    order_sql = order_map.get(sort, 'scraped_at DESC')

    with sqlite3.connect(str(SCRAPERS_DB)) as conn:
        conn.row_factory = sqlite3.Row
        total = conn.execute(
            f"SELECT COUNT(*) FROM scraped_content {where_sql}", params
        ).fetchone()[0]

        rows = conn.execute(f"""
            SELECT id, url, source_name, lang, title,
                   LENGTH(content) as content_length, relevance,
                   dtc_codes, content_class, imported, scraped_at,
                   SUBSTR(content, 1, 300) as preview
            FROM scraped_content {where_sql}
            ORDER BY {order_sql}
            LIMIT ? OFFSET ?
        """, params + [per_page, (page - 1) * per_page]).fetchall()

        items = [dict(r) for r in rows]

    pages = (total + per_page - 1) // per_page
    return jsonify({'items': items, 'total': total, 'page': page, 'pages': pages})


@app.route('/api/scrapers/content/<int:item_id>')
def scrapers_content_detail(item_id):
    """Get full content of scraped item."""
    if not SCRAPERS_DB.exists():
        return jsonify({'error': 'No database'}), 404
    with sqlite3.connect(str(SCRAPERS_DB)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM scraped_content WHERE id=?", (item_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(row))


@app.route('/api/scrapers/content/<int:item_id>', methods=['PUT'])
def scrapers_content_update(item_id):
    """Update scraped item (title, content, class)."""
    data = request.get_json() or {}
    sets = []
    params = []
    for field in ('title', 'content', 'content_class'):
        if field in data:
            sets.append(f"{field} = ?")
            params.append(data[field])
    if not sets:
        return jsonify({'error': 'Nothing to update'}), 400
    params.append(item_id)
    with sqlite3.connect(str(SCRAPERS_DB)) as conn:
        conn.execute(f"UPDATE scraped_content SET {', '.join(sets)} WHERE id=?", params)
    return jsonify({'updated': 1})


@app.route('/api/scrapers/content/<int:item_id>', methods=['DELETE'])
def scrapers_content_delete(item_id):
    """Delete scraped item."""
    with sqlite3.connect(str(SCRAPERS_DB)) as conn:
        conn.execute("DELETE FROM scraped_content WHERE id=?", (item_id,))
    return jsonify({'deleted': 1})


@app.route('/api/scrapers/import', methods=['POST'])
def scrapers_import_kb():
    """Import unimported items to KB (if KB tables exist)."""
    if not SCRAPERS_DB.exists():
        return jsonify({'error': 'No scraped database'}), 404
    with sqlite3.connect(str(SCRAPERS_DB)) as conn:
        total = conn.execute("SELECT COUNT(*) FROM scraped_content").fetchone()[0]
        imported = conn.execute("SELECT COUNT(*) FROM scraped_content WHERE imported=1").fetchone()[0]
        pending = total - imported
    return jsonify({'total': total, 'imported': imported, 'pending': pending,
                    'note': 'Use run_scrapers.py --import-kb for full KB integration'})


# ═══════════════════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print()
    print('=' * 70)
    print('    ⚡ LLCAR WEB CONTROL PANEL v3 — ПОЛНЫЙ ФУНКЦИОНАЛ')
    print('=' * 70)
    print()
    print('    Возможности:')
    print('    📡 Управление 4 типами источников')
    print('    🔍 Просмотр файлов в Telegram-каналах')
    print('    📁 Файловый браузер скачанных файлов')
    print('    ⚙️  Настройка фильтров и параметров')
    print('    📊 Статистика по типам и размерам')
    print('    🔍 Проверка целостности файлов')
    print('    📜 Просмотр и скачивание логов')
    print('    🖥️  Информация о системе')
    print()
    print('    🌐 Откройте: http://localhost:5000')
    print('    ⏹️  Ctrl+C для остановки')
    print('=' * 70)
    print()

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)