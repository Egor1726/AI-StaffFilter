import json
import os
import chromadb
from agent import rank_candidates
from config import CHROMA_DB_PATH, COLLECTION_NAME


def get_all_candidates_from_chroma() -> list:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.isabs(CHROMA_DB_PATH):
        chroma_path = CHROMA_DB_PATH
    else:
        chroma_path = os.path.normpath(os.path.join(base_dir, CHROMA_DB_PATH))

    client = chromadb.PersistentClient(path=chroma_path)
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

vacancy_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_data", "vacancy.txt"))
with open(vacancy_path, "r", encoding="utf-8") as f:
    vacancy = f.read()

print("Загружаем кандидатов из ChromaDB...")
candidates = get_all_candidates_from_chroma()
TEST_LIMIT = 3
candidates = candidates[:TEST_LIMIT]
print(f"Найдено кандидатов: {len(candidates)}\n")
print("=" * 50)

ranked = rank_candidates(candidates, vacancy)

for c in ranked:
    meta = c["metadata"]
    eval_ = c["evaluation"]

    print(f"\n#{c['rank']} {meta['name']}")
    print(f"Позиция:  {meta.get('position', '—')}")
    print(f"Опыт:     {meta.get('experience_years', '—')} лет")
    print(f"Зарплата: {meta.get('expected_salary', '—')}")
    print(f"Email:    {meta.get('email', '—')}")
    print(f"Телефон:  {meta.get('phone', '—')}")
    print(f"Score:    {c['score']}")
    print(f"Навыки:   {', '.join(eval_.get('matched_skills', []))}")
    print(f"Не хватает: {', '.join(eval_.get('missing_skills', []))}")
    print(f"Комментарий: {eval_.get('comment', '—')}")
    print("=" * 50)