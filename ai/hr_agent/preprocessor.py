import json
import re

class Preprocessor:
    def __init__(self):
        self.RESUME_PROMPT = """
        Ты — HR-ассистент. Преобразуй текст резюме в структурированный JSON на русском языке.
        
        ПРАВИЛА ИЗВЛЕЧЕНИЯ:
        - name: полное имя и фамилия из текста. Если не найдено — null (не придумывай)
        - phone: номер телефона из текста. Если не найдено — null
        - email: email из текста. Если не найдено — null
        - position: текущая или желаемая должность
        - level: Junior/Middle/Senior на основе опыта
        - experience_years: суммарный опыт в годах, число
        - skills.hard: технические навыки списком
        - skills.tools: инструменты и фреймворки списком
        - summary: 2-3 предложения об опыте, только факты

        ФОРМАТ ОТВЕТА:
        {{
          "name": null,
          "phone": null,
          "email": null,
          "position": "",
          "level": "",
          "experience_years": 0,
          "skills": {{
            "hard": [],
            "tools": []
          }},
          "summary": ""
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
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            return json.loads(match.group(0)) if match else json.loads(text)
        except:
            return {}

    def process_resume(self, raw_text):
        # ИМПОРТ ВНУТРИ МЕТОДА
        from agent import call_smart_llm
        prompt = self.RESUME_PROMPT.format(text=raw_text[:4000])
        response = call_smart_llm(prompt)
        return response if isinstance(response, dict) else self._parse_json(response)

    def process_vacancy(self, raw_text):
        # ИМПОРТ ВНУТРИ МЕТОДА
        from agent import call_smart_llm
        prompt = self.VACANCY_PROMPT.format(text=raw_text[:4000])
        response = call_smart_llm(prompt)
        return response if isinstance(response, dict) else self._parse_json(response)