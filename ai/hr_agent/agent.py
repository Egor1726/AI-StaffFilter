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
    DEBUG
)

# ------------------------
# JSON PARSER
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
def parse_json_response(text: str):
    """
    Извлекает JSON из любого текста. Если не находит — возвращает пустой словарь.
    """
    if not text or not isinstance(text, str):
        return {}

    # Ищем всё между первой { и последней }
    match = re.search(r'(\{[\s\S]*\})', text)
    if match:
        clean_text = match.group(1)
    else:
        clean_text = text

    # Убираем артефакты разметки
    clean_text = clean_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(clean_text)
    except Exception as e:
        if DEBUG:
            print(f"❌ Ошибка парсинга: {e}")
            # Выводим кусок текста для понимания проблемы
            snippet = text[:200].replace('\n', ' ')
            print(f"Сырой текст: {snippet}...")
        
        # Последняя попытка: чистка комментариев
        try:
            stripped = re.sub(r'//.*', '', clean_text)
            return json.loads(stripped)
        except:
            return {}

# ------------------------
# LLM CORE
# ------------------------

def call_llm_model(model_name: str, prompt: str, temperature: float, num_predict: int):
    """
    Вызов модели БЕЗ параметра format='json' для большей стабильности Llama 3.1.
    """
    try:
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            # format="json",  <-- УБРАНО: часто вызывает пустые ответы на малых моделях
            options={
                "temperature": temperature,
                "num_predict": num_predict,
                "top_p": 0.9,
            },
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"⚠️ Ошибка Ollama ({model_name}): {e}")
        return ""


def call_llm_safe(model, prompt, temperature, max_tokens):
    for attempt in range(MAX_RETRIES):
        raw = call_llm_model(model, prompt, temperature, max_tokens)
        if raw:
            data = parse_json_response(raw)
            # Если данных нет вообще — ретрай. Если есть хоть какой-то JSON — принимаем.
            if data: 
                return data
        
        if DEBUG:
            print(f"[{model}] Попытка {attempt+1} не удалась...")
            
    return {} # Возвращаем пустой словарь вместо заглушки со score


# ------------------------
# PROMPTS
# ------------------------

FAST_MATCH_PROMPT = """You are an HR filter. Compare candidate to vacancy.
Return ONLY a valid JSON object. No markdown, no code blocks, no extra text.

RULES:
- match: true if candidate is in same/adjacent field OR has 1+ key skills from vacancy
- score: 0-100. Be lenient: 50-69 = "pass to next stage", 0-29 = "wrong field", 70+ = "strong match"
- reason: short string (<80 chars), in Russian
- If unsure → set match:true, score:55. Better false positive than losing a good candidate.

[VACANCY]
{vacancy}

[RESUME]
{candidate}

[OUTPUT FORMAT - EXACTLY THIS, in Russian for 'reason']
{{
  "match": true,
  "score": 55,
  "reason": "краткая причина на русском"
}}"""


SMART_MATCH_PROMPT = """Ты — ведущий технический ассессор. Кандидаты уже прошли первичный отсев. Проведи глубокий аудит и выдай детализированную оценку для финального ранжирования.

ИЗВЛЕЧЕНИЕ ДАННЫХ:
- name, phone, email: бери ТОЛЬКО из текста резюме. Если нет — ставь null. Не выдумывай.
- phone: оставь как есть, не нормализуй.
- email: проверяй наличие @ и домена.

СИСТЕМА ОЦЕНИВАНИЯ (веса):
1. Stack & Hard Skills (40%): Совпадение стека, глубина опыта.
2. Experience Relevance (30%): Длительность, масштаб задач, домен.
3. Architecture & Context (20%): Процессы, методологии, софт-скиллы.
4. Adjustments (-10% до +10%): Гэпы, job-hopping, pet-projects, сертификаты.

ПРАВИЛА:
- score: целое 0-100, округляй до 5. Считай по весам.
- strengths: 1-3 пункта, только конкретика ("5 лет в HighLoad", а не "ответственный").
- weaknesses: 0-3 пункта. Только явные красные флаги. Нет флагов — пустой массив.
- summary: 2-3 предложения, сухо, только факты для сравнения.
- breakdown: объект с баллами по критериям. score должен коррелировать с ним.
- Верни СТРОГО JSON. Без markdown, без комментариев.

[ВАКАНСИЯ]
{vacancy}

[РЕЗЮМЕ]
{candidate}

[ФОРМАТ ОТВЕТА]
{{
  "name": null,
  "contact": {{"phone": null, "email": null}},
  "score": 75,
  "summary": "краткое описание",
  "breakdown": {{
    "stack_match": 80,
    "experience_relevance": 70,
    "architecture_context": 65,
    "adjustment": 5
  }},
  "strengths": ["пункт1", "пункт2"],
  "weaknesses": ["пункт1"]
}}"""


# ------------------------
# MATCHING LOGIC
# ------------------------

def fast_filter(candidate: dict, vacancy: dict):
    # Берем только суть, чтобы модель не "тупила" от объема
    cand_brief = {
        "pos": candidate.get("position"),
        "skills": candidate.get("skills"),
        "exp": candidate.get("experience_years")
    }
    
    prompt = FAST_MATCH_PROMPT.format(
        candidate=json.dumps(cand_brief, ensure_ascii=False),
        vacancy=json.dumps(vacancy, ensure_ascii=False)[:1000],
    )
    return call_fast_llm(prompt)


def smart_score(candidate: dict, vacancy: dict):
    prompt = SMART_MATCH_PROMPT.format(
        candidate=json.dumps(candidate, ensure_ascii=False)[:2000],
        vacancy=json.dumps(vacancy, ensure_ascii=False)[:2000],
    )
    return call_smart_llm(prompt)