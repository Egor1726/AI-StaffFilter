# create_test_db.py
import sqlite3
import json
from datetime import datetime


def create_test_database():
    """Создание тестовой базы данных с резюме"""

    # Создаем подключение к БД
    conn = sqlite3.connect('test_resumes.db')
    cursor = conn.cursor()

    # Создаем таблицу для резюме
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
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

    # Тестовые данные - 15 разных кандидатов
    test_resumes = [
        # Senior Python разработчики
        {
            'name': 'Иван Петров',
            'email': 'ivan.petrov@email.com',
            'phone': '+7-999-123-45-67',
            'position': 'Senior Python Developer',
            'experience_years': 7,
            'skills': json.dumps(['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Docker', 'Kubernetes', 'AWS', 'Redis']),
            'education': 'МГУ, Прикладная математика, 2016',
            'languages': json.dumps(['Русский (родной)', 'Английский (Upper-Intermediate)']),
            'expected_salary': '300 000 руб',
            'about': 'Опыт разработки высоконагруженных систем. Участвовал в создании микросервисной архитектуры. Есть опыт управления командой из 5 человек.'
        },

        {
            'name': 'Алексей Смирнов',
            'email': 'alex.smirnov@email.com',
            'phone': '+7-999-234-56-78',
            'position': 'Python Developer',
            'experience_years': 4,
            'skills': json.dumps(['Python', 'Flask', 'SQLAlchemy', 'MongoDB', 'Git', 'Docker']),
            'education': 'МФТИ, Информатика, 2019',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '200 000 руб',
            'about': 'Разработка backend для веб-приложений. Участие в полном цикле разработки.'
        },

        # Data Scientists
        {
            'name': 'Мария Иванова',
            'email': 'maria.ivanova@email.com',
            'phone': '+7-999-345-67-89',
            'position': 'Data Scientist',
            'experience_years': 5,
            'skills': json.dumps(['Python', 'SQL', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'ML']),
            'education': 'ВШЭ, Математика и статистика, 2018',
            'languages': json.dumps(['Русский (родной)', 'Английский (Advanced)']),
            'expected_salary': '280 000 руб',
            'about': 'Разработка ML моделей для предсказательной аналитики. Опыт работы с большими данными. Участие в соревнованиях Kaggle.'
        },

        {
            'name': 'Дмитрий Козлов',
            'email': 'dmitry.kozlov@email.com',
            'phone': '+7-999-456-78-90',
            'position': 'Junior Data Scientist',
            'experience_years': 1,
            'skills': json.dumps(['Python', 'SQL', 'Pandas', 'Matplotlib', 'Статистика']),
            'education': 'СПбГУ, Математика, 2022',
            'languages': json.dumps(['Русский (родной)', 'Английский (Pre-Intermediate)']),
            'expected_salary': '120 000 руб',
            'about': 'Выпускник курсов по Data Science. Участие в учебных проектах по анализу данных.'
        },

        # Frontend разработчики
        {
            'name': 'Елена Соколова',
            'email': 'elena.sokolova@email.com',
            'phone': '+7-999-567-89-01',
            'position': 'Senior Frontend Developer',
            'experience_years': 6,
            'skills': json.dumps(['JavaScript', 'TypeScript', 'React', 'Vue.js', 'Next.js', 'CSS', 'HTML', 'Webpack']),
            'education': 'ИТМО, Информационные системы, 2017',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '250 000 руб',
            'about': 'Разработка сложных интерфейсов. Оптимизация производительности. Наставничество.'
        },

        {
            'name': 'Павел Морозов',
            'email': 'pavel.morozov@email.com',
            'phone': '+7-999-678-90-12',
            'position': 'Frontend Developer',
            'experience_years': 3,
            'skills': json.dumps(['JavaScript', 'React', 'Redux', 'HTML', 'CSS', 'Git']),
            'education': 'МАИ, Информатика, 2020',
            'languages': json.dumps(['Русский (родной)', 'Английский (Elementary)']),
            'expected_salary': '150 000 руб',
            'about': 'Разработка SPA приложений. Адаптивная верстка.'
        },

        # Java разработчики
        {
            'name': 'Сергей Волков',
            'email': 'sergey.volkov@email.com',
            'phone': '+7-999-789-01-23',
            'position': 'Senior Java Developer',
            'experience_years': 8,
            'skills': json.dumps(['Java', 'Spring Boot', 'Hibernate', 'PostgreSQL', 'Kafka', 'Microservices', 'Maven']),
            'education': 'МГТУ им. Баумана, Программная инженерия, 2015',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '320 000 руб',
            'about': 'Разработка корпоративных приложений. Миграция с монолита на микросервисы.'
        },

        # DevOps
        {
            'name': 'Анна Белова',
            'email': 'anna.belova@email.com',
            'phone': '+7-999-890-12-34',
            'position': 'DevOps Engineer',
            'experience_years': 4,
            'skills': json.dumps(['Docker', 'Kubernetes', 'Jenkins', 'AWS', 'Terraform', 'Ansible', 'Linux', 'Bash']),
            'education': 'УрФУ, Информационная безопасность, 2019',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '260 000 руб',
            'about': 'Настройка CI/CD пайплайнов. Инфраструктура как код. Мониторинг и логирование.'
        },

        # Project Managers
        {
            'name': 'Михаил Новиков',
            'email': 'mikhail.novikov@email.com',
            'phone': '+7-999-901-23-45',
            'position': 'IT Project Manager',
            'experience_years': 6,
            'skills': json.dumps(
                ['Agile', 'Scrum', 'Kanban', 'Jira', 'Confluence', 'Team Management', 'Risk Management']),
            'education': 'РАНХиГС, Менеджмент, 2017',
            'languages': json.dumps(['Русский (родной)', 'Английский (Upper-Intermediate)']),
            'expected_salary': '280 000 руб',
            'about': 'Управление командами до 15 человек. Внедрение Agile. Успешная сдача проектов в срок.'
        },

        # QA Engineers
        {
            'name': 'Ольга Лебедева',
            'email': 'olga.lebedeva@email.com',
            'phone': '+7-999-012-34-56',
            'position': 'Senior QA Engineer',
            'experience_years': 5,
            'skills': json.dumps(['Manual Testing', 'Automation', 'Selenium', 'Python', 'JUnit', 'Postman', 'SQL']),
            'education': 'МЭИ, Информатика, 2018',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '210 000 руб',
            'about': 'Автоматизация тестирования. Написание тест-кейсов. Интеграционное тестирование.'
        },

        # Дополнительные кандидаты для разнообразия
        {
            'name': 'Владимир Соловьев',
            'email': 'vladimir.soloviev@email.com',
            'phone': '+7-999-111-22-33',
            'position': 'Fullstack Developer',
            'experience_years': 4,
            'skills': json.dumps(['Python', 'JavaScript', 'React', 'Django', 'PostgreSQL', 'REST API']),
            'education': 'КФУ, Информатика, 2019',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '220 000 руб',
            'about': 'Разработка как frontend, так и backend частей приложений.'
        },

        {
            'name': 'Татьяна Мороз',
            'email': 'tatiana.moroz@email.com',
            'phone': '+7-999-222-33-44',
            'position': 'Business Analyst',
            'experience_years': 4,
            'skills': json.dumps(['SQL', 'Excel', 'Power BI', 'Анализ требований', 'UML', 'BPMN']),
            'education': 'СПбГЭУ, Экономика, 2019',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '190 000 руб',
            'about': 'Сбор и анализ требований. Взаимодействие с заказчиком. Документирование.'
        },

        {
            'name': 'Артем Громов',
            'email': 'artem.gromov@email.com',
            'phone': '+7-999-333-44-55',
            'position': 'Security Engineer',
            'experience_years': 5,
            'skills': json.dumps(
                ['Network Security', 'Penetration Testing', 'Linux', 'Python', 'Wireshark', 'Metasploit']),
            'education': 'МИФИ, Информационная безопасность, 2018',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '270 000 руб',
            'about': 'Проведение пентестов. Анализ защищенности. Внедрение средств защиты.'
        },

        {
            'name': 'Кристина Цветкова',
            'email': 'kristina.tsvetkova@email.com',
            'phone': '+7-999-444-55-66',
            'position': 'UX/UI Designer',
            'experience_years': 3,
            'skills': json.dumps(['Figma', 'Adobe XD', 'Sketch', 'UI Design', 'UX Research', 'Прототипирование']),
            'education': 'Британская школа дизайна, 2020',
            'languages': json.dumps(['Русский (родной)', 'Английский (Intermediate)']),
            'expected_salary': '180 000 руб',
            'about': 'Дизайн интерфейсов для мобильных и веб-приложений. Проведение пользовательских интервью.'
        }
    ]

    # Добавляем данные
    for resume in test_resumes:
        cursor.execute('''
            INSERT INTO resumes (
                name, email, phone, position, experience_years, 
                skills, education, languages, expected_salary, about
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume['name'],
            resume['email'],
            resume['phone'],
            resume['position'],
            resume['experience_years'],
            resume['skills'],
            resume['education'],
            resume['languages'],
            resume['expected_salary'],
            resume['about']
        ))

    # Сохраняем изменения
    conn.commit()

    # Проверяем, что добавилось
    cursor.execute("SELECT COUNT(*) FROM resumes")
    count = cursor.fetchone()[0]

    print(f" Тестовая база данных создана!")
    print(f" Добавлено резюме: {count}")

    # Показываем структуру
    cursor.execute("PRAGMA table_info(resumes)")
    columns = cursor.fetchall()
    print("\n Структура таблицы resumes:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

    # Показываем несколько записей для примера
    print("\n👥 Примеры кандидатов:")
    cursor.execute("SELECT id, name, position, experience_years FROM resumes LIMIT 5")
    for row in cursor.fetchall():
        print(f"  {row[0]}. {row[1]} - {row[2]} ({row[3]} лет)")

    conn.close()
    return "test_resumes.db"


if __name__ == "__main__":
    db_path = create_test_database()
    print(f"\n База данных сохранена: {db_path}")