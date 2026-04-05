# main.py
from txt_processor import process_files
from resume_sorter import ResumeSorter

db_path, vacancy_text = process_files(
    resumes_path="data/resumes.txt",
    vacancy_path="data/vacancy.txt"
)

sorter = ResumeSorter(db_path)
results = sorter.sort_by_criteria({"требования": vacancy_text})

for i, candidate in enumerate(results, 1):
    print(f"{i}. {candidate['name']} — {candidate.get('match_score', 0)}%")