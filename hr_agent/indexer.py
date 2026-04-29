import requests
import chromadb
from typing import List, Dict, Any

from config import OLLAMA_HOST, EMBED_MODEL, CHROMA_DB_PATH, COLLECTION_NAME
from preprocessor import Preprocessor


# =====================
# INIT
# =====================

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)


# =====================
# EMBEDDINGS
# =====================

def get_embedding(text: str) -> List[float]:
    response = requests.post(
        f"{OLLAMA_HOST}/api/embed",
        json={
            "model": EMBED_MODEL,
            "input": text
        }
    )
    response.raise_for_status()
    return response.json()["embeddings"][0]


# =====================
# PROFILE BUILDER
# =====================

def build_candidate_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    skills = list(set([s.lower().strip() for s in data.get("skills", [])]))

    experience = data.get("experience_years") or 0
    position = data.get("position") or ""

    embedding_text = build_embedding_text(
        skills,
        experience,
        position,
        data.get("summary"),
        data.get("experience", [])
    )

    return {
        "name": data.get("name"),
        "position": position,
        "experience_years": experience,
        "education": data.get("education"),
        "skills": skills,
        "languages": data.get("languages"),
        "summary": data.get("summary"),

        # ключевое
        "embedding_text": embedding_text
    }


def build_embedding_text(
    skills,
    experience,
    position,
    summary,
    experience_list
) -> str:

    parts = []

    if position:
        parts.append(f"Position: {position}")

    if skills:
        parts.append(f"Skills: {', '.join(skills)}")

    parts.append(f"Experience: {experience} years")

    if summary:
        parts.append(f"Summary: {summary}")

    if experience_list:
        companies = [e.get("company") for e in experience_list if e.get("company")]
        if companies:
            parts.append(f"Companies: {', '.join(companies)}")

    return "\n".join(parts)


# =====================
# INDEX ONE RESUME
# =====================

def add_resume(doc_id: str, raw_text: str, preprocessor: Preprocessor) -> None:
    collection = get_collection()

    try:
        # 1. LLM → JSON
        parsed = preprocessor.process_resume(raw_text)

        # 2. JSON → профиль
        profile = build_candidate_profile(parsed)

        # 3. embedding
        embedding = get_embedding(profile["embedding_text"])

        # 4. запись в Chroma
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[profile["embedding_text"]],
            metadatas=[profile]
        )

        print(f"[indexer] Добавлен: {profile.get('name', doc_id)}")

    except Exception as e:
        print(f"[indexer] Ошибка обработки {doc_id}: {e}")


# =====================
# INDEX ALL
# =====================

def index_all(resumes: List[Dict], vacancy_text: str) -> str:
    """
    resumes = [
        {"id": "...", "text": "..."},
        ...
    ]
    """

    preprocessor = Preprocessor()

    for doc in resumes:
        add_resume(doc["id"], doc["text"], preprocessor)

    print(f"[indexer] Проиндексировано: {len(resumes)} резюме")

    return vacancy_text


# =====================
# SEARCH
# =====================

def search(query: str, top_k: int = 50) -> List[Dict]:
    collection = get_collection()

    total = collection.count()

    if total == 0:
        print("[indexer] База пуста")
        return []

    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, total),
        include=["documents", "metadatas", "distances"]
    )

    candidates = []

    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        score = round(1 - results["distances"][0][i], 3)

        candidates.append({
            "score": score,
            "candidate": meta
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    return candidates


# =====================
# DELETE
# =====================

def delete_resume(doc_id: str) -> None:
    collection = get_collection()
    collection.delete(ids=[doc_id])
    print(f"[indexer] Удалено: {doc_id}")


# =====================
# RUN
# =====================

if __name__ == "__main__":
    print("[indexer] Пример запуска...")

    resumes = [
        {"id": "1", "text": "пример резюме 1"},
        {"id": "2", "text": "пример резюме 2"},
    ]

    index_all(resumes, "пример вакансии")