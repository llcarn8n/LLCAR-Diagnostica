#!/usr/bin/env python3
"""
Веб-интерфейс для управления загрузками LLCAR
"""

import os
import sys
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Разрешаем CORS вручную
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response

# Глобальные переменные
download_status = {
    'running': False,
    'current_source': None,
    'current_file': None,
    'progress': 0,
    'stats': {
        'telegram': {'downloaded': 0, 'errors': 0, 'size': 0},
        'web': {'downloaded': 0, 'errors': 0, 'size': 0},
        'torrent': {'downloaded': 0, 'errors': 0, 'size': 0},
    },
    'logs': []
}

config_file = Path('web_config.json')

def load_config():
    """Загрузить конфигурацию"""
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'telegram': True,
        'web': True,
        'torrent': True,
        'recheck_mode': False
    }

def save_config(config):
    """Сохранить конфигурацию"""
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Получить конфигурацию"""
    return jsonify(load_config())

@app.route('/api/config', methods=['POST'])
def update_config():
    """Обновить конфигурацию"""
    config = request.json
    save_config(config)
    return jsonify({'success': True})

@app.route('/api/status')
def get_status():
    """Получить статус загрузки"""
    return jsonify(download_status)

@app.route('/api/start', methods=['POST'])
def start_download():
    """Запустить загрузку"""
    if download_status['running']:
        return jsonify({'success': False, 'error': 'Загрузка уже запущена'})

    config = request.json
    save_config(config)

    # Запуск в отдельном потоке
    thread = threading.Thread(target=run_download, args=(config,))
    thread.daemon = True
    thread.start()

    download_status['running'] = True
    download_status['logs'].append(f'{datetime.now().strftime("%H:%M:%S")} - Загрузка запущена')

    return jsonify({'success': True})

@app.route('/api/stop', methods=['POST'])
def stop_download():
    """Остановить загрузку"""
    download_status['running'] = False
    download_status['logs'].append(f'{datetime.now().strftime("%H:%M:%S")} - Загрузка остановлена')
    return jsonify({'success': True})

def run_download(config):
    """Запустить процесс загрузки"""
    try:
        download_status['logs'].append(f'{datetime.now().strftime("%H:%M:%S")} - Запуск main_v2.py...')

        # Запуск main_v2.py как subprocess
        import subprocess

        cmd = [sys.executable, '-X', 'utf8', 'main_v2.py']
        if config.get('recheck_mode'):
            cmd.append('--recheck')

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1
        )

        # Читаем вывод
        for line in iter(process.stdout.readline, ''):
            if not download_status['running']:
                process.terminate()
                break

            line = line.strip()
            if line:
                download_status['logs'].append(f'{datetime.now().strftime("%H:%M:%S")} - {line}')

                # Парсим прогресс
                if '📄' in line:
                    download_status['current_file'] = line.split('📄')[1].strip() if '📄' in line else None

                # Ограничиваем логи
                if len(download_status['logs']) > 100:
                    download_status['logs'] = download_status['logs'][-100:]

        process.wait()
        download_status['running'] = False
        download_status['logs'].append(f'{datetime.now().strftime("%H:%M:%S")} - Загрузка завершена')

    except Exception as e:
        download_status['running'] = False
        download_status['logs'].append(f'{datetime.now().strftime("%H:%M:%S")} - Ошибка: {e}')

if __name__ == '__main__':
    # Создаём папку для шаблонов
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)

    print('=' * 60)
    print('    WEB-INTERFACE LLCAR STARTED')
    print('=' * 60)
    print('Open in browser: http://localhost:5000')
    print('Press Ctrl+C to stop')
    print('=' * 60)

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
