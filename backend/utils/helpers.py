"""
═══════════════════════════════════════════════════════════════════════════════
                    ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import re
from pathlib import Path


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """Очищает имя файла от недопустимых символов"""
    invalid_chars = '<>:"/\\|?*\n\r\t'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = re.sub(r'[_\s]+', ' ', filename).strip()
    filename = filename.lstrip('.')
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    return filename if filename else 'unnamed'


def format_size(size_bytes: int) -> str:
    """Форматирует размер файла"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} ПБ"


def ensure_dir(path: Path) -> Path:
    """Создаёт директорию, если она не существует"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_archive(filename: str) -> bool:
    """Проверяет, является ли файл архивом"""
    archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
    _, ext = os.path.splitext(filename.lower())
    return ext in archive_extensions


def is_document(filename: str) -> bool:
    """Проверяет, является ли файл документом"""
    doc_extensions = ['.pdf', '.doc', '.docx', '.djvu', '.epub', '.xls', '.xlsx']
    _, ext = os.path.splitext(filename.lower())
    return ext in doc_extensions