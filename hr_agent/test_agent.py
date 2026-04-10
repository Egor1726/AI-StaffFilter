import json
from agent import evaluate_candidate

with open("test_data/vacancy.txt", "r", encoding="utf-8") as f:
    vacancy = f.read()

candidates = [
    # 1 — полностью не подходит
    {
        "id": "candidate_0001",
        "text": "Имя: Олег Смирнов\nДолжность: Frontend Developer\nОпыт: 1 год\nНавыки: JavaScript, React, HTML, CSS, Figma\nОбразование: Онлайн-курсы, 2023\nЗарплата: 80000 руб\nО себе: Верстаю сайты и делаю интерфейсы. Python не знаю, ML не изучал, с данными не работал.",
        "metadata": {
            "candidate_id": "candidate_0001",
            "name": "Олег Смирнов",
            "email": "oleg@mail.ru",
            "phone": "+7-900-000-00-01",
            "position": "Frontend Developer",
            "experience_years": "1",
            "skills": "JavaScript, React, HTML, CSS, Figma",
            "education": "Онлайн-курсы, 2023",
            "expected_salary": "80000 руб"
        }
    },
    # 2 — средний
    {
        "id": "candidate_0002",
        "text": "Имя: Дмитрий Волков\nДолжность: Data Scientist\nОпыт: 4 года\nНавыки: Python, pandas, scikit-learn, XGBoost, SQL, Docker, Git\nОбразование: МГУ, Математика, 2019\nЗарплата: 230000 руб\nО себе: Строю предсказательные модели для бизнеса. Работал с классификацией и регрессией. С LLM и RAG не работал, NLP поверхностно.",
        "metadata": {
            "candidate_id": "candidate_0002",
            "name": "Дмитрий Волков",
            "email": "volkov@yandex.ru",
            "phone": "+7-900-000-00-02",
            "position": "Data Scientist",
            "experience_years": "4",
            "skills": "Python, pandas, scikit-learn, XGBoost, SQL, Docker, Git",
            "education": "МГУ, Математика, 2019",
            "expected_salary": "230000 руб"
        }
    },
    # 3 — средний
    {
        "id": "candidate_0003",
        "text": "Имя: Анна Белова\nДолжность: Python Developer\nОпыт: 3 года\nНавыки: Python, TensorFlow, pandas, Docker, Git, PostgreSQL\nОбразование: МГТУ, Информатика, 2020\nЗарплата: 210000 руб\nО себе: Разрабатываю модели на TensorFlow, есть базовый опыт с NLP. RAG-системы не строила, LLM изучаю самостоятельно.",
        "metadata": {
            "candidate_id": "candidate_0003",
            "name": "Анна Белова",
            "email": "belova@gmail.com",
            "phone": "+7-900-000-00-03",
            "position": "Python Developer",
            "experience_years": "3",
            "skills": "Python, TensorFlow, pandas, Docker, Git, PostgreSQL",
            "education": "МГТУ, Информатика, 2020",
            "expected_salary": "210000 руб"
        }
    },
    # 4 — отличный
    {
        "id": "candidate_0004",
        "text": "Имя: Екатерина Лебедева\nДолжность: ML Engineer\nОпыт: 3 года\nНавыки: Python, PyTorch, HuggingFace, LangChain, FAISS, Docker, PostgreSQL, Git\nОбразование: МФТИ, Физтех, 2020\nЗарплата: 220000 руб\nО себе: Специализируюсь на NLP и языковых моделях. Строила RAG-пайплайны, файнтюнила LLM под бизнес-задачи. Деплоила модели в production через FastAPI.",
        "metadata": {
            "candidate_id": "candidate_0004",
            "name": "Екатерина Лебедева",
            "email": "lebedeva@email.com",
            "phone": "+7-900-000-00-04",
            "position": "ML Engineer",
            "experience_years": "3",
            "skills": "Python, PyTorch, HuggingFace, LangChain, FAISS, Docker, PostgreSQL, Git",
            "education": "МФТИ, Физтех, 2020",
            "expected_salary": "220000 руб"
        }
    },
    # 5 — отличный
    {
        "id": "candidate_0005",
        "text": "Имя: Мария Соколова\nДолжность: ML Engineer\nОпыт: 5 лет\nНавыки: Python, PyTorch, TensorFlow, HuggingFace, LangChain, FAISS, FastAPI, Docker, Git\nОбразование: ВШЭ, Прикладная математика, 2018\nЗарплата: 270000 руб\nО себе: 5 лет в ML, последние 2 года фокус на LLM и RAG-системах. Файнтюнила GPT-подобные модели, строила production RAG на LangChain + FAISS. Опыт деплоя через FastAPI, знаю английский B2.",
        "metadata": {
            "candidate_id": "candidate_0005",
            "name": "Мария Соколова",
            "email": "sokolova@gmail.com",
            "phone": "+7-900-000-00-05",
            "position": "ML Engineer",
            "experience_years": "5",
            "skills": "Python, PyTorch, TensorFlow, HuggingFace, LangChain, FAISS, FastAPI, Docker, Git",
            "education": "ВШЭ, Прикладная математика, 2018",
            "expected_salary": "270000 руб"
        }
    }
]

print("=" * 50)
for candidate in candidates:
    print(f"\nОцениваем: {candidate['metadata']['name']}")
    print("-" * 30)
    result = evaluate_candidate(candidate, vacancy)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 50)