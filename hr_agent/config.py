import os
from dotenv import load_dotenv

# Загружаем переменные из .env в корне проекта
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
TOP_K = int(os.getenv("TOP_K", "5"))

print(f"Конфигурация загружена:")
print(f"  Модель: {MODEL_NAME}")
print(f"  Путь к ChromaDB: {CHROMA_DB_PATH}")
print(f"  Top K: {TOP_K}")