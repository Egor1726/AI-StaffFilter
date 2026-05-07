import os
from dotenv import load_dotenv

# =====================
# LOAD ENV
# =====================
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# =====================
# MODELS
# =====================
# Llama 3.1 8B — идеальна для быстрого логического фильтра (Fast)[cite: 1]
# Qwen 2.5 14B — мощная модель для глубокого технического анализа (Smart)[cite: 1]

MODELS = {
    "fast": {
        "name": os.getenv("FAST_MODEL", "llama3.1:8b"), 
        "temperature": float(os.getenv("FAST_TEMP", 0.2))
    },
    "smart": {
        "name": os.getenv("SMART_MODEL", "qwen2.5:14b"),
        "temperature": float(os.getenv("SMART_TEMP", 0.3))
    }
}

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

# =====================
# SEARCH SETTINGS
# =====================
TOP_K_INITIAL = int(os.getenv("TOP_K_INITIAL", 40)) 
TOP_K_FINAL   = int(os.getenv("TOP_K_FINAL", 10))   # Оставляем только самый сок

SIMILARITY_THRESHOLD = float(os.getenv("SIM_THRESHOLD", 0.3)) # Повышаем планку для векторов

# Порог фильтра первой модели: Llama 3.1 8B очень хорошо обосновывает отказ[cite: 4]
FAST_FILTER_THRESHOLD = float(os.getenv("FAST_FILTER_THRESHOLD", 45)) 

# =====================
# LLM SETTINGS (Контроль токенов)
# =====================
FAST_MAX_TOKENS = int(os.getenv("FAST_MAX_TOKENS", 600)) 

SMART_MAX_TOKENS = int(os.getenv("SMART_MAX_TOKENS", 2000)) 

LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 60))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# =====================
# DEBUG & CACHE
# =====================
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

if DEBUG:
    print("\n[UPGRADED CONFIG]")
    print(f"  FAST_MODEL (Llama 3.1): {FAST_MODEL}")
    print(f"  SMART_MODEL (Qwen 14B): {SMART_MODEL}")
    print(f"  FAST_FILTER_THRESHOLD: {FAST_FILTER_THRESHOLD}")
    print(f"  TIMEOUT: {LLM_TIMEOUT}s")