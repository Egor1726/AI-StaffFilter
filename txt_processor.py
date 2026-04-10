# txt_processor.py
import re
import json
from pathlib import Path
import hashlib
from datetime import datetime


# ============ КЭШИРОВАНИЕ ============

def get_file_hash(file_path: str) -> str:
    """
    Вычисляет хеш файла (MD5).
    Если содержимое файла изменилось — хеш будет другим.
    """
    content = Path(file_path).read_bytes()
    return hashlib.md5(content).hexdigest()


def get_cache_path(resumes_path: str) -> Path:
    """
    Возвращает путь к файлу кэша на основе пути к исходному файлу.
    Например: data/resumes.txt → data/.cache_resumes.json
    """
    input_file = Path(resumes_path)
    cache_file = input_file.parent / f".cache_{input_file.stem}.json"
    return cache_file


def load_from_cache(resumes_path: str) -> list[dict] | None:
    """
    Загружает распаршенные резюме из кэша, если кэш актуален.
    Возвращает None, если кэша нет или файл изменился.
    """
    cache_path = get_cache_path(resumes_path)
    
    # Проверяем, существует ли файл кэша
    if not cache_path.exists():
        print("[txt_processor] Кэш не найден, будет выполнен парсинг")
        return None
    
    # Загружаем метаданные кэша
    with open(cache_path, 'r', encoding='utf-8') as f:
        cached_data = json.load(f)
    
    # Проверяем, изменился ли исходный файл
    current_hash = get_file_hash(resumes_path)
    if cached_data.get("source_hash") != current_hash:
        print("[txt_processor] Файл изменился, кэш устарел, будет выполнен парсинг")
        return None
    
    # Проверяем время создания кэша (опционально, можно убрать)
    cache_time = cached_data.get("cache_time", "неизвестно")
    print(f"[txt_processor] Кэш актуален (создан: {cache_time})")
    
    # Возвращаем сохранённые резюме
    return cached_data.get("resumes", [])


def save_to_cache(resumes_path: str, resumes: list[dict]) -> None:
    """
    Сохраняет распаршенные резюме в кэш.
    """
    cache_path = get_cache_path(resumes_path)
    
    # Получаем текущую дату и время
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Подготавливаем данные для сохранения
    cache_data = {
        "source_path": str(Path(resumes_path).absolute()),
        "source_hash": get_file_hash(resumes_path),
        "cache_time": current_time,
        "resumes": resumes,
        "resumes_count": len(resumes)
    }
    
    # Сохраняем в JSON
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    print(f"[txt_processor] Результаты сохранены в кэш: {cache_path}")
    print(f"[txt_processor]   Резюме: {len(resumes)} шт.")


#Удаляет мусор из текста перед парсингом
def clean_text_block(text: str) -> str:
    # Удаляем лишние пробелы и переносы
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Удаляем невидимые символы
    text = text.replace('\ufeff', '').replace('\r', '')
    
    # Нормализуем кавычки
    text = text.replace('«', '"').replace('»', '"')
    text = text.replace('—', '-').replace('–', '-')
    
    return text.strip()


