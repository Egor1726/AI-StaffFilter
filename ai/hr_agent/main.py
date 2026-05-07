import os
import json

from config import (
    TOP_K_INITIAL,
    TOP_K_FINAL,
    FAST_FILTER_THRESHOLD,
    DEBUG
)

from indexer import (
    get_collection,
    get_embedding,
    build_vacancy_embedding,
    add_resume
)

from preprocessor import Preprocessor
from agent import fast_filter, smart_score
from pdf_reader import load_pdf_resumes

# ------------------------
# PROCESS VACANCY
# ------------------------

def process_vacancy(vacancy_path):
    pre = Preprocessor()
    if not os.path.exists(vacancy_path):
        print(f"❌ ERROR: Файл вакансии не найден: {vacancy_path}")
        return None

    with open(vacancy_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    vacancy_json = pre.process_vacancy(raw_text)
    return vacancy_json


# ------------------------
# SEARCH PIPELINE
# ------------------------

def search_candidates(vacancy_json):
    if not vacancy_json:
        return []

    collection = get_collection()
    count = collection.count()
    print(f"\n[INFO] Статус базы: {count} записей.")
    
    if count == 0:
        print("❌ ERROR: База пуста! Поиск невозможен.")
        return []

    # 1. Поиск через эмбеддинги
    vacancy_embedding_text = build_vacancy_embedding(vacancy_json)
    query_embedding = get_embedding(vacancy_embedding_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(TOP_K_INITIAL, count)
    )

    # Загружаем полные JSON объекты из документов базы
    candidates = [json.loads(doc) for doc in results["documents"][0]]
    
    # 2. FAST FILTER — только отсев по порогу, без сортировки и обрезки
    passed = []
    rejected_count = 0
    print(f"\n[PROCESS] Первичный фильтр (Threshold: {FAST_FILTER_THRESHOLD})...")

    for i, c in enumerate(candidates):
        res = fast_filter(c, vacancy_json)
        score = res.get("score", 0)
        reason = res.get("reason", "")

        if score >= FAST_FILTER_THRESHOLD:
            passed.append(c)
            status = "PASS"
        else:
            rejected_count += 1
            status = "REJECT"

        if DEBUG:
            name = c.get("position", "N/A")[:25]
            print(f"  [{i+1}/{len(candidates)}] {status} | {name} | Score: {score} | {reason}")

    print(f"\n  Прошли фильтр: {len(passed)}, отсеяны: {rejected_count}")

    if not passed:
        print("Ни один кандидат не прошел порог фильтрации.")
        return []

    # 3. SMART RANKING — глубокий анализ всех прошедших, ранжирование по его скору
    final_results = []
    print(f"\n[PROCESS] Глубокий анализ {len(passed)} кандидатов...")

    for i, c in enumerate(passed):
        print(f"  [{i+1}/{len(passed)}] Анализирую: {c.get('position', 'N/A')[:30]}...")
        res = smart_score(c, vacancy_json)

        final_results.append({
            "candidate": c,
            "score": res.get("score", 0),
            "summary": res.get("summary") or res.get("description") or "Не сформировано",
            "strengths": res.get("strengths", []),
            "weaknesses": res.get("weaknesses", []),
            "ranking_notes": res.get("ranking_notes", ""),
            "breakdown": res.get("breakdown", {})
        })

    return sorted(final_results, key=lambda x: x["score"], reverse=True)


# ------------------------
# MAIN
# ------------------------

def index_resumes(resumes_dir: str):
    """
    Индексирует резюме из двух источников:
    1. PDF-файлы из resumes_dir
    2. Текстовый файл resumes.txt (блоки разделённые ---)
    """
    collection = get_collection()

    # --- Сброс коллекции, чтобы не было дублей при повторном запуске ---
    existing = collection.count()
    if existing > 0:
        print(f"  [INFO] Сбрасываю старую коллекцию ({existing} записей)...")
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)

    total_indexed = 0

    # --- Источник 1: PDF-файлы ---
    print("\n  [PDF] Читаю PDF-резюме...")
    pdf_resumes = load_pdf_resumes(resumes_dir)
    for doc_id, raw_text in pdf_resumes:
        print(f"  -> Индексирую PDF: {doc_id}")
        add_resume(f"pdf_{doc_id}", raw_text)
        total_indexed += 1

    # --- Источник 2: resumes.txt (блоки через ---) ---
    txt_file = os.path.join(resumes_dir, "resumes.txt")
    if os.path.exists(txt_file):
        print(f"\n  [TXT] Читаю текстовый файл: {txt_file}")
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read()
        blocks = [b.strip() for b in content.split("---") if b.strip()]
        print(f"  Найдено блоков: {len(blocks)}")
        for i, block in enumerate(blocks):
            doc_id = f"txt_res_{i+1}"
            print(f"  -> Индексирую блок {i+1}/{len(blocks)}: {block[:40]}...")
            add_resume(doc_id, block)
            total_indexed += 1
    else:
        print(f"\n  [TXT] resumes.txt не найден — пропускаю.")

    print(f"\n✅ Индексация завершена. Всего загружено: {total_indexed} резюме.")
    print(f"   Записей в базе: {get_collection().count()}")


