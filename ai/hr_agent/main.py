# main.py
"""
Вариант 2: мониторинг папки uploads/
Бэкенд кладёт файлы в uploads/{taskId}/
Мы мониторим папку, обрабатываем и пишем final_result.txt
"""

import time
import json
from pathlib import Path

from indexer import index_all, search
from agent import rank_candidates


# ── Настройки ─────────────────────────────────────────────────────────────────

UPLOADS_DIR = Path("../../uploads")   # папка uploads относительно ai/hr_agent
POLL_INTERVAL = 3                      # проверять каждые 3 секунды
PROCESSED_MARKER = ".processed"       # маркер что папка уже обработана


# ── Обработка одной задачи ────────────────────────────────────────────────────

def process_task(task_dir: Path) -> None:
    """
    Обрабатывает одну папку задачи.
    Читает resumes/ и requirements.txt → ранжирует → пишет final_result.txt
    """
    task_id = task_dir.name
    print(f"\n[main] Новая задача: {task_id}")

    # Пути к файлам
    resumes_dir = task_dir / "resumes"
    requirements_path = task_dir / "requirements.txt"
    final_result_path = task_dir / "final_result.txt"

    # Проверяем что нужные файлы есть
    if not resumes_dir.exists():
        print(f"[main] Папка resumes/ не найдена в {task_dir} — пропускаем")
        return
    if not requirements_path.exists():
        print(f"[main] Файл requirements.txt не найден в {task_dir} — пропускаем")
        return

    # Собираем все резюме из папки в один txt
    # (txt_processor ожидает один файл с разделителем ---)
    resumes_combined = task_dir / ".resumes_combined.txt"
    combine_resumes(resumes_dir, resumes_combined)

    try:
        # 1. Индексация — читаем файлы и грузим в ChromaDB
        print(f"[main] Индексация резюме...")
        vacancy_text = index_all(
            str(resumes_combined),
            str(requirements_path)
        )

        # 2. Поиск — получаем всех кандидатов из ChromaDB
        print(f"[main] Поиск кандидатов...")
        candidates = search(vacancy_text)

        if not candidates:
            print(f"[main] Кандидаты не найдены")
            write_empty_result(final_result_path)
            return

        # Приводим к формату который ожидает agent.py
        candidates_for_agent = [
            {
                "id": c.get("name", f"candidate_{i}"),
                "text": f"Навыки: {c.get('skills', '')}\nОпыт: {c.get('experience_years', '')} лет",
                "metadata": c,
            }
            for i, c in enumerate(candidates)
        ]

        # 3. Ранжирование через LLM
        print(f"[main] Ранжирование {len(candidates)} кандидатов...")
        ranked = rank_candidates(candidates_for_agent, vacancy_text)

        # 4. Записываем результат
        write_final_result(final_result_path, ranked)
        print(f"[main] Готово: {final_result_path}")

    finally:
        # Удаляем временный файл
        if resumes_combined.exists():
            resumes_combined.unlink()

    # Ставим маркер что задача обработана
    (task_dir / PROCESSED_MARKER).touch()


def combine_resumes(resumes_dir: Path, output_path: Path) -> None:
    """
    Объединяет все файлы резюме из папки в один файл с разделителем ---
    Поддерживает .txt и .pdf
    """
    parts = []

    for resume_file in sorted(resumes_dir.iterdir()):
        if resume_file.suffix == ".txt":
            text = resume_file.read_text(encoding="utf-8").strip()
            parts.append(text)
        elif resume_file.suffix == ".pdf":
            text = extract_pdf_text(resume_file)
            if text:
                parts.append(text)

    combined = "\n---\n".join(parts)
    output_path.write_text(combined, encoding="utf-8")
    print(f"[main] Объединено резюме: {len(parts)} файлов")


def extract_pdf_text(pdf_path: Path) -> str:
    """Извлекает текст из PDF через pdfplumber если установлен."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            ).strip()
    except ImportError:
        print(f"[main] pdfplumber не установлен — пропускаем {pdf_path.name}")
        return ""
    except Exception as e:
        print(f"[main] Ошибка чтения PDF {pdf_path.name}: {e}")
        return ""


# ── Запись результата ─────────────────────────────────────────────────────────

def write_final_result(output_path: Path, ranked: list) -> None:
    """Записывает ранжированный список кандидатов в final_result.txt"""
    lines = ["=" * 60, "РЕЗУЛЬТАТЫ РАНЖИРОВАНИЯ КАНДИДАТОВ", "=" * 60, ""]

    for candidate in ranked:
        rank = candidate.get("rank", "?")
        evaluation = candidate.get("evaluation", {})
        metadata = candidate.get("metadata", {})

        name = evaluation.get("name") or metadata.get("name", "Неизвестно")
        score = candidate.get("score", 0)
        matched = evaluation.get("matched_skills", [])
        missing = evaluation.get("missing_skills", [])
        comment = evaluation.get("comment", "")
        email = metadata.get("email", "")
        phone = metadata.get("phone", "")
        position = metadata.get("position", "")
        experience = metadata.get("experience_years", "")

        lines.append(f"#{rank}  {name}")
        lines.append(f"    Оценка:    {score}/100")
        lines.append(f"    Позиция:   {position}")
        lines.append(f"    Опыт:      {experience} лет")
        if email:
            lines.append(f"    Email:     {email}")
        if phone:
            lines.append(f"    Телефон:   {phone}")
        if matched:
            lines.append(f"    Плюсы:     {', '.join(matched)}")
        if missing:
            lines.append(f"    Минусы:    {', '.join(missing)}")
        if comment:
            lines.append(f"    Вывод:     {comment}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_empty_result(output_path: Path) -> None:
    output_path.write_text("Кандидаты не найдены.", encoding="utf-8")


# ── Мониторинг папки uploads/ ─────────────────────────────────────────────────

def is_ready(task_dir: Path) -> bool:
    """Проверяет что папка готова к обработке."""
    has_resumes = (task_dir / "resumes").exists()
    has_requirements = (task_dir / "requirements.txt").exists()
    not_processed = not (task_dir / PROCESSED_MARKER).exists()
    no_result_yet = not (task_dir / "final_result.txt").exists()
    return has_resumes and has_requirements and not_processed and no_result_yet


def watch_uploads() -> None:
    """Мониторит папку uploads/ и обрабатывает новые задачи."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[main] Мониторинг папки: {UPLOADS_DIR.resolve()}")
    print(f"[main] Интервал проверки: {POLL_INTERVAL} сек")
    print(f"[main] Ожидаю новые задачи...\n")

    while True:
        try:
            for task_dir in UPLOADS_DIR.iterdir():
                if task_dir.is_dir() and is_ready(task_dir):
                    process_task(task_dir)
        except Exception as e:
            print(f"[main] Ошибка: {e}")

        time.sleep(POLL_INTERVAL)


# ── Точка входа ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    watch_uploads()