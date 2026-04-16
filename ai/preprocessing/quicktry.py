# quick_test.py
from resume_sorter import ResumeSorter


def quick_test():
    """Быстрый тест модели"""

    # Создаем БД
    import create_test_db
    db_path = create_test_db.create_test_database()

    # Создаем сортировщик
    sorter = ResumeSorter(db_path)

    # Простой критерий
    criteria = {
        "нужны": "Python разработчики с опытом Django",
        "мин опыт": "3 года"
    }

    # Сортируем
    result = sorter.sort_by_criteria(criteria, limit=10)

    # Выводим результат
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТ СОРТИРОВКИ:")
    print("=" * 50)

    for i, cand in enumerate(result, 1):
        print(f"{i}. {cand['name']} - {cand.get('match_score', 0)}%")
        print(f"   {cand['position']}, {cand['experience_years']} лет")
        print(f"   {cand.get('match_explanation', '')[:100]}...")
        print()


if __name__ == "__main__":
    quick_test()