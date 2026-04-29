import json
import re
from agent import call_smart_llm

class Preprocessor:
    def __init__(self):
        # Промпты вынесены сюда, чтобы файл был самодостаточным
        self.RESUME_PROMPT = """
        Ты — HR-ассистент. Преобразуй текст резюме в структурированный JSON на русском языке.
        
        ФОРМАТ:
        {{
          "name": "Имя или Аноним",
          "position": "Текущая роль",
          "level": "Junior/Middle/Senior",
          "experience_years": число,
          "skills": {{
            "hard": ["навык1", "навык2"],
            "tools": ["инструмент1"]
          }},
          "summary": "Краткое описание опыта"
        }}

        ТЕКСТ РЕЗЮМЕ:
        {text}
        """

        self.VACANCY_PROMPT = """
        Ты — Senior IT Recruiter. Структурируй вакансию в JSON.
        
        ФОРМАТ:
        {{
          "position": "Название",
          "level": "Требуемый уровень",
          "required_skills": ["скилл1", "скилл2"],
          "required_experience": число,
          "description": "Краткое описание сути"
        }}

        ТЕКСТ ВАКАНСИИ:
        {text}
        """

    def _parse_json(self, text):
        """Очистка ответа модели от лишнего текста и поиск JSON."""
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
            return json.loads(text)
        except:
            return {}

    def process_resume(self, raw_text):
        prompt = self.RESUME_PROMPT.format(text=raw_text[:4000])
        # Используем умную модель для качественного парсинга
        response = call_smart_llm(prompt)
        # Если пришел словарь (уже распарсенный в agent.py), возвращаем его
        if isinstance(response, dict):
            return response
        return self._parse_json(response)

    def process_vacancy(self, raw_text):
        prompt = self.VACANCY_PROMPT.format(text=raw_text[:4000])
        response = call_smart_llm(prompt)
        if isinstance(response, dict):
            return response
        return self._parse_json(response)