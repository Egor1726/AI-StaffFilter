import requests
import chromadb
from config import OLLAMA_URL, EMBED_MODEL, CHROMA_PATH, COLLECTION_NAME


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)


def get_embedding(text: str) -> list[float]:
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]


def add_resume(doc_id: str, text: str, metadata: dict) -> None:
    """
    metadata должен содержать:
    {
        "name":       "Иван Иванов",
        "position":   "Python разработчик",
        "email":      "ivan@mail.ru",
        "phone":      "+7 999 123 45 67",
        "experience": 3,          # число (лет)
        "education":  "МГУ, ВМК",
        "skills":     "Python, Django, PostgreSQL",
        "salary":     150000      # число (рублей)
    }
    """
    collection = get_collection()
    embedding  = get_embedding(text)

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )
    print(f"[indexer] Добавлено: {metadata.get('name', doc_id)}")


def search(query: str) -> list[dict]:
    collection = get_collection()
    embedding  = get_embedding(query)

    total = collection.count()  # сколько резюме всего в базе

    results = collection.query(
        query_embeddings=[embedding],
        n_results=total,          # ← все резюме
        include=["documents", "metadatas", "distances"]
    )

    candidates = []
    for i in range(len(results["ids"][0])):
        score = round(1 - results["distances"][0][i], 3)  # чем больше — тем лучше
        candidates.append({
            "score":      score,
            "name":       results["metadatas"][0][i].get("name"),
            "position":   results["metadatas"][0][i].get("position"),
            "email":      results["metadatas"][0][i].get("email"),
            "phone":      results["metadatas"][0][i].get("phone"),
            "experience": results["metadatas"][0][i].get("experience"),
            "education":  results["metadatas"][0][i].get("education"),
            "skills":     results["metadatas"][0][i].get("skills"),
            "salary":     results["metadatas"][0][i].get("salary"),
        })

    # Сортировка по баллам — от лучшего к худшему
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


def delete_resume(doc_id: str) -> None:
    collection = get_collection()
    collection.delete(ids=[doc_id])

