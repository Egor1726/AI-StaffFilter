import json
import re
from typing import Dict, Any
from agent import Agent


# =====================
# PROMPT
# =====================

RESUME_PROMPT = """
Ты эксперт HR и Data Engineer.

Преобразуй резюме в СТРОГО валидный JSON.

ТРЕБОВАНИЯ:
- Только JSON
- Не выдумывай
- Если нет данных → null
- Навыки в lowercase
- Удали дубликаты
- Сократи описание опыта

ФОРМАТ:

{
  "name": string | null,
  "age": number | null,
  "location": string | null,
  "citizenship": string | null,
  "position": string | null,
  "employment_type": string | null,
  "work_format": [string],
  "experience_years": number,

  "skills": [string],

  "languages": [
    {"name": string, "level": string}
  ],

  "education": string | null,

  "experience": [
    {
      "company": string,
      "role": string,
      "duration": string,
      "domain": string | null,
      "stack": [string]
    }
  ],

  "summary": string
}

РЕЗЮМЕ:
{text}
"""


# =====================
# UTILS
# =====================

def clean_llm_output(text: str) -> str:
    text = re.sub(r"```json|```", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


def safe_json_load(text: str):
    try:
        return json.loads(text)
    except:
        return None


def truncate_text(text: str, max_chars=12000):
    return text[:max_chars]


class Preprocessor:
    def __init__(self):
        self.agent = Agent()

    def process_resume(self, text: str) -> Dict[str, Any]:
        text = truncate_text(text)

        prompt = RESUME_PROMPT.format(text=text)

        for _ in range(3):
            try:
                raw = self.agent.generate(prompt)
                cleaned = clean_llm_output(raw)
                data = safe_json_load(cleaned)

                if data:
                    return data
            except:
                continue

        raise ValueError("Ошибка парсинга резюме")