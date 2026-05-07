import json
import chromadb
import ollama

from config import (
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    EMBED_MODEL
)

from preprocessor import Preprocessor


# ------------------------
# CHROMA
# ------------------------

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_collection():
    return client.get_or_create_collection(name=COLLECTION_NAME)


# ------------------------
# EMBEDDING
# ------------------------

def get_embedding(text: str):
    response = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text
    )
    return response["embedding"]


def build_embedding_text(profile: dict):
    parts = []

    # Проверка позиции
    if profile.get("position"):
        parts.append(str(profile["position"]))

    # Безопасное извлечение скиллов
    skills = profile.get("skills")
    if isinstance(skills, dict):
        # Используем "or []" на случай, если в JSON пришло "hard": null
        hard_skills = skills.get("hard") or []
        tools = skills.get("tools") or []
        
        # Проверяем, что это именно списки, прежде чем делать extend
        if isinstance(hard_skills, list):
            parts.extend([str(s) for s in hard_skills])
        if isinstance(tools, list):
            parts.extend([str(t) for t in tools])

    # Опыт
    if profile.get("experience_years") is not None:
        parts.append(f"{profile['experience_years']} years experience")

    # Саммари
    if profile.get("summary"):
        parts.append(str(profile["summary"])[:500])

    return " ".join(parts)


def build_vacancy_embedding(vacancy: dict):
    parts = []

    if vacancy.get("position"):
        parts.append(str(vacancy["position"]))

    # Защита от null в required_skills
    req_skills = vacancy.get("required_skills") or []
    if isinstance(req_skills, list):
        parts.extend([str(s) for s in req_skills])

    if vacancy.get("required_experience") is not None:
        parts.append(f"{vacancy['required_experience']} years experience")

    if vacancy.get("description"):
        parts.append(str(vacancy["description"])[:500])

    return " ".join(parts)


# ------------------------
# Вспомогательная функция для ChromaDB
# ------------------------

def flatten_metadata(data: dict) -> dict:
    """Превращает вложенные словари и списки в строки для ChromaDB."""
    flat = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            # Сохраняем сложные структуры как JSON-строки
            flat[key] = json.dumps(value, ensure_ascii=False)
        elif value is None:
            # ChromaDB может не любить None в некоторых версиях, превращаем в пустую строку или null
            flat[key] = ""
        else:
            flat[key] = value
    return flat


# ------------------------
# ADD RESUME
# ------------------------

def add_resume(doc_id: str, raw_text: str):
    collection = get_collection()
    pre = Preprocessor()

    # 1. Получаем распарсенный профиль
    profile = pre.process_resume(raw_text)
    if not profile:
        print(f"  [SKIP] {doc_id}: модель не смогла распарсить текст")
        return

    # 2. Подготавливаем текст для эмбеддинга
    embedding_text = build_embedding_text(profile)
    embedding = get_embedding(embedding_text)

    if not embedding or len(embedding) == 0:
        print(f"  [SKIP] {doc_id}: не удалось получить эмбеддинг")
        return

    # 3. Подготавливаем плоские метаданные для фильтрации
    # Оставляем только простые типы для работы фильтров Chroma
    metadata = {
        "position": str(profile.get("position", "")),
        "experience_years": profile.get("experience_years", 0) or 0,
        "level": str(profile.get("level", ""))
    }

    # 4. Сохраняем в ChromaDB
    try:
        # Используем upsert вместо add, чтобы не падать на дубликатах ID
        collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            # В documents кладем ПОЛНЫЙ JSON строкой - его будем читать в поиске
            documents=[json.dumps(profile, ensure_ascii=False)],
            metadatas=[metadata]
        )
    except Exception as e:
        print(f"  [ERROR] {doc_id} при добавлении в базу: {e}")

# ------------------------
# ADD VACANCY
# ------------------------

def add_vacancy(doc_id: str, raw_text: str):
    collection = get_collection()
    pre = Preprocessor()

    # 1. Получаем распарсенную вакансию
    vacancy = pre.process_vacancy(raw_text)

    # 2. Подготавливаем текст для эмбеддинга
    embedding_text = build_vacancy_embedding(vacancy)
    embedding = get_embedding(embedding_text)

    # 3. Подготавливаем плоские метаданные
    metadata = flatten_metadata(vacancy)

    # 4. Сохраняем в ChromaDB
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[json.dumps(vacancy, ensure_ascii=False)],
        metadatas=[metadata]
    )