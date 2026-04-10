

import json
import ollama
from config import MODEL_NAME


def call_llm(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0.1,
            "num_predict": 1000
        }
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

"""
Написать пример для оценки скора и промпт поподробнее, с указанием что именно должно совпадать, какие навыки важные, и т.д.  
"""
def evaluate_candidate(candidate: dict, vacancy: str) -> dict:
    prompt = f"""
Ты — опытный HR-аналитик. Тебе нужно оценить кандидата на вакансию.

=== ВАКАНСИЯ ===
{vacancy}

=== КАНДИДАТ ===
{candidate["text"]}

=== КАК ДУМАТЬ ===
Перед тем как выставить score, рассуди про себя:
- Насколько реально этот человек справится с работой?
- Какие требования он закрывает уверенно, какие частично, каких нет совсем?
- Компенсирует ли его опыт недостающие навыки?
- Есть ли что-то что делает его особенно сильным или слабым кандидатом?
- Насколько критичны именно те навыки которых не хватает?

Score — это твоя экспертная оценка вероятности того, что кандидат подойдёт на эту роль.
Не считай по формуле. Думай как живой человек который провёл тысячи собеседований.
Используй всю шкалу от 0 до 100, не округляй до десяток.

=== ФОРМАТ ОТВЕТА ===
Верни ТОЛЬКО JSON без markdown:
{{
  "candidate_id": "{candidate["metadata"]["candidate_id"]}",
  "name": "{candidate["metadata"]["name"]}",
  "score": <число от 0 до 100>,
  "matched_skills": [<что есть и нужно>],
  "missing_skills": [<чего нет но требуется>],
  "experience_match": <true/false>,
  "salary_match": <true/false>,
  "comment": "<1-2 предложения итогового вывода с твоими комментариями и рекомендациями для HR>"
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