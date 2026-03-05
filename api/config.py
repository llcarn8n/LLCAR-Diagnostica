"""
LLCAR Diagnostica — конфигурация KB API.
"""
import os

# Базовая директория проекта (Diagnostica/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути к данным
CHROMADB_PATH = os.path.join(BASE_DIR, "chromadb_data")
KB_DIR = os.path.join(BASE_DIR, "knowledge-base")
ARCHITECTURE_DIR = os.path.join(BASE_DIR, "architecture")
MINERU_OUTPUT_DIR = os.path.join(BASE_DIR, "mineru-output")

# ChromaDB
COLLECTION_NAME = "llcar_kb"

# Embedding модель (мультиязычная: RU/EN/ZH, 384 dim)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# API настройки
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000"]

# Чанкинг
CHUNK_SIZE_CHARS = 2000        # ~500 токенов
CHUNK_OVERLAP_CHARS = 200      # ~50 токенов

# Поиск
DEFAULT_SEARCH_LIMIT = 20
MAX_SEARCH_LIMIT = 100
