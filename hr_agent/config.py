import os
from dotenv import load_dotenv

# Загружаем переменные из .env в корне проекта
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
# Параметры генерации — оптимизированы для структурированного вывода (JSON)
# Чем ниже temperature, тем стабильнее формат, но меньше вариативности
MODEL_OPTIONS = {
    "temperature": 0.1,      # Минимум креатива → стабильный JSON
    "top_p": 0.9,            # Баланс разнообразия токенов
    "repeat_penalty": 1.1,   # Предотвращает зацикливание на словах
    "num_predict": 500       # Лимит токенов ответа (хватит на JSON + комментарий)
}
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "resumes")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

print(f"Конфигурация загружена:")
print(f"  Модель: {MODEL_NAME}")
print(f"  Путь к ChromaDB: {CHROMA_DB_PATH}")
print(f"  Опции модели: {MODEL_OPTIONS}")
print(f"  Коллекция: {COLLECTION_NAME}")