# resume_sorter.py
import sqlite3
import json
from langchain_ollama import ChatOllama
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime


class ResumeSorter:
    """
    Класс для сортировки резюме по критериям с использованием LLM
    """

    def __init__(self, db_path: str, model_name: str = "qwen2.5:1.5b"):
        """
        Инициализация сортировщика резюме

        Args:
            db_path: путь к базе данных SQLite
            model_name: имя модели в Ollama
        """
        # Подключение к базе данных
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Подключение к LLM
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.2,  # Низкая температура для более точных ответов
            base_url="http://localhost:11434"
        )

        print(f"✅ Подключено к БД: {db_path}")
        print(f"✅ Модель загружена: {model_name}")

        # Определяем таблицу с резюме
        self.table_name = self._detect_table()

    def _detect_table(self) -> str:
        """Определить таблицу с резюме"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in self.cursor.fetchall()]

        # Ищем таблицу с резюме
        resume_keywords = ['resume', 'candidate', 'applicant', 'employee', 'hr']
        for table in tables:
            if any(keyword in table.lower() for keyword in resume_keywords):
                print(f"📋 Найдена таблица: {table}")
                return table

        # Если не нашли, берем первую таблицу
        if tables:
            print(f"📋 Используем таблицу: {tables[0]}")
            return tables[0]

        raise Exception("В базе данных нет таблиц")

    def get_candidates(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Получить список кандидатов из БД

        Args:
            limit: максимальное количество кандидатов

        Returns:
            List[Dict]: список кандидатов
        """
        query = f"SELECT * FROM {self.table_name}"
        if limit:
            query += f" LIMIT {limit}"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        candidates = []
        for row in rows:
            candidate = dict(row)

            # Преобразуем JSON строки в объекты
            for key, value in candidate.items():
                if isinstance(value, str):
                    # Проверяем, не является ли строка JSON массивом
                    if value.startswith('[') and value.endswith(']'):
                        try:
                            candidate[key] = json.loads(value)
                        except:
                            pass
                    # Проверяем, не является ли строка JSON объектом
                    elif value.startswith('{') and value.endswith('}'):
                        try:
                            candidate[key] = json.loads(value)
                        except:
                            pass

            candidates.append(candidate)

        return candidates

    def sort_by_criteria(self, criteria: Dict[str, Any], limit: int = 50) -> List[Dict]:
        """
        Сортировка кандидатов по заданным критериям

        Args:
            criteria: словарь с критериями отбора
            limit: максимальное количество кандидатов для анализа

        Returns:
            List[Dict]: отсортированный список кандидатов
        """
        # Получаем кандидатов
        candidates = self.get_candidates(limit)

        if not candidates:
            print("❌ Нет кандидатов в базе данных")
            return []

        print(f"\n🔍 Анализируем {len(candidates)} кандидатов...")

        # Создаем промпт для LLM
        prompt = self._create_sorting_prompt(candidates, criteria)

        # Получаем ответ от LLM
        try:
            response = self.llm.invoke(prompt)
            sorted_candidates = self._parse_response(response.content, candidates)
            print(f"✅ Сортировка завершена")
            return sorted_candidates
        except Exception as e:
            print(f"❌ Ошибка при сортировке: {e}")
            return []

    def _create_sorting_prompt(self, candidates: List[Dict], criteria: Dict) -> str:
        """Создать промпт для сортировки"""

        # Форматируем критерии
        criteria_text = ""
        for key, value in criteria.items():
            if isinstance(value, list):
                value = ", ".join(value)
            criteria_text += f"- {key}: {value}\n"

        # Форматируем кандидатов
        candidates_text = ""
        for i, cand in enumerate(candidates, 1):
            # Форматируем навыки
            skills = cand.get('skills', [])
            if isinstance(skills, str):
                skills = skills.split(',') if skills else []
            skills_str = ", ".join(str(s) for s in skills[:5])

            # Форматируем языки
            languages = cand.get('languages', [])
            if isinstance(languages, str):
                languages = languages.split(',') if languages else []
            languages_str = ", ".join(str(l) for l in languages[:3])

            candidates_text += f"""
Кандидат #{i}:
ID: {cand.get('id', 'N/A')}
Имя: {cand.get('name', cand.get('candidate_name', 'Неизвестно'))}
Должность: {cand.get('position', cand.get('job_title', 'Не указана'))}
Опыт: {cand.get('experience_years', cand.get('experience', 0))} лет
Навыки: {skills_str}
Образование: {cand.get('education', 'Не указано')}
Языки: {languages_str}
Ожидаемая зарплата: {cand.get('expected_salary', 'Не указана')}
О кандидате: {cand.get('about', cand.get('description', ''))[:200]}
---
"""

        prompt = f"""
Ты HR-эксперт с многолетним опытом. Твоя задача - отсортировать кандидатов по их соответствию заданным критериям.

КРИТЕРИИ ОТБОРА (важность в порядке перечисления):
{criteria_text}

КАНДИДАТЫ ДЛЯ АНАЛИЗА:
{candidates_text}

ИНСТРУКЦИИ:
1. Внимательно проанализируй каждого кандидата
2. Оцени, насколько каждый кандидат соответствует каждому критерию
3. Поставь общую оценку соответствия от 0 до 100
4. Отсортируй кандидатов от наиболее подходящего к наименее подходящему

ТВОЙ ОТВЕТ ДОЛЖЕН БЫТЬ ТОЛЬКО В ФОРМАТЕ JSON:

{{
    "ranked_candidates": [
        {{
            "candidate_id": 1,
            "name": "Имя кандидата",
            "match_score": 95,
            "explanation": "Краткое объяснение, почему кандидат получил такую оценку",
            "strengths": ["сильная сторона 1", "сильная сторона 2"],
            "weaknesses": ["слабая сторона 1", "слабая сторона 2"]
        }}
    ],
    "summary": "Общий вывод о найденных кандидатах (2-3 предложения)"
}}

НЕ ДОБАВЛЯЙ НИКАКОГО ДРУГОГО ТЕКСТА, ТОЛЬКО JSON.
"""

        return prompt

    def _parse_response(self, response: str, original_candidates: List[Dict]) -> List[Dict]:
        """Распарсить ответ от LLM"""
        try:
            # Очищаем ответ от markdown
            response_text = response.strip()

            # Убираем ```json если есть
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1]

            # Убираем возможный текст до и после JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                response_text = response_text[start_idx:end_idx]

            # Парсим JSON
            result = json.loads(response_text)

            # Создаем отсортированный список
            ranked = []
            for ranked_cand in result.get('ranked_candidates', []):
                # Находим оригинального кандидата по ID
                cand_id = ranked_cand.get('candidate_id', 1)
                if 1 <= cand_id <= len(original_candidates):
                    candidate = original_candidates[cand_id - 1].copy()
                    candidate['match_score'] = ranked_cand.get('match_score', 0)
                    candidate['match_explanation'] = ranked_cand.get('explanation', '')
                    candidate['strengths'] = ranked_cand.get('strengths', [])
                    candidate['weaknesses'] = ranked_cand.get('weaknesses', [])
                    ranked.append(candidate)

            # Сортируем по убыванию match_score
            ranked.sort(key=lambda x: x.get('match_score', 0), reverse=True)

            return ranked

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            print("Ответ LLM:", response[:500])
            return []
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return []

    def filter_by_skills(self, required_skills: List[str], min_match: int = 1) -> List[Dict]:
        """
        Быстрая фильтрация по навыкам (без использования LLM)

        Args:
            required_skills: список требуемых навыков
            min_match: минимальное количество совпадений

        Returns:
            List[Dict]: отфильтрованные кандидаты
        """
        candidates = self.get_candidates()
        matched = []

        # Приводим навыки к нижнему регистру для сравнения
        required_skills_lower = [s.lower() for s in required_skills]

        for cand in candidates:
            # Получаем навыки кандидата
            cand_skills = cand.get('skills', [])
            if isinstance(cand_skills, str):
                cand_skills = [s.strip().lower() for s in cand_skills.split(',')]
            elif isinstance(cand_skills, list):
                cand_skills = [str(s).lower() for s in cand_skills]
            else:
                cand_skills = []

            # Считаем совпадения
            matches = sum(1 for skill in required_skills_lower if skill in cand_skills)

            if matches >= min_match:
                cand['matched_skills'] = matches
                cand['match_percent'] = (matches / len(required_skills)) * 100
                matched.append(cand)

        # Сортируем по количеству совпадений
        matched.sort(key=lambda x: x['matched_skills'], reverse=True)

        return matched

    def export_to_excel(self, candidates: List[Dict], filename: str = "sorted_candidates.xlsx"):
        """
        Экспорт результатов в Excel

        Args:
            candidates: список кандидатов
            filename: имя файла для сохранения
        """
        if not candidates:
            print("❌ Нет данных для экспорта")
            return

        # Подготавливаем данные для DataFrame
        data = []
        for cand in candidates:
            # Получаем навыки
            skills = cand.get('skills', [])
            if isinstance(skills, list):
                skills_str = ", ".join(str(s) for s in skills[:5])
            else:
                skills_str = str(skills)[:100]

            row = {
                'ID': cand.get('id', ''),
                'Имя': cand.get('name', cand.get('candidate_name', 'Неизвестно')),
                'Должность': cand.get('position', cand.get('job_title', 'Не указана')),
                'Опыт (лет)': cand.get('experience_years', cand.get('experience', 0)),
                'Соответствие %': cand.get('match_score', cand.get('match_percent', 0)),
                'Навыки': skills_str,
                'Образование': cand.get('education', ''),
                'Ожидания': cand.get('expected_salary', ''),
                'Комментарий': cand.get('match_explanation', '')[:200]
            }

            # Добавляем рекомендацию на основе процента
            score = row['Соответствие %']
            if isinstance(score, (int, float)):
                if score >= 80:
                    row['Рекомендация'] = '🔥 Топ кандидат'
                elif score >= 60:
                    row['Рекомендация'] = '✅ Подходит'
                elif score >= 40:
                    row['Рекомендация'] = '⚠️ Возможно'
                else:
                    row['Рекомендация'] = '❌ Не подходит'
            else:
                row['Рекомендация'] = '❓ Не определено'

            data.append(row)

        # Создаем DataFrame и сохраняем
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

        print(f"✅ Результаты сохранены в {filename}")
        print(f"📊 Всего записей: {len(df)}")

    def get_table_info(self) -> Dict:
        """Получить информацию о структуре таблицы"""
        self.cursor.execute(f"PRAGMA table_info({self.table_name})")
        columns = self.cursor.fetchall()

        return {
            'table_name': self.table_name,
            'columns': [col[1] for col in columns],
            'column_types': {col[1]: col[2] for col in columns}
        }

    def close(self):
        """Закрыть соединение с БД"""
        self.conn.close()
        print("✅ Соединение с БД закрыто")


# Пример использования (для тестирования)
if __name__ == "__main__":
    # Этот код выполнится только если файл запущен напрямую
    print("=" * 60)
    print("МОДУЛЬ ResumeSorter")
    print("=" * 60)
    print("\nКласс для сортировки резюме с использованием LLM")
    print("\nИспользование:")
    print("  from resume_sorter import ResumeSorter")
    print("  sorter = ResumeSorter('path/to/database.db')")
    print("  results = sorter.sort_by_criteria(criteria)")
    print("=" * 60)