# agent.py
"""
Модуль работы с LLM-агентом.
"""

import json
import ollama
from config import MODEL_NAME, MODEL_OPTIONS


def call_llm(prompt: str) -> str:
    """Вызов LLM через Ollama."""
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


def extract_info(resume: str) -> dict:
    """Извлечение информации из резюме."""
    # TODO: добавить промпт
    pass


def evaluate_candidate(resume: str, vacancy: str) -> dict:
    """Оценка соответствия кандидата вакансии."""
    # TODO: добавить промпт
    pass


def rank_candidates(candidates: list, vacancy: str) -> list:
    """Ранжирование кандидатов."""
    # TODO: добавить промпт
    pass


def generate_feedback(resume: str, evaluation: dict) -> dict:
    """Генерация фидбека."""
    # TODO: добавить промпт
    pass


if __name__ == "__main__":
    print("agent.py loaded OK")