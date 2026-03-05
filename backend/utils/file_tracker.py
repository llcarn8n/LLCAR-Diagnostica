"""
═══════════════════════════════════════════════════════════════════════════════
                    FILE TRACKER - ОТСЛЕЖИВАНИЕ СОСТОЯНИЯ ФАЙЛОВ
═══════════════════════════════════════════════════════════════════════════════

ОПИСАНИЕ:
    Модуль для отслеживания истории скачивания файлов и проверки их целостности

ОСНОВНЫЕ ФУНКЦИИ:
    - Сохранение информации о скачанных файлах в SQLite базу
    - Проверка целостности файлов (сравнение размера)
    - Определение недокачанных файлов
    - Определение новых файлов с момента последней сессии
    - Отслеживание пропущенных файлов

ЗАЧЕМ:
    - Автоматическое возобновление недокачанных файлов
    - Не пропускать новые файлы в каналах
    - Контроль целостности скачанных данных
    - История всех скачиваний

АВТОР: Улучшенная версия v2.1
ДАТА: 2026-01-24
"""

import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging


class FileTracker:
    """
    КЛАСС: FileTracker - Отслеживание состояния файлов

    МЕТОДЫ:
        - add_file() - Добавить информацию о файле
        - get_file_info() - Получить информацию о файле
        - is_file_complete() - Проверить целостность файла
        - get_incomplete_files() - Найти недокачанные файлы
        - get_missing_files() - Найти отсутствующие файлы
        - mark_for_redownload() - Пометить для повторного скачивания
        - get_stats() - Получить статистику
    """

    def __init__(self, db_path: Path = None):
        """
        КОМАНДА: Инициализация трекера файлов

        ЧТО ДЕЛАЕТ:
            1. Создает/открывает SQLite базу данных
            2. Создает таблицы если их нет
            3. Настраивает логирование

        ПАРАМЕТРЫ:
            db_path - путь к файлу базы данных (по умолчанию ./data/files.db)

        СТРУКТУРА БД:
            Таблица 'files':
                - id: уникальный идентификатор
                - source: источник (telegram/web/github)
                - source_id: идентификатор в источнике (channel/url/repo)
                - file_id: ID файла в источнике
                - filename: имя файла
                - filepath: путь сохранения
                - expected_size: ожидаемый размер
                - actual_size: фактический размер на диске
                - file_hash: MD5 хеш файла
                - status: статус (complete/incomplete/missing/pending)
                - first_seen: когда впервые обнаружен
                - last_checked: последняя проверка
                - download_attempts: количество попыток
                - metadata: JSON с дополнительными данными
        """
        # ПУТЬ: Определяем путь к базе данных
        if db_path is None:
            db_path = Path('./data/files_tracker.db')

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # ЛОГИРОВАНИЕ: Настраиваем логгер
        self.logger = logging.getLogger(__name__)

        # ИНИЦИАЛИЗАЦИЯ: Создаем соединение и таблицы
        self.conn = None
        self._init_database()

        self.logger.info(f"📊 FileTracker инициализирован: {self.db_path}")

    def _init_database(self):
        """
        КОМАНДА: Создает структуру базы данных

        ЧТО ДЕЛАЕТ:
            Создает таблицу files если её нет

        ИНДЕКСЫ:
            - По source + source_id для быстрого поиска
            - По filename для проверки дубликатов
            - По status для фильтрации
        """
        # ПОДКЛЮЧЕНИЕ: Открываем соединение с БД
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Доступ к колонкам по имени

        cursor = self.conn.cursor()

        # SQL: Создаем таблицу files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                file_id TEXT,
                filename TEXT NOT NULL,
                filepath TEXT,
                expected_size INTEGER,
                actual_size INTEGER DEFAULT 0,
                file_hash TEXT,
                status TEXT DEFAULT 'pending',
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                download_attempts INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)

        # ИНДЕКСЫ: Создаем индексы для ускорения поиска
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_id
            ON files(source, source_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filename
            ON files(filename)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status
            ON files(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_id
            ON files(file_id)
        """)

        # СОХРАНЕНИЕ: Применяем изменения
        self.conn.commit()

        self.logger.debug("✅ База данных инициализирована")

    def add_file(
        self,
        source: str,
        source_id: str,
        filename: str,
        expected_size: int,
        file_id: Optional[str] = None,
        filepath: Optional[Path] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        КОМАНДА: Добавляет информацию о файле в базу

        ЧТО ДЕЛАЕТ:
            1. Проверяет существует ли запись
            2. Если существует - обновляет
            3. Если нет - создает новую
            4. Возвращает ID записи

        ПАРАМЕТРЫ:
            source - источник (telegram/web/github/torrent)
            source_id - ID источника (имя канала/URL/repo)
            filename - имя файла
            expected_size - ожидаемый размер в байтах
            file_id - уникальный ID файла в источнике
            filepath - путь сохранения (если уже скачан)
            metadata - дополнительные данные (dict)

        ВОЗВРАЩАЕТ:
            int - ID записи в базе

        ПРИМЕР:
            tracker.add_file(
                source='telegram',
                source_id='@avtomanualy',
                file_id='12345',
                filename='bmw_manual.pdf',
                expected_size=15728640,  # 15 MB
                metadata={'caption': 'BMW Service Manual 2020'}
            )
        """
        cursor = self.conn.cursor()

        # ПРОВЕРКА: Существует ли уже запись об этом файле
        cursor.execute("""
            SELECT id, filepath, actual_size
            FROM files
            WHERE source = ? AND source_id = ? AND file_id = ?
        """, (source, source_id, file_id))

        existing = cursor.fetchone()

        # METADATA: Сериализуем дополнительные данные в JSON
        metadata_json = json.dumps(metadata) if metadata else None

        # ОБНОВЛЕНИЕ: Если запись существует
        if existing:
            record_id = existing['id']

            # Если filepath указан - обновляем actual_size
            if filepath and filepath.exists():
                actual_size = filepath.stat().st_size
                file_hash = self._calculate_hash(filepath)

                # СТАТУС: Определяем статус файла
                if actual_size == expected_size:
                    status = 'complete'
                elif actual_size < expected_size:
                    status = 'incomplete'
                else:
                    status = 'complete'  # Размер больше - считаем нормальным

                # UPDATE: Обновляем запись
                cursor.execute("""
                    UPDATE files
                    SET filepath = ?,
                        actual_size = ?,
                        file_hash = ?,
                        status = ?,
                        last_checked = CURRENT_TIMESTAMP,
                        download_attempts = download_attempts + 1,
                        metadata = ?
                    WHERE id = ?
                """, (str(filepath), actual_size, file_hash, status, metadata_json, record_id))

            else:
                # Просто обновляем метаданные
                cursor.execute("""
                    UPDATE files
                    SET expected_size = ?,
                        last_checked = CURRENT_TIMESTAMP,
                        metadata = ?
                    WHERE id = ?
                """, (expected_size, metadata_json, record_id))

            self.logger.debug(f"🔄 Обновлена запись #{record_id}: {filename}")

        # ВСТАВКА: Если записи нет - создаем новую
        else:
            # Если filepath указан - вычисляем actual_size
            actual_size = 0
            file_hash = None
            status = 'pending'

            if filepath and filepath.exists():
                actual_size = filepath.stat().st_size
                file_hash = self._calculate_hash(filepath)

                if actual_size == expected_size:
                    status = 'complete'
                elif actual_size < expected_size:
                    status = 'incomplete'
                else:
                    status = 'complete'

            # INSERT: Создаем запись
            cursor.execute("""
                INSERT INTO files
                (source, source_id, file_id, filename, filepath,
                 expected_size, actual_size, file_hash, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source, source_id, file_id, filename,
                str(filepath) if filepath else None,
                expected_size, actual_size, file_hash, status, metadata_json
            ))

            record_id = cursor.lastrowid
            self.logger.debug(f"➕ Добавлена запись #{record_id}: {filename}")

        # СОХРАНЕНИЕ: Применяем изменения
        self.conn.commit()

        return record_id

    def get_file_info(self, source: str, source_id: str, file_id: str) -> Optional[Dict]:
        """
        КОМАНДА: Получает информацию о файле из базы

        ПАРАМЕТРЫ:
            source - источник
            source_id - ID источника
            file_id - ID файла

        ВОЗВРАЩАЕТ:
            Dict с информацией или None если не найден
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM files
            WHERE source = ? AND source_id = ? AND file_id = ?
        """, (source, source_id, file_id))

        row = cursor.fetchone()

        if row:
            return dict(row)

        return None

    def is_file_complete(self, filepath: Path, expected_size: int) -> bool:
        """
        КОМАНДА: Проверяет целостность файла

        ЧТО ДЕЛАЕТ:
            1. Проверяет существование файла
            2. Сравнивает фактический размер с ожидаемым
            3. Возвращает True если файл полный

        ПАРАМЕТРЫ:
            filepath - путь к файлу
            expected_size - ожидаемый размер в байтах

        ВОЗВРАЩАЕТ:
            bool - True если файл полный и корректный

        КРИТЕРИИ ЦЕЛОСТНОСТИ:
            - Файл существует
            - Размер >= expected_size (допускается чуть больше)
            - Размер не равен 0
        """
        # ПРОВЕРКА: Существует ли файл
        if not filepath.exists():
            return False

        # РАЗМЕР: Получаем фактический размер
        actual_size = filepath.stat().st_size

        # СРАВНЕНИЕ: Файл должен быть не меньше ожидаемого
        # Допускаем небольшое отклонение (до 1% больше)
        if actual_size == 0:
            return False

        if actual_size < expected_size:
            return False

        # Если размер больше на 1% - считаем нормой
        if actual_size > expected_size * 1.01:
            self.logger.warning(f"⚠️ Размер файла больше ожидаемого: {filepath.name}")

        return True

    def get_incomplete_files(self, source: Optional[str] = None) -> List[Dict]:
        """
        КОМАНДА: Находит все недокачанные файлы

        ЧТО ДЕЛАЕТ:
            Ищет файлы со статусом 'incomplete' или отсутствующие на диске

        ПАРАМЕТРЫ:
            source - фильтр по источнику (опционально)

        ВОЗВРАЩАЕТ:
            List[Dict] - список недокачанных файлов

        ЗАЧЕМ:
            Используется для повторного скачивания файлов
        """
        cursor = self.conn.cursor()

        # SQL: Запрос недокачанных файлов
        if source:
            cursor.execute("""
                SELECT * FROM files
                WHERE source = ? AND status IN ('incomplete', 'pending')
                ORDER BY first_seen DESC
            """, (source,))
        else:
            cursor.execute("""
                SELECT * FROM files
                WHERE status IN ('incomplete', 'pending')
                ORDER BY first_seen DESC
            """)

        rows = cursor.fetchall()

        # ПРОВЕРКА: Дополнительно проверяем существование файлов
        incomplete = []
        for row in rows:
            file_dict = dict(row)

            # Если filepath указан - проверяем существование
            if file_dict['filepath']:
                filepath = Path(file_dict['filepath'])

                # Файл отсутствует на диске
                if not filepath.exists():
                    file_dict['reason'] = 'missing'
                    incomplete.append(file_dict)

                # Размер не совпадает
                elif not self.is_file_complete(filepath, file_dict['expected_size']):
                    file_dict['reason'] = 'incomplete'
                    incomplete.append(file_dict)
            else:
                # Файл еще не скачивался
                file_dict['reason'] = 'pending'
                incomplete.append(file_dict)

        return incomplete

    def get_missing_files(self) -> List[Dict]:
        """
        КОМАНДА: Находит файлы которые были скачаны но исчезли с диска

        ВОЗВРАЩАЕТ:
            List[Dict] - список отсутствующих файлов
        """
        cursor = self.conn.cursor()

        # SQL: Находим файлы со статусом 'complete' но отсутствующие
        cursor.execute("""
            SELECT * FROM files
            WHERE status = 'complete' AND filepath IS NOT NULL
        """)

        rows = cursor.fetchall()

        missing = []
        for row in rows:
            file_dict = dict(row)
            filepath = Path(file_dict['filepath'])

            # ПРОВЕРКА: Файл должен существовать
            if not filepath.exists():
                file_dict['reason'] = 'deleted_or_moved'
                missing.append(file_dict)

                # ОБНОВЛЕНИЕ: Меняем статус в БД
                cursor.execute("""
                    UPDATE files
                    SET status = 'missing', last_checked = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (file_dict['id'],))

        if missing:
            self.conn.commit()

        return missing

    def mark_for_redownload(self, file_id: int):
        """
        КОМАНДА: Помечает файл для повторного скачивания

        ЧТО ДЕЛАЕТ:
            Меняет статус на 'pending' и увеличивает счетчик попыток

        ПАРАМЕТРЫ:
            file_id - ID записи в базе
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE files
            SET status = 'pending',
                last_checked = CURRENT_TIMESTAMP,
                download_attempts = download_attempts + 1
            WHERE id = ?
        """, (file_id,))

        self.conn.commit()

        self.logger.info(f"🔄 Файл #{file_id} помечен для повторного скачивания")

    def get_files_by_source(self, source: str, source_id: str) -> List[Dict]:
        """
        КОМАНДА: Получает все файлы из конкретного источника

        ЧТО ДЕЛАЕТ:
            Возвращает все известные файлы из источника

        ПАРАМЕТРЫ:
            source - тип источника (telegram/web/github)
            source_id - ID источника (имя канала/URL)

        ВОЗВРАЩАЕТ:
            List[Dict] - список всех файлов

        ЗАЧЕМ:
            Для сверки со списком файлов в канале/на сайте
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM files
            WHERE source = ? AND source_id = ?
            ORDER BY first_seen DESC
        """, (source, source_id))

        return [dict(row) for row in cursor.fetchall()]

    def _calculate_hash(self, filepath: Path) -> str:
        """
        КОМАНДА: Вычисляет MD5 хеш файла

        ЧТО ДЕЛАЕТ:
            Читает файл блоками и вычисляет MD5

        ПАРАМЕТРЫ:
            filepath - путь к файлу

        ВОЗВРАЩАЕТ:
            str - MD5 хеш в hex формате

        ЗАЧЕМ:
            Для проверки целостности и обнаружения дубликатов
        """
        md5 = hashlib.md5()

        try:
            with open(filepath, 'rb') as f:
                # ЧТЕНИЕ: Читаем файл блоками по 8KB
                for chunk in iter(lambda: f.read(8192), b''):
                    md5.update(chunk)

            return md5.hexdigest()

        except Exception as e:
            self.logger.error(f"❌ Ошибка вычисления хеша {filepath}: {e}")
            return None

    def get_stats(self) -> Dict:
        """
        КОМАНДА: Возвращает статистику по всем файлам

        ВОЗВРАЩАЕТ:
            Dict со статистикой:
                - total: всего записей
                - complete: полных файлов
                - incomplete: недокачанных
                - missing: отсутствующих
                - pending: ожидающих скачивания
                - by_source: статистика по источникам
        """
        cursor = self.conn.cursor()

        # ОБЩАЯ СТАТИСТИКА
        cursor.execute("SELECT COUNT(*) as total FROM files")
        total = cursor.fetchone()['total']

        # ПО СТАТУСАМ
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM files
            GROUP BY status
        """)

        status_stats = {row['status']: row['count'] for row in cursor.fetchall()}

        # ПО ИСТОЧНИКАМ
        cursor.execute("""
            SELECT source, COUNT(*) as count, SUM(actual_size) as total_size
            FROM files
            GROUP BY source
        """)

        source_stats = {}
        for row in cursor.fetchall():
            source_stats[row['source']] = {
                'count': row['count'],
                'total_size': row['total_size'] or 0
            }

        return {
            'total': total,
            'complete': status_stats.get('complete', 0),
            'incomplete': status_stats.get('incomplete', 0),
            'missing': status_stats.get('missing', 0),
            'pending': status_stats.get('pending', 0),
            'by_source': source_stats
        }

    def cleanup_old_records(self, days: int = 30):
        """
        КОМАНДА: Удаляет старые записи о пропущенных файлах

        ЧТО ДЕЛАЕТ:
            Удаляет записи старше N дней со статусом 'missing'

        ПАРАМЕТРЫ:
            days - количество дней для хранения

        ЗАЧЕМ:
            База не разрастается бесконечно
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            DELETE FROM files
            WHERE status = 'missing'
            AND julianday('now') - julianday(last_checked) > ?
        """, (days,))

        deleted = cursor.rowcount
        self.conn.commit()

        if deleted > 0:
            self.logger.info(f"🧹 Удалено старых записей: {deleted}")

    def close(self):
        """
        КОМАНДА: Закрывает соединение с базой данных
        """
        if self.conn:
            self.conn.close()
            self.logger.debug("✅ Соединение с БД закрыто")

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста"""
        self.close()
