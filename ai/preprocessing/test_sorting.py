# test_sorting.py
from resume_sorter import ResumeSorter
import json


def test_different_criteria():
    """Тестирование разных критериев сортировки"""

    # Подключаемся к тестовой БД
    sorter = ResumeSorter('test_resumes.db')

    # Тест 1: Поиск Python разработчиков
    print("\n" + "=" * 60)
    print("ТЕСТ 1: Python разработчики с опытом от 3 лет")
    print("=" * 60)

    criteria1 = {
        "должность": "Python разработчик",
        "минимальный опыт": "3 года",
        "необходимые навыки": ["Python", "SQL", "Git"],
        "желательно": ["Django", "Docker"],
        "уровень английского": "Intermediate"
    }

    result1 = sorter.sort_by_criteria(criteria1, limit=20)

    print(f"\nНайдено кандидатов: {len(result1)}")
    for i, cand in enumerate(result1[:3], 1):
        print(f"\n{i}. {cand['name']} - {cand.get('match_score', 0)}%")
        print(f"   Должность: {cand['position']}")
        print(f"   Опыт: {cand['experience_years']} лет")
        print(f"   Навыки: {', '.join(json.loads(cand['skills'])[:5])}")

    # Тест 2: Поиск Data Scientist
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Data Scientist с опытом от 2 лет")
    print("=" * 60)

    criteria2 = {
        "должность": "Data Scientist / ML специалист",
        "обязательные навыки": ["Python", "Pandas", "SQL", "Machine Learning"],
        "желательные навыки": ["TensorFlow", "PyTorch"],
        "опыт": "от 2 лет",
        "образование": "математическое или техническое"
    }

    result2 = sorter.sort_by_criteria(criteria2, limit=20)

    print(f"\nНайдено кандидатов: {len(result2)}")
    for i, cand in enumerate(result2[:3], 1):
        print(f"\n{i}. {cand['name']} - {cand.get('match_score', 0)}%")
        print(f"   Должность: {cand['position']}")
        print(f"   Опыт: {cand['experience_years']} лет")

    # Тест 3: Поиск Senior разработчиков (лидов)
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Senior/Lead разработчики")
    print("=" * 60)

    criteria3 = {
        "уровень": "Senior или Lead",
        "опыт": "более 5 лет",
        "навыки управления": ["team management", "mentoring"],
        "технический стек": "широкий",
        "зарплатные ожидания": "до 350 000 руб"
    }

    result3 = sorter.sort_by_criteria(criteria3, limit=20)

    print(f"\nНайдено кандидатов: {len(result3)}")
    for i, cand in enumerate(result3[:3], 1):
        print(f"\n{i}. {cand['name']} - {cand.get('match_score', 0)}%")
        print(f"   Должность: {cand['position']}")
        print(f"   Опыт: {cand['experience_years']} лет")
        print(f"   Ожидания: {cand['expected_salary']}")

    # Сохраняем результаты
    sorter.export_results(result1, "python_devs.xlsx")
    sorter.export_results(result2, "data_scientists.xlsx")
    sorter.export_results(result3, "seniors.xlsx")

    return result1, result2, result3


def test_filter_by_skills():
    """Тестирование фильтрации по навыкам"""

    print("\n" + "=" * 60)
    print("ТЕСТ: Быстрая фильтрация по навыкам")
    print("=" * 60)

    sorter = ResumeSorter('test_resumes.db')

    # Ищем кандидатов с разными наборами навыков
    skills_sets = [
        ["Python", "Django", "PostgreSQL"],
        ["Python", "Pandas", "Scikit-learn"],
        ["Docker", "Kubernetes", "AWS"],
        ["React", "JavaScript", "TypeScript"],
        ["Java", "Spring", "Hibernate"]
    ]

    for skills in skills_sets:
        print(f"\n🔍 Поиск по навыкам: {skills}")
        matches = sorter.filter_by_skills(skills, min_match=2)

        print(f"   Найдено: {len(matches)} кандидатов")
        for cand in matches[:2]:
            print(f"   • {cand['name']} - {cand.get('match_percent', 0):.0f}% совпадений")
            print(f"     Навыки: {', '.join(json.loads(cand['skills'])[:3])}")


def test_complex_criteria():
    """Тестирование сложных критериев"""

    print("\n" + "=" * 60)
    print("ТЕСТ: Сложные критерии отбора")
    print("=" * 60)

    sorter = ResumeSorter('test_resumes.db')

    # Пример сложного запроса
    complex_criteria = {
        "требования": """
            Ищем технического лида для команды из 5 разработчиков.
            Стек: Python/Java, микросервисы, Docker, Kubernetes.
            Обязателен опыт управления командой и английский для общения с заказчиком.
            Желательно знание облачных технологий (AWS/GCP).
        """,
        "ключевые слова": ["lead", "senior", "team", "management", "microservices"],
        "минимальный опыт": 5,
        "приоритеты": {
            "опыт управления": "высокий",
            "технический стек": "средний",
            "английский": "средний",
            "образование": "низкий"
        }
    }

    result = sorter.sort_by_criteria(complex_criteria, limit=20)

    print(f"\nНайдено кандидатов: {len(result)}")
    for i, cand in enumerate(result[:5], 1):
        print(f"\n{i}. {cand['name']} - {cand.get('match_score', 0)}%")
        print(f"   Должность: {cand['position']}")
        print(f"   Опыт: {cand['experience_years']} лет")
        if 'strengths' in cand:
            print(f"   Сильные стороны: {', '.join(cand['strengths'][:2])}")


def main():
    """Главная функция тестирования"""

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МОДЕЛИ СОРТИРОВКИ РЕЗЮМЕ")
    print("=" * 60)
    print("\nСначала создаем тестовую БД...")

    # Создаем БД
    import create_test_db
    create_test_db.create_test_database()

    # Запускаем тесты
    test_different_criteria()
    test_filter_by_skills()
    test_complex_criteria()

    print("\n" + "=" * 60)
    print("✅ Все тесты завершены!")
    print("📁 Результаты сохранены в Excel файлах:")
    print("   - python_devs.xlsx")
    print("   - data_scientists.xlsx")
    print("   - seniors.xlsx")


if __name__ == "__main__":
    main()