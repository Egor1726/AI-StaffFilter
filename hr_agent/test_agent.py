import json
import chromadb
from agent import evaluate_candidate, rank_candidates
from config import CHROMA_DB_PATH, COLLECTION_NAME

# ─────────────────────────────────────────────
# Получение кандидатов из ChromaDB
# ─────────────────────────────────────────────

def get_all_candidates_from_chroma() -> list:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.get(
        include=["documents", "metadatas"]
    )

    candidates = []
    for i in range(len(results["ids"])):
        candidates.append({
            "id": results["ids"][i],
            "text": results["documents"][i],
            "metadata": results["metadatas"][i]
        })

    return candidates

# ─────────────────────────────────────────────
# Тест
# ─────────────────────────────────────────────

with open("test_data/vacancy.txt", "r", encoding="utf-8") as f:
    vacancy = f.read()

print("Загружаем кандидатов из ChromaDB...")
candidates = get_all_candidates_from_chroma()
print(f"Найдено кандидатов: {len(candidates)}\n")

print("=" * 50)
ranked = rank_candidates(candidates, vacancy)

for c in ranked:
    print(f"\n#{c['rank']} {c['metadata']['name']}")
    print(f"Score: {c['score']}")
    print(f"Verdict: {c['evaluation'].get('verdict', '—')}")
    print(f"Comment: {c['evaluation'].get('comment', '—')}")
    print("=" * 50)