#Сохранение результатов в JSON (для отладки)
def save_resumes_json(resumes: list[dict], output_path: str = "data/parsed_resumes.json"):
    """Сохраняет распаршенные резюме в JSON для отладки"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resumes, f, ensure_ascii=False, indent=2)
    print(f"[txt_processor] Сохранено в {output_path}")


#Добавила проверку на дубликаты, чтобы дважды не выводить одного кандитдата
#    seen_hashes = set() — создаётся пустое множество для хранения хешей
def get_text_hash(text: str) -> str:
    """
    Создает MD5-хеш текста для сравнения резюме.
    Одинаковые резюме дают одинаковый хеш.
    """
    # Очищаем текст от лишних пробелов перед хешированием
    normalized = ' '.join(text.split())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


# ── Парсинг одного резюме ─────────────────────────────────────────────────────
# Добавила небольшую чистку текста(удаление ненужного, счто будет мешать приводить метаданные потом в добром хорошем виде) +
# добавиоа блок с языками
def parse_resume_fields(text: str) -> dict:
    text = clean_text_block(text) 
    
    """
    Извлекает поля из текстового блока одного резюме.
    Возвращает словарь с полями кандидата.
    """
    fields = {
        "name": "Неизвестно",
        "email": "",
        "phone": "",
        "position": "",
        "experience_years": 0,
        "skills": [],
        "education": "",
        "languages": [],
        "expected_salary": "",
        "about": text[:500]
    }

    # Имя — первая строка блока
    first_line = text.strip().split('\n')[0].strip()
    if first_line:
        fields["name"] = first_line

    # Email
    m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    if m:
        fields["email"] = m.group(0)

    # Телефон
    m = re.search(r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', text)
    if m:
        fields["phone"] = m.group(0)

    # Должность
    m = re.search(r'(?:Позиция|Должность|Position):\s*(.+)', text, re.IGNORECASE)
    if m:
        fields["position"] = m.group(1).strip()

    # Опыт в годах
    m = re.search(r'(\d+)\s*(?:лет|год|года)\s*опыт', text, re.IGNORECASE)
    if m:
        fields["experience_years"] = int(m.group(1))

    # Навыки
    m = re.search(r'(?:Навыки|Skills):\s*(.+)', text, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()
        fields["skills"] = [s.strip() for s in raw.split(',') if s.strip()]

    # Образование
    m = re.search(r'(?:Образование|Education):\s*(.+)', text, re.IGNORECASE)
    if m:
        fields["education"] = m.group(1).strip()

    # Языки
    m = re.search(r'(?:Языки|Languages):\s*(.+)', text, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()
        fields["languages"] = [lang.strip() for lang in raw.split(',') if lang.strip()]

    # Зарплата
    m = re.search(r'(?:Зарплата|Salary|Ожидания):\s*(.+)', text, re.IGNORECASE)
    if m:
        fields["expected_salary"] = m.group(1).strip()

    # О себе — текст после "О себе:"
    m = re.search(r'(?:О себе|About):\s*(.+?)(?=\n[А-ЯA-Z]|\Z)', text, re.IGNORECASE | re.DOTALL)
    if m:
        fields["about"] = m.group(1).strip()[:500]

    return fields


# ── Чтение файлов ─────────────────────────────────────────────────────────────
#seen_hashes = set() — создаётся пустое множество для хранения хешей
#get_text_hash(block) — из текста резюме создаётся уникальный отпечаток 
#if block_hash in seen_hashes — проверяем, встречался ли уже такой хеш
#continue — если хеш уже есть, пропускаем это резюме
#seen_hashes.add(block_hash) — если хеш новый, запоминаем его
def load_resumes(resumes_path: str, use_cache: bool = True) -> list[dict]:
    """
    Читает resumes.txt и разбивает по разделителю ---.
    Возвращает список словарей с полями каждого резюме.
    Дубликаты отсеиваются автоматически.
    
    Параметры:
        resumes_path: путь к файлу с резюме
        use_cache: если True, использует кэш при возможности
    """
    
    # ===== ПРОВЕРКА КЭША =====
    if use_cache:
        cached = load_from_cache(resumes_path)
        if cached is not None:
            return cached
    # ===== КОНЕЦ ПРОВЕРКИ =====
    
    # ===== ОСНОВНАЯ РАБОТА (парсинг) =====
    print("[txt_processor] Выполняется парсинг резюме...")
    
    text = Path(resumes_path).read_text(encoding="utf-8")
    
    # Если есть разделитель ---
    if '---' in text:
        blocks = [b.strip() for b in text.split("---") if b.strip()]
    else:
        # Запасной вариант: каждая строка с "Резюме" или "Кандидат" — новое
        blocks = re.split(r'\n(?=Резюме|Кандидат|\d+\.)', text)

    resumes = []
    seen_hashes = set()  # Хранит хеши уже обработанных резюме
    duplicates_count = 0

    for block in blocks:
        # Создаём хеш текста резюме
        block_hash = get_text_hash(block)
        
        # Если такой хеш уже был — пропускаем (дубликат)
        if block_hash in seen_hashes:
            duplicates_count += 1
            continue
        
        # Запоминаем хеш
        seen_hashes.add(block_hash)
        
        # Парсим резюме
        fields = parse_resume_fields(block)
        resumes.append(fields)

    print(f"[txt_processor] Найдено резюме: {len(resumes) + duplicates_count}")
    print(f"[txt_processor] Из них уникальных: {len(resumes)}")
    if duplicates_count > 0:
        print(f"[txt_processor] Пропущено дубликатов: {duplicates_count}")
    
    # ===== СОХРАНЕНИЕ В КЭШ =====
    save_to_cache(resumes_path, resumes)
    
    return resumes


def load_vacancy(vacancy_path: str) -> str:
    """
    Читает vacancy.txt и возвращает текст как строку.
    Не парсим — передаём в LLM целиком.
    """
    text = Path(vacancy_path).read_text(encoding="utf-8").strip()
    print(f"[txt_processor] Вакансия загружена: {len(text)} символов")
    return text


# ── Подготовка для ChromaDB ───────────────────────────────────────────────────

def prepare_for_chroma(resumes: list[dict]) -> list[dict]:
    """
    Готовит резюме в формате который ожидает ChromaDB / indexer.py.

    Возвращает список словарей:
    {
        "id":       уникальный ID кандидата
        "text":     полный текст для векторизации (эмбеддинга)
        "metadata": поля для фильтрации и вывода результатов
    }

    Важно:
    - все значения в metadata должны быть строками (требование ChromaDB)
    - skills передаётся как строка через запятую, не список
    - experience_years приводится к строке
    """
    documents = []
    
    for i, r in enumerate(resumes):
        candidate_id = f"candidate_{i:04d}"  
        
        if not r.get("name") and not r.get("about"):
            continue
        
        # Полный текст для эмбеддинга — чем больше контекста тем лучше
        full_text = f"""
