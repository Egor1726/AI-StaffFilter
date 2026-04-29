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
        "name": os.getenv("FAST_MODEL", "llama3:8b"),
        "temperature": float(os.getenv("FAST_TEMP", 0.1))
    },
    "smart": {
        "name": os.getenv("SMART_MODEL", "qwen:14b"),
        "temperature": float(os.getenv("SMART_TEMP", 0.2))
    }
}

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

TOP_K_INITIAL = int(os.getenv("TOP_K_INITIAL", 50))   # сколько берем из Chroma
TOP_K_FINAL   = int(os.getenv("TOP_K_FINAL", 15))     # сколько в финал

SIMILARITY_THRESHOLD = float(os.getenv("SIM_THRESHOLD", 0.2))

# =====================
# LLM SETTINGS
# =====================

LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 120))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

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
    print(f"  FAST_MODEL: {MODELS['fast']['name']}")
    print(f"  SMART_MODEL: {MODELS['smart']['name']}")
    print(f"  CHROMA_DB_PATH: {CHROMA_DB_PATH}")
    print(f"  COLLECTION: {COLLECTION_NAME}")
    print(f"  TOP_K_INITIAL: {TOP_K_INITIAL}")
    print(f"  TOP_K_FINAL: {TOP_K_FINAL}")