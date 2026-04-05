# speed_test.py
from resume_sorter import ResumeSorter
import time


def test_speed():
    sorter = ResumeSorter('test_resumes.db')

    # Тест с разным количеством резюме
    for limit in [5, 10, 20]:
        print(f"\n🔍 Тест с {limit} резюме:")

        start = time.time()
        results = sorter.sort_by_criteria(
            {"должность": "Python разработчик"},
            limit=limit
        )
        end = time.time()

        print(f"   Время: {end - start:.1f} секунд")
        print(f"   Найдено: {len(results)} кандидатов")

    sorter.close()


if __name__ == "__main__":
    test_speed()