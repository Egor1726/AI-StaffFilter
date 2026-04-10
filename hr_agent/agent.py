

import json
import ollama
from config import MODEL_NAME, MODEL_OPTIONS


def call_llm(prompt: str) -> str:
    """Базовый вызов модели через Ollama."""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options=MODEL_OPTIONS
    )
    return response["message"]["content"]


def parse_json_response(text: str) -> dict:
    """Парсинг JSON из ответа модели."""
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def call_llm_safe(prompt: str, retries: int = 3) -> dict:
    """Вызов модели с повторными попытками при сбое парсинга."""
    for attempt in range(retries):
        try:
            raw = call_llm(prompt)
            return parse_json_response(raw)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[attempt {attempt + 1}/{retries}] Ошибка парсинга: {e}")
    return {}


# ─────────────────────────────────────────────
# Основные функции агента
# ─────────────────────────────────────────────

def extract_info(resume: str) -> dict:
    """
    Извлечение структурированной информации из текста резюме.
    Возвращает: имя, навыки, опыт, образование, контакты.
    """
    prompt = f"""
    TODO: написать промпт

    Резюме:
    {resume}
    """
    return call_llm_safe(prompt)


def evaluate_candidate(candidate: dict, vacancy: str) -> dict:
    """
    Оценка соответствия кандидата вакансии.
    """
    prompt = f"""
Ты — HR-специалист. Оцени соответствие кандидата вакансии.

Вакансия:
{vacancy}

Кандидат:
{candidate["text"]}

Верни ТОЛЬКО JSON, без пояснений, без markdown:
{{
  "candidate_id": "{candidate["metadata"]["candidate_id"]}",
  "name": "{candidate["metadata"]["name"]}",
  "score": <число от 0 до 100>,
  "matched_skills": [<навыки которые совпали с вакансией>],
  "missing_skills": [<навыки из вакансии которых нет у кандидата>],
  "experience_match": <true если опыт >= 3 лет иначе false>,
  "salary_match": <true если зарплата <= 280000 иначе false>,
  "verdict": "<подходит / не подходит / рассмотреть>",
  "comment": "<1-2 предложения почему>"
}}
"""
    return call_llm_safe(prompt)


def generate_feedback(resume: str, evaluation: dict) -> dict:
    """
    Генерация фидбека для кандидата на основе оценки.
    Возвращает: решение, сильные стороны, зоны роста, текст письма.
    """
    prompt = f"""
    TODO: написать промпт

    Резюме:
    {resume}

    Оценка:
    {json.dumps(evaluation, ensure_ascii=False, indent=2)}
    """
    return call_llm_safe(prompt)


def rank_candidates(candidates: list, vacancy: str) -> list:
    """
    Ранжирование списка кандидатов по вакансии.
    Оценивает каждого через evaluate_candidate, сортирует по score.
    """
    results = []

    for i, resume in enumerate(candidates):
        evaluation = evaluate_candidate(resume, vacancy)
        results.append({
            "index": i,
            "resume": resume,
            "score": evaluation.get("score", 0),
            "evaluation": evaluation
        })

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank

    return ranked


if __name__ == "__main__":
    print("agent.py loaded OK")