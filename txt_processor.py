# txt_processor.py
import re
import sqlite3
import json
from pathlib import Path


def parse_resume_fields(text: str) -> dict:
    """Извлекает поля из текстового блока одного резюме."""
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
        "about": text[:500]   # первые 500 символов как описание
    }

    # Email
    m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    if m:
        fields["email"] = m.group(0)

    # Телефон
    m = re.search(r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', text)
    if m:
        fields["phone"] = m.group(0)

    first_line = text.strip().split('\n')[0].strip()
    if first_line:
        fields["name"] = first_line

    # Опыт в годах
    m = re.search(r'(\d+)\s*(?:лет|год|года)\s*опыт', text, re.IGNORECASE)
    if m:
        fields["experience_years"] = int(m.group(1))

    # Должность — строка после "Позиция:" или "Должность:" или "Вакансия:"
    m = re.search(r'(?:Позиция|Должность|Position):\s*(.+)', text, re.IGNORECASE)
    if m:
        fields["position"] = m.group(1).strip()

    # Навыки — строка после "Навыки:"
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

    return fields


def load_resumes(resumes_path: str) -> list[dict]:
    """Читает resumes.txt и разбивает на отдельные резюме по разделителю ---"""
    text = Path(resumes_path).read_text(encoding="utf-8")
    blocks = [b.strip() for b in text.split("---") if b.strip()]

    resumes = []
    for block in blocks:
        fields = parse_resume_fields(block)
        resumes.append(fields)

    print(f"Найдено резюме: {len(resumes)}")
    return resumes


def load_vacancy(vacancy_path: str) -> str:
    """Читает vacancy.txt и возвращает текст как строку — без парсинга."""
    text = Path(vacancy_path).read_text(encoding="utf-8").strip()
    print(f"Вакансия загружена: {len(text)} символов")
    return text

def process_files(resumes_path: str, vacancy_path: str,
                  db_path: str = "resumes.db") -> tuple[str, str]:
    """
    Главная функция модуля.
    Вход:  resumes.txt + vacancy.txt
    Выход: путь к SQLite + текст вакансии
    """
    resumes = load_resumes(resumes_path)
    vacancy_text = load_vacancy(vacancy_path)
    save_to_database(resumes, db_path)
    return db_path, vacancy_text


def save_to_database(resumes: list[dict], db_path: str = "resumes.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Сначала удаляем старую таблицу если есть
    cursor.execute("DROP TABLE IF EXISTS resumes")

    # Потом создаём новую с нуля
    cursor.execute('''
        CREATE TABLE resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            position TEXT,
            experience_years INTEGER,
            skills TEXT,
            education TEXT,
            languages TEXT,
            expected_salary TEXT,
            about TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


    # Вставляем каждое резюме
    for r in resumes:
        cursor.execute('''
            INSERT INTO resumes
            (name, email, phone, position, experience_years,
             skills, education, languages, expected_salary, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            r["name"],
            r["email"],
            r["phone"],
            r["position"],
            r["experience_years"],
            json.dumps(r["skills"], ensure_ascii=False),  # список → JSON строка
            r["education"],
            json.dumps(r["languages"], ensure_ascii=False),  # список → JSON строка
            r["expected_salary"],
            r["about"],
        ))

    # Сохраняем все изменения в файл
    conn.commit()
    conn.close()

    print(f"Сохранено: {len(resumes)} резюме → {db_path}")

# Быстрая проверка
if __name__ == "__main__":
    db, vacancy = process_files("data/resumes.txt", "data/vacancy.txt")
    print(f"\nБД: {db}")
    print(f"Вакансия (первые 200 символов):\n{vacancy[:200]}")