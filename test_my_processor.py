from txt_processor import process_files
import sqlite3
import json

# Запускаем ваш модуль
db_path, vacancy_text = process_files(
    resumes_path="data/resumes.txt",
    vacancy_path="data/vacancy.txt"
)

# Проверяем что записалось
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM resumes")
print(f"Резюме в базе: {cursor.fetchone()[0]}")

cursor.execute("SELECT id, name, position, experience_years FROM resumes")
for row in cursor.fetchall():
    print(f"  {row[0]}. {row[1]} — {row[2]} ({row[3]} лет)")

cursor.execute("SELECT name, skills FROM resumes LIMIT 1")
row = cursor.fetchone()
print(f"\nНавыки {row[0]}: {json.loads(row[1])}")

conn.close()

print(f"\nВакансия (первые 100 символов):\n{vacancy_text[:100]}")