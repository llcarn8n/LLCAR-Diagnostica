"""
═══════════════════════════════════════════════════════════════════════════════
                    ОРГАНИЗАЦИЯ ФАЙЛОВ ПО ПАПКАМ
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import Tuple

from .car_brands import detect_brand, detect_document_type, get_all_brands, DOCUMENT_TYPES

logger = logging.getLogger(__name__)


class FileOrganizer:
    """Класс для организации скачанных файлов по папкам"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self._create_structure()
    
    def _create_structure(self):
        """Создаёт структуру папок"""
        logger.info(f"📁 Создание структуры папок в {self.base_path}")
        
        # Базовая папка
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Папки для каждой марки
        for brand in get_all_brands():
            brand_path = self.base_path / brand
            brand_path.mkdir(exist_ok=True)
            
            # Подпапки для типов документов
            for doc_type in DOCUMENT_TYPES.keys():
                (brand_path / doc_type).mkdir(exist_ok=True)
        
        # Папка для неопределённых марок
        other_path = self.base_path / 'Другие марки'
        other_path.mkdir(exist_ok=True)
        for doc_type in DOCUMENT_TYPES.keys():
            (other_path / doc_type).mkdir(exist_ok=True)
        
        # Служебные папки
        (self.base_path / '_temp').mkdir(exist_ok=True)
        (self.base_path / '_duplicates').mkdir(exist_ok=True)
        
        logger.info("✅ Структура папок создана")
    
    def _sanitize_filename(self, filename: str, max_length: int = 200) -> str:
        """Очищает имя файла"""
        invalid_chars = '<>:"/\\|?*\n\r\t'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = re.sub(r'[_\s]+', ' ', filename).strip()
        filename = filename.lstrip('.')
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext
        return filename if filename else 'unnamed'
    
    def get_target_path(self, filename: str, description: str = '') -> Tuple[Path, str, str]:
        """Определяет целевой путь для файла"""
        search_text = f"{filename} {description}"
        
        brand = detect_brand(search_text)
        doc_type = detect_document_type(search_text)
        
        target_folder = self.base_path / brand / doc_type
        
        return target_folder, brand, doc_type
    
    def organize_file(self, source_path: Path, filename: str = None, description: str = '') -> Path:
        """Перемещает файл в соответствующую папку"""
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Файл не найден: {source_path}")
        
        if filename is None:
            filename = source_path.name
        
        filename = self._sanitize_filename(filename)
        
        target_folder, brand, doc_type = self.get_target_path(filename, description)
        target_path = target_folder / filename
        
        # Проверка на дубликат
        if target_path.exists():
            if source_path.stat().st_size == target_path.stat().st_size:
                logger.debug(f"Дубликат: {filename}")
                dup_path = self.base_path / '_duplicates' / filename
                counter = 1
                while dup_path.exists():
                    name, ext = os.path.splitext(filename)
                    dup_path = self.base_path / '_duplicates' / f"{name}_{counter}{ext}"
                    counter += 1
                shutil.move(str(source_path), str(dup_path))
                return dup_path
            else:
                counter = 1
                name, ext = os.path.splitext(filename)
                while target_path.exists():
                    target_path = target_folder / f"{name}_{counter}{ext}"
                    counter += 1
        
        # Перемещаем
        shutil.move(str(source_path), str(target_path))
        logger.debug(f"Организовано: {filename} -> {brand}/{doc_type}")
        
        return target_path
    
    def get_stats(self) -> dict:
        """Возвращает статистику по папкам"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_brand': {},
            'by_type': {},
        }
        
        for brand_folder in self.base_path.iterdir():
            if brand_folder.is_dir() and not brand_folder.name.startswith('_'):
                brand_name = brand_folder.name
                stats['by_brand'][brand_name] = {'files': 0, 'size': 0}
                
                for type_folder in brand_folder.iterdir():
                    if type_folder.is_dir():
                        type_name = type_folder.name
                        if type_name not in stats['by_type']:
                            stats['by_type'][type_name] = {'files': 0, 'size': 0}
                        
                        for file in type_folder.iterdir():
                            if file.is_file():
                                size = file.stat().st_size
                                stats['total_files'] += 1
                                stats['total_size'] += size
                                stats['by_brand'][brand_name]['files'] += 1
                                stats['by_brand'][brand_name]['size'] += size
                                stats['by_type'][type_name]['files'] += 1
                                stats['by_type'][type_name]['size'] += size
        
        return stats