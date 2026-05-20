#!/usr/bin/env python
"""
AI Watcher — мониторит backend/uploads/, ищет PDF рекурсивно
и для каждой новой задачи запускает AI-пайплайн.
"""
import os, sys, time, json
from pathlib import Path

AI_DIR = Path(__file__).resolve().parent / "hr_agent"
sys.path.insert(0, str(AI_DIR))

os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
os.environ.setdefault("CHROMA_DB_PATH", str(AI_DIR / "chroma_db"))

from preprocessor import Preprocessor
from indexer import get_collection, get_embedding, build_vacancy_embedding, add_resume
from agent import fast_filter, smart_score
from pdf_reader import extract_text_from_pdf
from config import TOP_K_INITIAL, FAST_FILTER_THRESHOLD

UPLOADS_DIR = Path(__file__).resolve().parent.parent / "backend" / "uploads"


def load_pdfs_recursive(res_dir: Path):
    """Ищет все *.pdf в res_dir и любых вложенных подпапках."""
    pdfs = []
    for path in sorted(res_dir.rglob("*.pdf")):
        doc_id = path.stem
        print(f"  -> Читаю: {path.relative_to(res_dir)}")
        text = extract_text_from_pdf(str(path))
        if text.strip():
            pdfs.append((doc_id, text))
        else:
            print(f"     [SKIP] пустой текст: {path.name}")
    return pdfs


def process_task(task_dir: Path) -> str:
    print(f"\n[TASK] {task_dir.name}")
    req_file = task_dir / "requirements.txt"
    res_dir = task_dir / "resumes"
    if not req_file.exists():
        return "ERROR: requirements.txt не найден"
    if not res_dir.exists():
        return "ERROR: папка resumes/ не найдена"

    pre = Preprocessor()
    vacancy_json = pre.process_vacancy(req_file.read_text(encoding="utf-8"))
    if not vacancy_json:
        return "ERROR: не распарсилась вакансия"

    pdfs = load_pdfs_recursive(res_dir)
    if not pdfs:
        return "ERROR: PDF-резюме не найдены (даже рекурсивно)"
    print(f"  Прочитано PDF: {len(pdfs)}")

    coll = get_collection()
    if coll.count() > 0:
        ids = coll.get()["ids"]
        if ids:
            coll.delete(ids=ids)

    for doc_id, txt in pdfs:
        add_resume(f"pdf_{doc_id}", txt)
    print(f"  Индексировано: {coll.count()} резюме")

    q_emb = get_embedding(build_vacancy_embedding(vacancy_json))
    found = coll.query(query_embeddings=[q_emb], n_results=min(TOP_K_INITIAL, coll.count()))
    candidates = [json.loads(d) for d in found["documents"][0]]

    passed = []
    for c in candidates:
        if fast_filter(c, vacancy_json).get("score", 0) >= FAST_FILTER_THRESHOLD:
            passed.append(c)
    print(f"  Прошли fast filter: {len(passed)}/{len(candidates)}")

    if not passed:
        return "Ни один кандидат не прошёл первичный фильтр."

    final = []
    for i, c in enumerate(passed, 1):
        print(f"  Smart score {i}/{len(passed)}: {c.get('position', '?')[:40]}")
        r = smart_score(c, vacancy_json)
        final.append({
            "candidate": c,
            "score": r.get("score", 0),
            "summary": r.get("summary") or r.get("description") or "—",
            "strengths": r.get("strengths", []),
            "weaknesses": r.get("weaknesses", []),
        })
    final.sort(key=lambda x: x["score"], reverse=True)

    out = []
    out.append("=" * 70)
    out.append("    ФИНАЛЬНЫЙ РЕЙТИНГ КАНДИДАТОВ (AI SMART SCORING)")
    out.append("=" * 70)
    out.append(f"\nОбработано: {len(pdfs)} резюме, прошли фильтр: {len(passed)}\n")
    for i, r in enumerate(final, 1):
        c = r["candidate"]
        out.append("-" * 70)
        out.append(f"#{i}  SCORE: {r['score']}/100")
        out.append(f"    Кандидат : {c.get('name') or 'Аноним'}")
        if c.get("phone") and str(c["phone"]).lower() != "null":
            out.append(f"    Телефон  : {c['phone']}")
        if c.get("email") and str(c["email"]).lower() != "null":
            out.append(f"    Email    : {c['email']}")
        out.append(f"    Должность: {c.get('position', 'N/A')}")
        out.append(f"    Опыт     : {c.get('experience_years', 'N/A')} лет")
        if r["strengths"]:
            out.append(f"    Плюсы    : {', '.join(r['strengths'])}")
        if r["weaknesses"]:
            out.append(f"    Минусы   : {', '.join(r['weaknesses'])}")
        out.append(f"    Итог     : {r['summary']}")
    return "\n".join(out)


def main():
    print("=" * 60)
    print("AI WATCHER STARTED (recursive PDF search)")
    print(f"Watch: {UPLOADS_DIR}")
    print(f"AI:    {AI_DIR}")
    print(f"Ollama:{os.environ['OLLAMA_HOST']}")
    print("=" * 60)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    done = set()

    while True:
        try:
            for d in UPLOADS_DIR.iterdir():
                if not d.is_dir() or d.name in done:
                    continue
                final = d / "final_result.txt"
                if final.exists():
                    done.add(d.name)
                    continue
                req = d / "requirements.txt"
                res = d / "resumes"
                if not req.exists() or not res.exists():
                    continue

                try:
                    text = process_task(d)
                except Exception as e:
                    text = f"ERROR в watcher: {type(e).__name__}: {e}"
                    import traceback; traceback.print_exc()
                final.write_text(text, encoding="utf-8")
                done.add(d.name)
                print(f"[DONE] {final}\n")
            time.sleep(2)
        except KeyboardInterrupt:
            print("Stopped.")
            break


if __name__ == "__main__":
    main()
