import json

import ollama

from config import MODEL_NAME


def call_llm(prompt: str, num_predict: int = 350) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={
            "temperature": 0.0,
            "num_predict": num_predict,
        },
    )
    return response["message"]["content"]


def parse_json_response(text: str) -> dict:
    """Парсинг JSON из ответа модели."""
    text = text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text[:-3]

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    return json.loads(text)


def call_llm_safe(prompt: str, retries: int = 2, num_predict: int = 350) -> dict:
    """Вызов модели с повторными попытками при сбое парсинга."""
    for attempt in range(retries):
        try:
            current_num_predict = num_predict + attempt * 120
            raw = call_llm(prompt, num_predict=current_num_predict)
            return parse_json_response(raw)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            print(f"[attempt {attempt + 1}/{retries}] Ошибка парсинга: {e}")
    return {}


def extract_info(resume: str) -> dict:
    """
    Извлечение структурированной информации из текста резюме.
    Возвращает: имя, навыки, опыт, образование, контакты.
    """
    prompt = f"""
Ты извлекаешь структуру из резюме. Верни только JSON без markdown и без пояснений.

Нужные поля:
- name
- position
- experience_years
- skills
- education
- email
- phone
- salary
- summary

Правила:
- skills = массив коротких строк без дублей
- experience_years = число или null
- summary = 1-2 коротких предложения по сути опыта
- если поле не найдено, используй null или пустой массив

Резюме:
{resume}

Формат ответа:
{{
  "name": null,
  "position": null,
  "experience_years": null,
  "skills": [],
  "education": null,
  "email": null,
  "phone": null,
  "salary": null,
  "summary": null
}}
"""
    return call_llm_safe(prompt, num_predict=320)

"""
Написать пример для оценки скора и промпт поподробнее, с указанием что именно должно совпадать, какие навыки важные, и т.д.  
"""
def evaluate_candidate(candidate: dict, vacancy: str) -> dict:
    candidate_text = candidate.get("text", "")
    metadata = candidate.get("metadata", {})
    candidate_name = metadata.get("name", "")
    candidate_id = metadata.get("candidate_id") or candidate.get("id", "")

    prompt = f"""
Ты оцениваешь кандидата на вакансию. Верни только JSON без markdown и без пояснений.

=== ВАКАНСИЯ ===
{vacancy}

=== КАНДИДАТ ===
ID: {candidate_id}
Имя: {candidate_name}
Текст резюме:
{candidate_text}

=== КАК ОЦЕНИВАТЬ ===
Сделай оценку УНИВЕРСАЛЬНО для любой вакансии, опираясь ТОЛЬКО на текст вакансии выше.

1) Сначала выдели из вакансии:
- обязательные требования (must-have),
- желательные требования (nice-to-have),
- условия (зарплата, формат, график, локация и т.д., если они явно указаны).

2) Затем сравни кандидата с вакансией:
- matched_skills: включай только то, что явно требуется в вакансии и действительно есть у кандидата;
- missing_skills: включай только то, что требуется в вакансии, но у кандидата не найдено;
- учитывай частичные/эквивалентные совпадения (похожие технологии) как частичный плюс, но не как полное совпадение must-have;
- не дублируй пункты и не добавляй в missing то, что уже есть у кандидата.

3) По опыту и роли:
- оцени релевантность опыта именно к данной вакансии;
- коммерческий и production-опыт приоритетнее учебных и pet-проектов;
- experience_match = true только если кандидат в целом тянет обязательный уровень по опыту.

4) По условиям:
- salary_match = true только если ожидания кандидата вписываются в условия вакансии,
  если в вакансии указана зарплата; если зарплата в вакансии не указана, ставь true.

5) Итоговый score (0-100):
- это вероятность, что кандидат подойдет на эту вакансию;
- не считай по формуле, но must-have влияют сильнее nice-to-have;
- если провалены ключевые must-have, score должен заметно снижаться;
- используй всю шкалу, не округляй до десятков.

Пиши кратко, фактически и без противоречий.

=== ФОРМАТ ОТВЕТА ===
Верни ТОЛЬКО JSON без markdown:
{{
  "candidate_id": "{candidate_id}",
  "name": "{candidate_name}",
  "score": <число от 0 до 100>,
  "matched_skills": [<что есть и нужно>],
  "missing_skills": [<чего нет но требуется>],
  "experience_match": <true/false>,
  "salary_match": <true/false>,
    "comment": "<1-3 коротких предложения: ключевые совпадения, ключевые пробелы и итог по интервью>"
}}
"""
    return call_llm_safe(prompt, num_predict=220)


def rank_candidates(candidates: list, vacancy: str) -> list:
    results = []

    for candidate in candidates:
        evaluation = evaluate_candidate(candidate, vacancy)
        raw_score = evaluation.get("score", 0)
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0

        results.append({
            "id": candidate["id"],
            "metadata": candidate["metadata"],
            "score": score,
            "evaluation": evaluation,
        })

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank

    return ranked


if __name__ == "__main__":
    print("agent.py loaded OK")