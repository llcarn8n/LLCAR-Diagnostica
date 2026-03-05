#!/usr/bin/env python3
"""
LLCAR Diagnostica — Построение ChromaDB индекса.

Загружает chunks-unified.json, генерирует embeddings через
sentence-transformers (multilingual), индексирует в ChromaDB.

Вход:  knowledge-base/chunks-unified.json
Выход: chromadb_data/ (персистентная ChromaDB)
"""

import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'api'))
from config import KB_DIR, CHROMADB_PATH, COLLECTION_NAME, EMBEDDING_MODEL

# ═══════════════════════════════════════════════════════════
# Зависимости
# ═══════════════════════════════════════════════════════════

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Требуется: pip install chromadb")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Требуется: pip install sentence-transformers")
    sys.exit(1)


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_index():
    print("=" * 60)
    print("LLCAR KB — Построение ChromaDB индекса")
    print("=" * 60)

    # 1. Загружаем чанки
    chunks_path = os.path.join(KB_DIR, 'chunks-unified.json')
    if not os.path.exists(chunks_path):
        print(f"[!] {chunks_path} не найден. Запустите chunk_and_normalize.py сначала.")
        sys.exit(1)

    data = load_json(chunks_path)
    chunks = data.get('chunks', [])
    print(f"  Чанков для индексации: {len(chunks)}")

    if not chunks:
        print("[!] Нет чанков для индексации.")
        sys.exit(1)

    # 2. Инициализация embedding модели
    print(f"\n--- Загрузка embedding модели: {EMBEDDING_MODEL} ---")
    t0 = time.time()
    st_model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"  Модель загружена за {time.time() - t0:.1f} сек")

    # ChromaDB embedding function (обёртка)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    # 3. Создание/очистка ChromaDB
    print(f"\n--- Инициализация ChromaDB: {CHROMADB_PATH} ---")
    os.makedirs(CHROMADB_PATH, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMADB_PATH)

    # Удаляем старую коллекцию если есть
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"  Удалена старая коллекция '{COLLECTION_NAME}'")
    except Exception:
        pass  # Коллекция не существовала — нормально

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"  Создана коллекция '{COLLECTION_NAME}'")

    # 4. Индексация пакетами
    BATCH_SIZE = 100
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\n--- Индексация ({len(chunks)} чанков, батчи по {BATCH_SIZE}) ---")
    t0 = time.time()

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(chunks))
        batch = chunks[start:end]

        ids = []
        documents = []
        metadatas = []

        for chunk in batch:
            # Документ для embedding: title + content (для семантического поиска)
            doc_text = chunk['title'] + '\n' + chunk['content'][:1500]

            # Метаданные для фильтрации
            meta = {
                'vehicle': chunk.get('vehicle', 'both'),
                'layer': chunk.get('layer', 'general'),
                'content_type': chunk.get('contentType', 'manual'),
                'language': chunk.get('language', 'ru'),
                'source': chunk.get('source', ''),
                'title': chunk.get('title', '')[:500],
                'page_start': chunk.get('pageStart', 0),
                'page_end': chunk.get('pageEnd', 0),
                'source_url': chunk.get('sourceUrl', '')[:500],
                'glossary_ids': json.dumps(chunk.get('glossaryIds', []), ensure_ascii=False),
                'dtc_codes': json.dumps(chunk.get('dtcCodes', []), ensure_ascii=False),
                'has_procedures': chunk.get('hasProcedures', False),
                'has_warnings': chunk.get('hasWarnings', False),
            }

            ids.append(chunk['id'])
            documents.append(doc_text)
            metadatas.append(meta)

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        elapsed = time.time() - t0
        pct = (end / len(chunks)) * 100
        print(f"  [{batch_idx + 1}/{total_batches}] {end}/{len(chunks)} ({pct:.0f}%) — {elapsed:.1f} сек")

    elapsed_total = time.time() - t0
    print(f"\n  Индексация завершена за {elapsed_total:.1f} сек")

    # 5. Проверка
    print(f"\n--- Проверка ---")
    count = collection.count()
    print(f"  Документов в коллекции: {count}")

    # Тестовый запрос
    test_queries = [
        "тормозная система",
        "battery charging",
        "空调系统",
    ]
    for q in test_queries:
        results = collection.query(
            query_texts=[q],
            n_results=3,
        )
        titles = [m['title'][:60] for m in results['metadatas'][0]] if results['metadatas'] else []
        print(f"  Запрос '{q}': {len(titles)} результатов → {titles}")

    # 6. Статистика
    print(f"\n{'=' * 60}")
    print(f"ChromaDB индекс создан:")
    print(f"  Путь: {CHROMADB_PATH}")
    print(f"  Коллекция: {COLLECTION_NAME}")
    print(f"  Документов: {count}")
    print(f"  Embedding модель: {EMBEDDING_MODEL}")

    # Закрываем клиент для корректного сохранения индекса
    del collection
    del client
    import gc
    gc.collect()
    time.sleep(2)

    # Размер на диске
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(CHROMADB_PATH):
        for f in filenames:
            total_size += os.path.getsize(os.path.join(dirpath, f))
    print(f"  Размер на диске: {total_size / (1024 * 1024):.1f} МБ")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    build_index()
