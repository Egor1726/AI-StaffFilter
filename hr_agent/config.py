import os
from dotenv import load_dotenv

# Загружаем переменные из .env в корне проекта
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "resumes")

print(f"Конфигурация загружена:")
print(f"  Модель: {MODEL_NAME}")
print(f"  Путь к ChromaDB: {CHROMA_DB_PATH}")
print(f"  Коллекция: {COLLECTION_NAME}")