Имя: {r['name']}
Должность: {r['position']}
Опыт: {r['experience_years']} лет
Навыки: {', '.join(r['skills']) if isinstance(r['skills'], list) else r['skills']}
Образование: {r['education']}
Зарплата: {r['expected_salary']}
О себе: {r['about']}
        """.strip()

        # Метаданные — только строки, ChromaDB не принимает числа и списки
        metadata = {
            "candidate_id":    candidate_id,
            "name":            r["name"],
            "email":           r["email"],
            "phone":           r["phone"],
            "position":        r["position"],
            "experience_years": str(r["experience_years"]),
            "skills":          ", ".join(r["skills"]) if isinstance(r["skills"], list) else r["skills"],
            "education":       r["education"],
            "expected_salary": r["expected_salary"],
        }

        documents.append({
            "id":       candidate_id,
            "text":     full_text,
            "metadata": metadata,
        })

    print(f"[txt_processor] Подготовлено для ChromaDB: {len(documents)} документов")
    return documents


# ── Главная функция ───────────────────────────────────────────────────────────

def process_files(resumes_path: str, vacancy_path: str, use_cache: bool = True) -> tuple[list[dict], str]:
    """
    Главная функция модуля. Точка входа для всей системы.

    Вход:
        resumes_path — путь к файлу со всеми резюме (resumes.txt)
        vacancy_path — путь к файлу с требованиями (vacancy.txt)
        use_cache — использовать ли кэш для резюме (по умолчанию True)

    Выход:
        documents    — список готовых документов для ChromaDB (indexer.py)
        vacancy_text — текст вакансии для LLM агента (agent.py)

    Использование в indexer.py:
        from txt_processor import process_files
        documents, vacancy_text = process_files("data/resumes.txt", "data/vacancy.txt")
    """
    resumes = load_resumes(resumes_path, use_cache=use_cache)
    vacancy_text = load_vacancy(vacancy_path)
    documents = prepare_for_chroma(resumes)
    return documents, vacancy_text


# ── Быстрая проверка ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    documents, vacancy = process_files("data/resumes.txt", "data/vacancy.txt")

    print("\n── Первый документ ──────────────────────────────")
    print(f"ID:       {documents[0]['id']}")
    print(f"Имя:      {documents[0]['metadata']['name']}")
    print(f"Навыки:   {documents[0]['metadata']['skills']}")
    print(f"Опыт:     {documents[0]['metadata']['experience_years']} лет")
    print(f"\nТекст для эмбеддинга:\n{documents[0]['text']}")

    print("\n── Вакансия (первые 150 символов) ───────────────")
    print(vacancy[:150])

    print(f"\n── Итого: {len(documents)} кандидатов готовы для ChromaDB ──")