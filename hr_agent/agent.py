

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
Ты опытный HR с многолетней практикой в найме IT-специалистов. 
Перед тем как выставить score, последовательно рассуди по каждому пункту:

НАВЫКИ:
- Какие обязательные навыки из вакансии есть у кандидата напрямую?
- Какие навыки похожи но не совпадают точно — например scikit-learn вместо PyTorch, Flask вместо FastAPI?
- Насколько критична именно эта замена для данной роли?
- Есть ли у кандидата навыки которых нет в вакансии но которые усиливают его профиль?

ОПЫТ:
- Сколько лет опыта и в какой именно области — общий Python или именно ML/NLP/LLM?
- Работал ли кандидат с production-системами или только с учебными проектами?
- Есть ли опыт именно с языковыми моделями и RAG или только с классическим ML?
- Компенсирует ли глубина опыта в одной области отсутствие опыта в другой?

СООТВЕТСТВИЕ РОЛИ:
- Эта позиция требует ML Engineer — насколько близка текущая позиция кандидата к этому?
- Если кандидат backend-разработчик или data scientist — насколько реален переход на эту роль?
- Есть ли признаки что кандидат уже двигается в нужную сторону?

ЗАРПЛАТА:
- Вписывается ли ожидаемая зарплата в бюджет вакансии?
- Если превышает — насколько кандидат это оправдывает своим опытом?

После того как прошёлся по всем пунктам — выставь score как итоговое впечатление.
Не усредняй механически. Если кандидат закрывает самое критичное — это важнее чем 
несколько мелких пробелов. Если не хватает чего-то ключевого — это должно сильно 
тянуть score вниз даже при сильном остальном профиле.

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
  "comment": ""comment": "<если score >= 70: напиши что именно делает кандидата сильным, какие навыки особенно ценны для этой роли и почему стоит пригласить на собеседование | если score 40-69: напиши что есть хорошего но чего критически не хватает и стоит ли рассматривать при отсутствии лучших кандидатов | если score < 40: напиши коротко почему не подходит и что именно мешает — без воды, конкретно по стеку и опыту. Максимум 2-3 предложения>""
}}
"""
    return call_llm_safe(prompt)


def rank_candidates(candidates: list, vacancy: str) -> list:
    results = []

    for candidate in candidates:
        evaluation = evaluate_candidate(candidate, vacancy)
        results.append({
            "id": candidate["id"],
            "metadata": candidate["metadata"],
            "score": evaluation.get("score", 0),
            "evaluation": evaluation
        })

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank

    return ranked


if __name__ == "__main__":
    print("agent.py loaded OK")