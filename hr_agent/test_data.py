# test_data.py
"""
Тестовые данные для разработки и проверки агента.
"""

# Резюме 1: Опытный разработчик
RESUME_SENIOR_PYTHON = """
ФИО: Иван Петров
Опыт: 5 лет
Должность: Senior Python Developer

Навыки:
- Python (Django, FastAPI)
- PostgreSQL, Redis
- Docker, Kubernetes
- AWS, GCP
- Git, CI/CD

Образование:
- Бакалавр по специальности "Информатика"
- МГУ им. Ломоносова

Опыт работы:
- ООО "Техкомпания" - Senior Backend Developer (2021-2024)
  * Разработка микросервисов на Python
  * Оптимизация БД снизила загрузку на 40%
  
- ООО "СтартапИТ" - Python Developer (2019-2021)
  * Разработка REST API
  * Интеграция с внешними сервисами
"""

# Резюме 2: Junior разработчик
RESUME_JUNIOR = """
ФИО: Мария Сидорова
Опыт: 1 год
Должность: Junior Python Developer

Навыки:
- Python (базовый уровень)
- JavaScript, HTML, CSS
- MySQL
- Git

Образование:
- Студент курса "Python для начинающих"
- Школа программирования "CodePath"

Опыт работы:
- ООО "СтартапСофт" - Junior Developer (2023-2024)
  * Доработка фронтенда
  * Исправление багов в backend API
"""

# Резюме 3: Frontend разработчик
RESUME_FRONTEND = """
ФИО: Денис Золотухин
Опыт: 3 года
Должность: Frontend Developer

Навыки:
- JavaScript, TypeScript
- React, Vue.js
- HTML5, CSS3, SCSS
- Docker

Образование:
- Бакалавр "Web-разработка"
- СПбГУ

Опыт работы:
- АО "МобильОС" - Senior Frontend Developer (2021-2024)
  * Разработка React приложений
  * Оптимизация производительности UI
"""
# Резюме 4: Студент без опыта
RESUME_WITHOUT_EXPERIENCE = """
ФИО: Леха Иванов
Опыт: 0 лет
Должность: Студент
Навыки: - Python (изучаю)
Образование: Студент курса "Python для начинающих"
Опыт работы: Нет опыта работы
"""
RESUMES = {
    "senior": RESUME_SENIOR_PYTHON,
    "junior": RESUME_JUNIOR,
    "frontend": RESUME_FRONTEND,
    "without_experience": RESUME_WITHOUT_EXPERIENCE,
}
