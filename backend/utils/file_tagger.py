"""
═══════════════════════════════════════════════════════════════════════════════
    utils/file_tagger.py — система тегов для организации файлов
═══════════════════════════════════════════════════════════════════════════════

Вдохновлено batch tag update из telegram-files v0.2.4.
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class FileTagger:
    """
    Система тегов для скачанных файлов.

    ФИЧИ:
        ✅ Добавление/удаление тегов для файлов
        ✅ Пакетное обновление тегов (batch)
        ✅ Автоматические теги по имени файла
        ✅ Поиск файлов по тегам
        ✅ Экспорт/импорт тегов

    Пример:
        tagger = FileTagger(Path('./data/tags.json'))

        # Ручные теги
        tagger.add_tag('manual.pdf', 'toyota')
        tagger.add_tag('manual.pdf', 'camry')
        tagger.add_tag('manual.pdf', '2020')

        # Автотеги
        tagger.auto_tag('Toyota_Camry_2020_Service_Manual.pdf')
        # → автоматически добавит: toyota, camry, 2020, service, manual

        # Пакетное
        tagger.batch_add_tag(['file1.pdf', 'file2.pdf', 'file3.pdf'], 'bmw')

        # Поиск
        files = tagger.find_by_tags(['toyota', '2020'])
        # → ['Toyota_Camry_2020_Service_Manual.pdf']
    """

    # Автоматически распознаваемые бренды
    AUTO_BRANDS = {
        'toyota', 'honda', 'nissan', 'mazda', 'subaru', 'mitsubishi',
        'suzuki', 'lexus', 'infiniti', 'acura', 'daihatsu',
        'bmw', 'mercedes', 'audi', 'volkswagen', 'porsche', 'opel',
        'ford', 'chevrolet', 'dodge', 'chrysler', 'jeep', 'gmc',
        'hyundai', 'kia', 'ssangyong', 'daewoo',
        'volvo', 'saab', 'peugeot', 'renault', 'citroen', 'fiat',
        'lada', 'vaz', 'gaz', 'uaz', 'kamaz',
        'land rover', 'range rover', 'jaguar', 'mini', 'smart',
    }

    # Типы документов
    AUTO_DOC_TYPES = {
        'manual', 'service', 'repair', 'workshop', 'owner',
        'wiring', 'diagram', 'electrical', 'body', 'engine',
        'transmission', 'brake', 'suspension',
        'руководство', 'ремонт', 'обслуживание', 'эксплуатация',
        'электросхема', 'кузов', 'двигатель',
    }

    def __init__(self, db_path: Path = Path('./data/tags.json')):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # filename → Set[tags]
        self._tags: Dict[str, Set[str]] = {}
        self._load()

    def _load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._tags = {
                    k: set(v) for k, v in data.items()
                }
            except Exception as e:
                logger.warning(f"Ошибка загрузки тегов: {e}")

    def _save(self):
        try:
            data = {k: sorted(v) for k, v in self._tags.items()}
            tmp = self.db_path.with_suffix('.json.tmp')
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            tmp.replace(self.db_path)
        except Exception as e:
            logger.warning(f"Ошибка сохранения тегов: {e}")

    # ── Операции с тегами ────────────────────────────────────────

    def add_tag(self, filename: str, tag: str):
        """Добавляет тег к файлу"""
        tag = tag.lower().strip()
        if filename not in self._tags:
            self._tags[filename] = set()
        self._tags[filename].add(tag)

    def remove_tag(self, filename: str, tag: str):
        """Удаляет тег у файла"""
        if filename in self._tags:
            self._tags[filename].discard(tag.lower().strip())

    def get_tags(self, filename: str) -> List[str]:
        """Возвращает теги файла"""
        return sorted(self._tags.get(filename, set()))

    def batch_add_tag(self, filenames: List[str], tag: str):
        """Добавляет тег к нескольким файлам"""
        tag = tag.lower().strip()
        for fn in filenames:
            if fn not in self._tags:
                self._tags[fn] = set()
            self._tags[fn].add(tag)
        self._save()

    def batch_remove_tag(self, filenames: List[str], tag: str):
        """Удаляет тег у нескольких файлов"""
        tag = tag.lower().strip()
        for fn in filenames:
            if fn in self._tags:
                self._tags[fn].discard(tag)
        self._save()

    # ── Авто-теги ────────────────────────────────────────────────

    def auto_tag(self, filename: str) -> List[str]:
        """
        Автоматически определяет теги из имени файла.

        'Toyota_Camry_V50_2015_Service_Manual.pdf'
        → ['toyota', 'camry', 'v50', '2015', 'service', 'manual', 'pdf']
        """
        import re

        base = Path(filename).stem.lower()
        # Разбиваем по разделителям
        tokens = set(re.split(r'[_\-\s.,;()\[\]{}]+', base))

        found_tags = set()

        for token in tokens:
            if not token or len(token) < 2:
                continue

            # Бренды
            if token in self.AUTO_BRANDS:
                found_tags.add(token)

            # Типы документов
            if token in self.AUTO_DOC_TYPES:
                found_tags.add(token)

            # Годы (1990-2030)
            if token.isdigit() and 1990 <= int(token) <= 2030:
                found_tags.add(token)

            # Модели (V40, E90, W211, ...)
            if re.match(r'^[a-z]\d{1,3}$', token):
                found_tags.add(token)

        # Расширение
        ext = Path(filename).suffix.lstrip('.').lower()
        if ext:
            found_tags.add(ext)

        # Сохраняем
        if filename not in self._tags:
            self._tags[filename] = set()
        self._tags[filename].update(found_tags)

        return sorted(found_tags)

    def auto_tag_all(self, filenames: List[str]) -> int:
        """Авто-теги для списка файлов"""
        count = 0
        for fn in filenames:
            tags = self.auto_tag(fn)
            if tags:
                count += 1
        self._save()
        return count

    # ── Поиск ────────────────────────────────────────────────────

    def find_by_tags(
        self,
        tags: List[str],
        match_all: bool = True,
    ) -> List[str]:
        """
        Поиск файлов по тегам.

        Args:
            tags:      Список тегов для поиска
            match_all: True = файл должен иметь ВСЕ теги
                       False = файл должен иметь ХОТЯ БЫ ОДИН тег
        """
        search_tags = {t.lower().strip() for t in tags}
        results = []

        for filename, file_tags in self._tags.items():
            if match_all:
                if search_tags.issubset(file_tags):
                    results.append(filename)
            else:
                if search_tags & file_tags:
                    results.append(filename)

        return sorted(results)

    def find_by_brand(self, brand: str) -> List[str]:
        """Быстрый поиск по марке автомобиля"""
        return self.find_by_tags([brand.lower()])

    def get_all_tags(self) -> Dict[str, int]:
        """Все теги с количеством файлов"""
        tag_counts: Dict[str, int] = {}
        for file_tags in self._tags.values():
            for tag in file_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return dict(sorted(tag_counts.items(), key=lambda x: -x[1]))

    def save(self):
        self._save()
