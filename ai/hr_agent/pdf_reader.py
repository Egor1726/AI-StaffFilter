import os
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Извлекает текст из PDF-файла.
    Возвращает склеенный текст всех страниц или пустую строку при ошибке.
    """
    try:
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text.strip())
        return "\n\n".join(pages_text)
    except Exception as e:
        print(f"  [ERROR] Не удалось прочитать PDF {pdf_path}: {e}")
        return ""


def load_pdf_resumes(resumes_dir: str) -> list[tuple[str, str]]:
    """
    Загружает все PDF из указанной директории.
    Возвращает список кортежей (doc_id, raw_text).
    doc_id формируется из имени файла без расширения.
    """
    if not os.path.isdir(resumes_dir):
        print(f"  [ERROR] Директория не найдена: {resumes_dir}")
        return []

    results = []
    pdf_files = sorted(f for f in os.listdir(resumes_dir) if f.lower().endswith(".pdf"))

    if not pdf_files:
        print(f"  [WARN] PDF-файлы не найдены в: {resumes_dir}")
        return []

    print(f"  Найдено PDF-файлов: {len(pdf_files)}")
    for filename in pdf_files:
        path = os.path.join(resumes_dir, filename)
        doc_id = os.path.splitext(filename)[0]  # имя файла без расширения
        print(f"  -> Читаю: {filename}")
        text = extract_text_from_pdf(path)
        if text.strip():
            results.append((doc_id, text))
        else:
            print(f"     [SKIP] Пустой текст в файле: {filename}")

    return results