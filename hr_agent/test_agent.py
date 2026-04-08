# test_agent.py
"""
Простой тестовый скрипт для проверки работы агента.
"""

from agent import call_llm, parse_json_response
from test_data import RESUMES


def test_python_experience_check(resume: str):
    """Проверка наличия Python-опыта по одному резюме."""
    print("=" * 60)
    print("Тест 1: Проверка опыта с Python")
    print("=" * 60)

    prompt = f"""Проанализируй резюме кандидата.
Правила ответа:
1) Отвечай строго на русском языке.
2) Верни только JSON, без Markdown и без пояснений.
3) Поле "details" всегда на русском.

Логика определения has_python_experience:
- has_python_experience = true, если есть ХОТЯ БЫ ОДНО подтверждение практического опыта Python:
    a) в должности указано "Python Developer" или аналогичное,
    b) в опыте работы есть backend/API задачи и Python указан в навыках,
    c) есть коммерческий опыт разработки от 1 года и Python среди основных навыков.
- has_python_experience = false, только если Python указан как "изучаю"/курс и нет рабочего опыта разработчиком.

Правила для level:
- Если has_python_experience = false, то level строго "none".
- Если has_python_experience = true и опыт до 2 лет, level = "beginner".
- Если has_python_experience = true и опыт 2-5 лет, level = "intermediate".
- Если has_python_experience = true и опыт более 5 лет, level = "advanced".


Резюме:
{resume}

Верни только JSON:
{{"has_python_experience": true/false, "level": "none/beginner/intermediate/advanced", "details": "только на русском"}}
"""
    print("\nПромпт:")
    print(prompt)

    try:
        print("\nВызываем LLM...")
        response = call_llm(prompt)
        print(f"\nОтвет модели:\n{response}")

        print("\nПопытка парсинга JSON...")
        result = parse_json_response(response)
        print(f"Распарсено: {result}")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    print("\nЗАПУСК ТЕСТА АГЕНТА\n")

    resume_key = "senior"
    resume = RESUMES[resume_key]

    print(f"Резюме для теста: {resume_key}")
    print("\n" + "=" * 60)

    try:
        test_python_experience_check(resume)
        print("\n" + "Тест завершен\n")
    except Exception as e:
        print(f"\nТест упал: {e}\n")

    print("=" * 60)
    print("Тест выполнен")
    print("=" * 60)
