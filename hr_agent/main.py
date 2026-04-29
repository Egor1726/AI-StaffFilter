import os
import json
from glob import glob

from config import (
    TOP_K_INITIAL,
    TOP_K_FINAL,
    FAST_FILTER_THRESHOLD
)

from indexer import (
    add_resume,
    get_collection,
    get_embedding,
    build_vacancy_embedding
)

from preprocessor import Preprocessor
from agent import fast_filter, smart_score


# ------------------------
# LOAD FILES
# ------------------------

# def load_txt_files(folder_path):
#     files = glob(os.path.join(folder_path, "*.txt"))

#     data = []
#     for path in files:
#         with open(path, "r", encoding="utf-8") as f:
#             data.append((os.path.basename(path), f.read()))

#     return data
def load_and_split_resumes(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_resumes = content.split("\n---\n")

    resumes = []
    for i, r in enumerate(raw_resumes):
        if r.strip():
            resumes.append((f"candidate_{i}", r.strip()))

    return resumes


# ------------------------
# INDEX RESUMES
# ------------------------

# def index_resumes(folder_path):
#     resumes = load_txt_files(folder_path)

#     print(f"[INFO] Найдено резюме: {len(resumes)}")

#     for file_name, text in resumes:
#         doc_id = file_name

#         print(f"[INDEX] {doc_id}")

#         add_resume(doc_id, text)
def index_resumes(file_path):
    resumes = load_and_split_resumes(file_path)

    print(f"[INFO] Найдено резюме: {len(resumes)}")

    for doc_id, text in resumes:
        print(f"[INDEX] {doc_id}")
        add_resume(doc_id, text)


# ------------------------
# PROCESS VACANCY
# ------------------------

def process_vacancy(vacancy_path):
    pre = Preprocessor()

    with open(vacancy_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    vacancy_json = pre.process_vacancy(raw_text)

    print("\n[VACANCY JSON]")
    print(json.dumps(vacancy_json, indent=2, ensure_ascii=False))

    return vacancy_json


# ------------------------
# SEARCH PIPELINE
# ------------------------

def search_candidates(vacancy_json):
    collection = get_collection()

    # embedding вакансии
    vacancy_embedding_text = build_vacancy_embedding(vacancy_json)
    query_embedding = get_embedding(vacancy_embedding_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K_INITIAL
    )

    candidates = results["metadatas"][0]

    print(f"\n[SEARCH] найдено кандидатов: {len(candidates)}")

    # ------------------------
    # FAST FILTER
    # ------------------------

    filtered = []

    for c in candidates:
        res = fast_filter(c, vacancy_json)

        score = res.get("score", 0)

        if score >= FAST_FILTER_THRESHOLD:
            filtered.append((c, score))

    print(f"[FAST FILTER] осталось: {len(filtered)}")

    # ограничиваем
    filtered = sorted(filtered, key=lambda x: x[1], reverse=True)
    filtered = filtered[:TOP_K_FINAL]

    # ------------------------
    # SMART RANKING
    # ------------------------

    final_results = []

    for c, fast_score in filtered:
        res = smart_score(c, vacancy_json)

        final_results.append({
            "candidate": c,
            "score": res.get("score", 0),
            "reason": res.get("reason", ""),
            "strengths": res.get("strengths", []),
            "weaknesses": res.get("weaknesses", [])
        })

    final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)

    return final_results


# ------------------------
# MAIN
# ------------------------

def main():
    import os

    print("=== START MAIN ===")

    BASE_DIR = os.path.dirname(__file__)

    resumes_file = os.path.join(BASE_DIR, "data", "resumes", "resumes.txt")
    vacancy_file = os.path.join(BASE_DIR, "data", "vacancy.txt")

    # ------------------------
    # CHECK FILES
    # ------------------------

    print("\n[PATH CHECK]")
    print("RESUMES PATH:", resumes_file)
    print("RESUMES EXISTS:", os.path.exists(resumes_file))

    print("VACANCY PATH:", vacancy_file)
    print("VACANCY EXISTS:", os.path.exists(vacancy_file))

    if not os.path.exists(resumes_file):
        print("❌ ERROR: resumes.txt not found")
        return

    if not os.path.exists(vacancy_file):
        print("❌ ERROR: vacancy.txt not found")
        return

    # ------------------------
    # LOAD RESUMES
    # ------------------------

    print("\n[LOAD RESUMES]")

    resumes = load_and_split_resumes(resumes_file)
    print(f"Найдено резюме: {len(resumes)}")

    if len(resumes) == 0:
        print("❌ ERROR: нет резюме (проверь формат и разделитель ---)")
        return

    print("Пример резюме:")
    print(resumes[0][1][:200], "...")

    # ------------------------
    # INDEX RESUMES
    # ------------------------

    print("\n[INDEXING]")

    for doc_id, text in resumes:
        print(f"[INDEX] {doc_id}")
        add_resume(doc_id, text)

    # ------------------------
    # PROCESS VACANCY
    # ------------------------

    print("\n[PROCESS VACANCY]")

    vacancy_json = process_vacancy(vacancy_file)

    if not vacancy_json:
        print("❌ ERROR: вакансия не распарсилась (LLM вернул пустоту)")
        return

    # ------------------------
    # SEARCH
    # ------------------------

    print("\n[SEARCH PIPELINE]")

    results = search_candidates(vacancy_json)

    if not results:
        print("❌ НЕТ РЕЗУЛЬТАТОВ")
        return

    # ------------------------
    # OUTPUT
    # ------------------------

    print("\n====== ТОП КАНДИДАТЫ ======\n")

    for i, r in enumerate(results, 1):
        c = r["candidate"]

        print(f"#{i} | SCORE: {r['score']}")
        print(f"POSITION: {c.get('position')}")
        print(f"LEVEL: {c.get('level')}")
        print(f"EXP: {c.get('experience_years')}")

        print("STRENGTHS:", ", ".join(r["strengths"]))
        print("WEAKNESSES:", ", ".join(r["weaknesses"]))
        print("REASON:", r["reason"])

        print("-" * 50)
if __name__ == "__main__":
    main()