def ask_mode() -> str:
    """Интерактивный выбор режима запуска."""
    collection = get_collection()
    count = collection.count()

    print("\n  Текущая база: ", end="")
    if count > 0:
        print(f"{count} резюме проиндексировано")
    else:
        print("пуста")

    print()
    print("  [1] Переиндексировать — сбросить базу и загрузить резюме заново")
    print("  [2] Только скоринг   — использовать уже имеющуюся базу")
    print()

    while True:
        choice = input("  Выбор (1/2): ").strip()
        if choice in ("1", "2"):
            return choice
        print("  Введите 1 или 2.")


def main():
    print("="*60)
    print("    AI STAFF FILTER: BATCH PROCESSING MODE")
    print("="*60)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    vacancy_file = os.path.join(BASE_DIR, "data", "vacancy.txt")
    resumes_dir  = os.path.join(BASE_DIR, "data", "resumes")

    # 1. ШАГ ИНДЕКСАЦИИ
    mode = ask_mode()

    if mode == "1":
        print("\n[STEP 1] Индексация резюме...")
        index_resumes(resumes_dir)
    else:
        count = get_collection().count()
        if count == 0:
            print("\n[WARN] База пуста — запускаю индексацию автоматически...")
            index_resumes(resumes_dir)
        else:
            print(f"\n[STEP 1] Пропуск индексации, в базе {count} резюме.")

    # 2. ШАГ АНАЛИЗА ВАКАНСИИ
    print("\n[STEP 2] Разбор вакансии...")
    vacancy_json = process_vacancy(vacancy_file)
    if not vacancy_json:
        return

    # 3. ШАГ ПОИСКА
    print("\n[STEP 3] Поиск и скоринг...")
    results = search_candidates(vacancy_json)

    # 4. ВЫВОД РЕЗУЛЬТАТОВ
    if results:
        print("\n" + "█"*70)
        print("                   ФИНАЛЬНЫЙ РЕЙТИНГ КАНДИДАТОВ")
        print("█"*70 + "\n")

        for i, r in enumerate(results, 1):
            c = r["candidate"]
            bd = r.get("breakdown", {})
            strengths = r["strengths"] if r["strengths"] else ["—"]
            weaknesses = r["weaknesses"] if r["weaknesses"] else ["—"]

            # Идентификация кандидата: имя > имя из кандидата > должность+опыт
            name = (c.get("name") or r.get("name") or "").strip()
            phone = (r.get("contact", {}).get("phone") or c.get("phone") or "")
            email = (r.get("contact", {}).get("email") or c.get("email") or "")
            identity = name if name and name.lower() not in ("null", "аноним", "none") else None
            if not identity:
                identity = f"{c.get('position','?')} | {c.get('experience_years','?')} лет опыта"

            print(f"#{i}  SCORE: {r['score']}/100")
            print(f"    Кандидат  : {identity}")
            if phone and phone.lower() != "null":
                print(f"    Телефон   : {phone}")
            if email and email.lower() != "null":
                print(f"    Email     : {email}")
            print(f"    Должность : {c.get('position', 'N/A')}")
            print(f"    Опыт      : {c.get('experience_years', 'N/A')} лет")
            print(f"    Плюсы     : {', '.join(strengths)}")
            if r["weaknesses"]:
                print(f"    Минусы    : {', '.join(weaknesses)}")
            print(f"    Итог      : {r['summary']}")
            print("-" * 70)
    else:
        print("\n[!] Результаты не найдены.")

if __name__ == "__main__":
    main()