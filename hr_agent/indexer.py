import requests
import chromadb
from config import OLLAMA_HOST, CHROMA_DB_PATH, COLLECTION_NAME
from txt_processor import process_files


# ── Инициализация ──────────────────────────────────────────

def get_collection():
    """Возвращает (или создаёт) коллекцию ChromaDB."""
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)


# ── Эмбеддинги ─────────────────────────────────────────────

def get_embedding(text: str) -> list[float]:
    """Превращает текст в вектор через Ollama."""
    response = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]


# ── Индексация ─────────────────────────────────────────────

def add_resume(doc_id: str, text: str, metadata: dict) -> None:
    """
    Добавляет одно резюме в ChromaDB.
    Вызывается из index_all() для каждого кандидата.
    """
    collection = get_collection()
    embedding = get_embedding(text)

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )
    print(f"[indexer] Добавлен: {metadata.get('name', doc_id)}")


def index_all(resumes_path: str, vacancy_path: str) -> str:
    """
    Главная функция индексации.
    Читает файлы через txt_processor, векторизирует и кладёт в ChromaDB.

    Возвращает текст вакансии — для агента (Человек 3).
    """
    documents, vacancy_text = process_files(resumes_path, vacancy_path)

    for doc in documents:
        add_resume(doc["id"], doc["text"], doc["metadata"])

    print(f"[indexer] Проиндексировано: {len(documents)} резюме")
    return vacancy_text


# ── Поиск ──────────────────────────────────────────────────

def search(query: str) -> list[dict]:
    """
    Ищет всех кандидатов и возвращает их отсортированными по score.
    Вызывается агентом (Человек 3).

    Args:
        query: текст вакансии или поисковый запрос

    Returns:
        список всех кандидатов, отсортированных по релевантности (score 0.0–1.0)
    """
    collection = get_collection()
    total = collection.count()

    if total == 0:
        print("[indexer] База пуста — сначала запусти index_all()")
        return []

    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=total,
        include=["documents", "metadatas", "distances"]
    )

    candidates = []
    for i in range(len(results["ids"][0])):
        score = round(1 - results["distances"][0][i], 3)
        meta  = results["metadatas"][0][i]

        candidates.append({
            "score":            score,
            "name":             meta.get("name"),
            "position":         meta.get("position"),
            "email":            meta.get("email"),
            "phone":            meta.get("phone"),
            "experience_years": meta.get("experience_years"),
            "education":        meta.get("education"),
            "skills":           meta.get("skills"),
            "expected_salary":  meta.get("expected_salary"),
        })

    # Сортировка: лучшие кандидаты наверху
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


def delete_resume(doc_id: str) -> None:
    """Удаляет резюме из базы по ID."""
    collection = get_collection()
    collection.delete(ids=[doc_id])
    print(f"[indexer] Удалено: {doc_id}")


# ── Тест ───────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Индексируем все резюме
    vacancy_text = index_all("data/resumes.txt", "data/vacancy.txt")

    # 2. Ищем по тексту вакансии
    print("\n── Результаты поиска ────────────────────────────")
    results = search(vacancy_text)

    for r in results:
        print(f"{r['score']} | {r['name']} | {r['position']} | {r['skills']}")