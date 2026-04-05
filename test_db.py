# test_db.py — запускаем один раз чтобы понять как работает SQLite
import sqlite3
import json

# 1. Создаём/открываем файл базы данных
conn = sqlite3.connect("test_my.db")
cursor = conn.cursor()

# 2. Создаём таблицу
cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        skills TEXT
    )
''')

# 3. Вставляем одну строку
cursor.execute(
    "INSERT INTO resumes (name, email, skills) VALUES (?, ?, ?)",
    (
        "Иван Петров",
        "ivan@mail.ru",
        json.dumps(["Python", "Docker"], ensure_ascii=False)
    )
)

# 4. Сохраняем
conn.commit()

# 5. Читаем обратно и печатаем
cursor.execute("SELECT * FROM resumes")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
# Проверяем что всё сохранилось корректно
conn = sqlite3.connect("resumes.db")
cursor = conn.cursor()

# Считаем сколько строк
cursor.execute("SELECT COUNT(*) FROM resumes")
count = cursor.fetchone()[0]
print(f"Всего резюме в базе: {count}")

# Смотрим первые три
cursor.execute("SELECT id, name, position, experience_years FROM resumes LIMIT 3")
for row in cursor.fetchall():
    print(f"  {row[0]}. {row[1]} — {row[2]} ({row[3]} лет)")

# Проверяем что skills записались как JSON
cursor.execute("SELECT name, skills FROM resumes LIMIT 1")
row = cursor.fetchone()
print(f"\nНавыки {row[0]}: {row[1]}")
print(f"После json.loads: {json.loads(row[1])}")

conn.close()