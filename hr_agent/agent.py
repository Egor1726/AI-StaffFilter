import json
import ollama
import re

from config import (
    FAST_MODEL,
    SMART_MODEL,
    FAST_TEMP,
    SMART_TEMP,
    FAST_MAX_TOKENS,
    SMART_MAX_TOKENS,
    MAX_RETRIES,
)

# ------------------------
# JSON PARSER
# ------------------------

def parse_json_response(text: str):
    # Ищем всё, что находится внутри фигурных скобок { ... }
    # Это позволит игнорировать вводные слова модели и markdown-разметку
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        clean_text = match.group(0)
    else:
        clean_text = text

    try:
        return json.loads(clean_text)
    except Exception as e:
        # Если всё равно ошибка — выводим текст, чтобы понять, что пришло
        print(f"❌ Ошибка парсинга: {e}")
        print(f"Сырой текст от модели: {text[:200]}...") 
        return {}

# ------------------------
# LLM CORE
# ------------------------

def call_llm_model(model_name: str, prompt: str, temperature: float, num_predict: int):
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={
            "temperature": temperature,
            "num_predict": num_predict,
        },
    )
    return response["message"]["content"]


def call_llm_safe(model, prompt, temperature, max_tokens):
    for attempt in range(MAX_RETRIES):
        try:
            raw = call_llm_model(
                model,
                prompt,
                temperature,
                max_tokens + attempt * 100
            )
            return parse_json_response(raw)
        except Exception as e:
            print(f"[{model}] retry {attempt}: {e}")
    return {}


# ------------------------
# MODEL WRAPPERS
# ------------------------

def call_fast_llm(prompt: str):
    return call_llm_safe(
        FAST_MODEL,
        prompt,
        FAST_TEMP,
        FAST_MAX_TOKENS
    )


def call_smart_llm(prompt: str):
    return call_llm_safe(
        SMART_MODEL,
        prompt,
        SMART_TEMP,
        SMART_MAX_TOKENS
    )


FAST_MATCH_PROMPT = """[ROLE]: Ты — автоматический HR-фильтр. Работай строго по алгоритму. Никаких размышлений, только валидный JSON.

[INPUT]
ВАКАНСИЯ: {vacancy}
РЕЗЮМЕ: {candidate}

[HARD RULES]
1. DOMAIN_CHECK: Если вакансия IT, а кандидат из non-IT сфер (медицина, логистика, сфера услуг, госслужба, педагогика, строительство и т.д.) → match: false, score: 0.
2. SENIORITY_CHECK: Если вакансия требует Senior/Lead/5+ лет, а у кандидата <2 лет релевантного IT-опыта → match: false, score: 0.
3. STACK_CHECK: Если в вакансии указан критический стек (Python, NLP, SQL, React и т.д.), а в резюме нет ни одного упоминания или кейса с ним → match: false, score: 0.
4. Если все правила пройдены → match: true, score: 60.

[OUTPUT FORMAT]
Верни ТОЛЬКО JSON-объект. Без markdown, без комментариев, без пояснений.
{{
  "match": false,
  "score": 0,
  "reason": "краткая причина"
}}"""

SMART_MATCH_PROMPT = """[ROLE]: Ты — Senior Tech Lead. Проводи технический аудит резюме. Оценивай только факты, игнорируй воду. Твоя цель — выявить накрутку и ранжировать кандидатов.

[INPUT]
ВАКАНСИЯ: {vacancy}
РЕЗЮМЕ: {candidate}

[AUDIT ALGORITHM]
1. EXTRACT MUST-HAVE: Выпиши из вакансии критичные требования.
2. SKILL_VALIDATION: Ищи конкретные кейсы: "Что делал" + "Стек" + "Метрика". Просто "знаю/изучал" = 0 баллов.
3. ANTI_COPYPAST: Если формулировки из вакансии перенесены в резюме слово в слово без привязки к проектам — это накрутка. Снимай 20-30 баллов.
4. MANDATORY_CAP: Если вакансия требует API/Automation, а у кандидата его нет → score <= 60.
5. SCORING_RUBRIC: 0-40 (мусор/накрутка), 41-70 (пробелы), 71-85 (крепкий профиль), 86-100 (идеальный мэтч).

[OUTPUT FORMAT]
Верни ТОЛЬКО JSON-объект. Без markdown.
{{
  "score": 0,
  "match_quality": "low|medium|high",
  "strengths": [],
  "weaknesses": [],
  "red_flags": [],
  "reason": "технический вердикт"
}}"""


# ------------------------
# MATCHING
# ------------------------

def fast_filter(candidate: dict, vacancy: dict):
    prompt = FAST_MATCH_PROMPT.format(
        candidate=json.dumps(candidate, ensure_ascii=False)[:2000],
        vacancy=json.dumps(vacancy, ensure_ascii=False)[:2000],
    )
    return call_fast_llm(prompt)


def smart_score(candidate: dict, vacancy: dict):
    prompt = SMART_MATCH_PROMPT.format(
        candidate=json.dumps(candidate, ensure_ascii=False)[:2000],
        vacancy=json.dumps(vacancy, ensure_ascii=False)[:2000],
    )
    return call_smart_llm(prompt)