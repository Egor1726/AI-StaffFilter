import os
from dotenv import load_dotenv

# =====================
# LOAD ENV
# =====================

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# =====================
# MODELS
# =====================

MODELS = {
    "fast": {
        "name": os.getenv("FAST_MODEL", "qwen2.5:1.5b"),
        "temperature": float(os.getenv("FAST_TEMP", 0.0))
    },
    "smart": {
        "name": os.getenv("SMART_MODEL", "qwen2.5:3b"),
        "temperature": float(os.getenv("SMART_TEMP", 0.1))
    }
}

# 👉 ДОБАВЛЯЕМ удобные алиасы (чтобы не лезть в dict везде)
FAST_MODEL = MODELS["fast"]["name"]
SMART_MODEL = MODELS["smart"]["name"]

FAST_TEMP = MODELS["fast"]["temperature"]
SMART_TEMP = MODELS["smart"]["temperature"]

# =====================
# EMBEDDINGS
# =====================

EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# =====================
# INFRA
# =====================

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "resumes")

# 👉 полезно: разделить коллекции (опционально)
RESUME_COLLECTION = os.getenv("RESUME_COLLECTION", "resumes")
VACANCY_COLLECTION = os.getenv("VACANCY_COLLECTION", "vacancies")

# =====================
# SEARCH SETTINGS
# =====================

TOP_K_INITIAL = int(os.getenv("TOP_K_INITIAL", 50))
TOP_K_FINAL   = int(os.getenv("TOP_K_FINAL", 15))

SIMILARITY_THRESHOLD = float(os.getenv("SIM_THRESHOLD", 0.2))

# 👉 НОВОЕ: порог фильтра первой модели
FAST_FILTER_THRESHOLD = float(os.getenv("FAST_FILTER_THRESHOLD", 50))

# =====================
# LLM SETTINGS
# =====================

LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 120))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# 👉 НОВОЕ: контроль токенов
FAST_MAX_TOKENS = int(os.getenv("FAST_MAX_TOKENS", 200))
SMART_MAX_TOKENS = int(os.getenv("SMART_MAX_TOKENS", 4096))

# =====================
# CACHE (очень важно)
# =====================

ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"

# =====================
# DEBUG
# =====================

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# =====================
# LOG
# =====================

if DEBUG:
    print("\n[CONFIG]")
    print(f"  OLLAMA_HOST: {OLLAMA_HOST}")
    print(f"  EMBED_MODEL: {EMBED_MODEL}")
    print(f"  FAST_MODEL: {FAST_MODEL}")
    print(f"  SMART_MODEL: {SMART_MODEL}")
    print(f"  CHROMA_DB_PATH: {CHROMA_DB_PATH}")
    print(f"  COLLECTION: {COLLECTION_NAME}")
    print(f"  TOP_K_INITIAL: {TOP_K_INITIAL}")
    print(f"  TOP_K_FINAL: {TOP_K_FINAL}")
    print(f"  FAST_FILTER_THRESHOLD: {FAST_FILTER_THRESHOLD}")