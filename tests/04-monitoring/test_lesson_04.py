# tests/04-monitoring/test_lesson_04.py
from pathlib import Path
from tests._helpers import fetch_readme_text, extract_tasks_from_readme, find_student_report, student_answer_has_task

def test_student_report_exists():
    rp = find_student_report("04-monitoring")
    assert rp is not None and rp.exists(), "Ожидается файл lessons/04-monitoring/student-report.md (или в подпапке student/)."

def test_answers_cover_readme_tasks():
    readme = fetch_readme_text("04-monitoring")
    tasks = extract_tasks_from_readme(readme)
    assert tasks, "Не удалось извлечь задания из README урока 04."

    rp = find_student_report("04-monitoring")
    student_text = rp.read_text(encoding="utf-8") if rp else ""
    missing = []
    for t in tasks:
        if not student_answer_has_task(student_text, t):
            missing.append(t)
    assert not missing, "Отсутствуют ответы на задачи из README урока 04: " + "; ".join(missing)
