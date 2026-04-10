import json
from agent import evaluate_candidate

# Читаем вакансию из файла
with open("test_data/vacancy.txt", "r", encoding="utf-8") as f:
    vacancy = f.read()

# Тестовый кандидат в формате от человека 1
candidate = {
    {
  "id": "candidate_0000",
  "text": "Имя: Иван Петров\nДолжность: Senior Python Developer\nОпыт: 6 лет\nНавыки: Python, FastAPI, Django, PostgreSQL, Docker, Redis, Git\nОбразование: МГТУ им. Баумана, Информатика, 2017\nЗарплата: 280000 руб\nО себе: Разрабатываю backend-сервисы для высоконагруженных систем. Участвовал в проектировании микросервисной архитектуры. Есть опыт внедрения ML-моделей в production.",
  "metadata": {
    "candidate_id": "candidate_0000",
    "name": "Иван Петров",
    "email": "ivan.petrov@email.com",
    "phone": "+7-999-123-45-67",
    "position": "Senior Python Developer",
    "experience_years": "6",
    "skills": "Python, FastAPI, Django, PostgreSQL, Docker, Redis, Git",
    "education": "МГТУ им. Баумана, Информатика, 2017",
    "expected_salary": "280000 руб"
  }
}   
}

print("=== evaluate_candidate ===")
result = evaluate_candidate(candidate, vacancy)
print(json.dumps(result, ensure_ascii=False, indent=2))