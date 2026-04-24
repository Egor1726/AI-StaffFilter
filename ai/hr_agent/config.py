import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "resumes")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

print(f"Конфигурация загружена:")
print(f"  Модель: {MODEL_NAME}")
print(f"  Путь к ChromaDB: {CHROMA_DB_PATH}")
print(f"  Коллекция: {COLLECTION_NAME}")