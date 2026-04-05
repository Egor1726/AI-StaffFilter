# txt_processor.py
import re
import json
from pathlib import Path


# ── Парсинг одного резюме ─────────────────────────────────────────────────────

def parse_resume_fields(text: str) -> dict:
    """
    Извлекает поля из текстового блока одного резюме.
    Возвращает словарь с полями кандидата.
    """
    fields = {
        "name": "Неизвестно",
        "email": "",
        "phone": "",
        "position": "",
        "experience_years": 0,
        "skills": [],
        "education": "",
        "languages": [],
        "expected_salary": "",
        "about": text[:500]
    }

    # Имя — первая строка блока
    first_line = text.strip().split('\n')[0].strip()
    if first_line:
        fields["name"] = first_line

    # Email
    m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    if m:
        fields["email"] = m.group(0)

    # Телефон
    m = re.search(r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', text)
    if m:
        fields["phone"] = m.group(0)

    # Должность
    m = re.search(r'(?:Позиция|Должность|Position):\s*(.+)', text, re.IGNORECASE)
    if m:
        fields["position"] = m.group(1).strip()

    # Опыт в годах
    m = re.search(r'(\d+)\s*(?:лет|год|года)\s*опыт', text, re.IGNORECASE)
    if m:
        fields["experience_years"] = int(m.group(1))

    # Навыки
    m = re.search(r'(?:Навыки|Skills):\s*(.+)', text, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()
        fields["skills"] = [s.strip() for s in raw.split(',') if s.strip()]

    # Образование
    m = re.search(r'(?:Образование|Education):\s*(.+)', text, re.IGNORECASE)
    if m:
        fields["education"] = m.group(1).strip()

    # Зарплата
    m = re.search(r'(?:Зарплата|Salary|Ожидания):\s*(.+)', text, re.IGNORECASE)
    if m:
        fields["expected_salary"] = m.group(1).strip()

    # О себе — текст после "О себе:"
    m = re.search(r'(?:О себе|About):\s*(.+?)(?=\n[А-ЯA-Z]|\Z)', text, re.IGNORECASE | re.DOTALL)
    if m:
        fields["about"] = m.group(1).strip()[:500]

    return fields


# ── Чтение файлов ─────────────────────────────────────────────────────────────

def load_resumes(resumes_path: str) -> list[dict]:
    """
    Читает resumes.txt и разбивает по разделителю ---.
    Возвращает список словарей с полями каждого резюме.
    """
    text = Path(resumes_path).read_text(encoding="utf-8")
    blocks = [b.strip() for b in text.split("---") if b.strip()]

    resumes = []
    for block in blocks:
        fields = parse_resume_fields(block)
        resumes.append(fields)

    print(f"[txt_processor] Найдено резюме: {len(resumes)}")
    return resumes


def load_vacancy(vacancy_path: str) -> str:
    """
    Читает vacancy.txt и возвращает текст как строку.
    Не парсим — передаём в LLM целиком.
    """
    text = Path(vacancy_path).read_text(encoding="utf-8").strip()
    print(f"[txt_processor] Вакансия загружена: {len(text)} символов")
    return text


# ── Подготовка для ChromaDB ───────────────────────────────────────────────────

def prepare_for_chroma(resumes: list[dict]) -> list[dict]:
    """
    Готовит резюме в формате который ожидает ChromaDB / indexer.py.

    Возвращает список словарей:
    {
        "id":       уникальный ID кандидата
        "text":     полный текст для векторизации (эмбеддинга)
        "metadata": поля для фильтрации и вывода результатов
    }

    Важно:
    - все значения в metadata должны быть строками (требование ChromaDB)
    - skills передаётся как строка через запятую, не список
    - experience_years приводится к строке
    """
    documents = []

    for i, r in enumerate(resumes):
        candidate_id = f"candidate_{i:04d}"

        # Полный текст для эмбеддинга — чем больше контекста тем лучше
        full_text = f"""
Имя: {r['name']}
Должность: {r['position']}
Опыт: {r['experience_years']} лет
Навыки: {', '.join(r['skills']) if isinstance(r['skills'], list) else r['skills']}
Образование: {r['education']}
Зарплата: {r['expected_salary']}
О себе: {r['about']}
        """.strip()

        # Метаданные — только строки, ChromaDB не принимает числа и списки
        metadata = {
            "candidate_id":    candidate_id,
            "name":            r["name"],
            "email":           r["email"],
            "phone":           r["phone"],
            "position":        r["position"],
            "experience_years": str(r["experience_years"]),
            "skills":          ", ".join(r["skills"]) if isinstance(r["skills"], list) else r["skills"],
            "education":       r["education"],
            "expected_salary": r["expected_salary"],
        }

        documents.append({
            "id":       candidate_id,
            "text":     full_text,
            "metadata": metadata,
        })

    print(f"[txt_processor] Подготовлено для ChromaDB: {len(documents)} документов")
    return documents


# ── Главная функция ───────────────────────────────────────────────────────────

def process_files(resumes_path: str, vacancy_path: str) -> tuple[list[dict], str]:
    """
    Главная функция модуля. Точка входа для всей системы.

    Вход:
        resumes_path — путь к файлу со всеми резюме (resumes.txt)
        vacancy_path — путь к файлу с требованиями (vacancy.txt)

    Выход:
        documents    — список готовых документов для ChromaDB (indexer.py)
        vacancy_text — текст вакансии для LLM агента (agent.py)

    Использование в indexer.py:
        from txt_processor import process_files
        documents, vacancy_text = process_files("data/resumes.txt", "data/vacancy.txt")
    """
    resumes = load_resumes(resumes_path)
    vacancy_text = load_vacancy(vacancy_path)
    documents = prepare_for_chroma(resumes)
    return documents, vacancy_text


# ── Быстрая проверка ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    documents, vacancy = process_files("data/resumes.txt", "data/vacancy.txt")

    print("\n── Первый документ ──────────────────────────────")
    print(f"ID:       {documents[0]['id']}")
    print(f"Имя:      {documents[0]['metadata']['name']}")
    print(f"Навыки:   {documents[0]['metadata']['skills']}")
    print(f"Опыт:     {documents[0]['metadata']['experience_years']} лет")
    print(f"\nТекст для эмбеддинга:\n{documents[0]['text']}")

    print("\n── Вакансия (первые 150 символов) ───────────────")
    print(vacancy[:150])

    print(f"\n── Итого: {len(documents)} кандидатов готовы для ChromaDB ──")