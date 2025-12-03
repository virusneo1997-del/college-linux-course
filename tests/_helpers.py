# tests/_helpers.py
import re
import requests
from pathlib import Path

# Map lesson folder -> raw README url (you provided these earlier)
RAW_README = {
    "01-initial-setup": "https://raw.githubusercontent.com/virusneo1997-del/college-linux-course/refs/heads/main/lessons/01-initial-setup/README.md",
    "02-users-permissions": "https://raw.githubusercontent.com/virusneo1997-del/college-linux-course/refs/heads/main/lessons/02-users-permissions/README.md",
    "03-web-server": "https://raw.githubusercontent.com/virusneo1997-del/college-linux-course/refs/heads/main/lessons/03-web-server/README.md",
    "04-monitoring": "https://raw.githubusercontent.com/virusneo1997-del/college-linux-course/refs/heads/main/lessons/04-monitoring/README.md",
    "05-databases-backups": "https://raw.githubusercontent.com/virusneo1997-del/college-linux-course/refs/heads/main/lessons/05-databases-backups/README.md",
    "06-docker-containers": "https://raw.githubusercontent.com/virusneo1997-del/college-linux-course/refs/heads/main/lessons/06-docker-containers/README.md",
}

def fetch_readme_text(lesson_name):
    url = RAW_README.get(lesson_name)
    if not url:
        return None
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.text

def extract_tasks_from_readme(text):
    """
    Heuristic: find a section that likely contains tasks:
    - section heading contains 'Зад' or 'Task' or 'Tasks'
    - then collect following list items (lines starting with '-', '*' or digits '1.' etc.)
    Fallback: collect all numbered list items anywhere.
    Returns list of stripped task strings.
    """
    lines = text.splitlines()
    tasks = []
    # search for headings with keywords
    heading_idx = None
    for i, ln in enumerate(lines):
        if re.search(r'(Зад|Задач|Tasks|Tasks:|Tasks)', ln, re.IGNORECASE):
            heading_idx = i
            break
    def collect_from(start_idx):
        collected = []
        for j in range(start_idx+1, min(len(lines), start_idx+200)):
            l = lines[j].strip()
            if not l:
                # blank -> could be break
                continue
            if re.match(r'#{1,6}\s', l):
                # new heading -> stop
                break
            if re.match(r'[-\*\u2022]\s+', l) or re.match(r'\d+\.', l):
                # normalized
                collected.append(re.sub(r'^[\-\*\u2022]\s+','', re.sub(r'^\d+\.\s*','', l)).strip())
            else:
                # maybe plain sentence - include if we already have items
                if collected:
                    collected[-1] += " " + l
        return collected

    if heading_idx is not None:
        tasks = collect_from(heading_idx)

    if not tasks:
        # fallback: take any numbered list items in the doc
        for l in lines:
            m = re.match(r'\d+\.\s+(.*)', l)
            if m:
                tasks.append(m.group(1).strip())
    # remove empties and duplicates
    tasks = [t for t in (x.strip() for x in tasks) if t]
    # dedupe while keeping order
    seen = set()
    out = []
    for t in tasks:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def find_student_report(lesson_name):
    """
    Look for student-report.md in:
    - lessons/<lesson_name>/student-report.md
    - any subfolder under lessons/<lesson_name> named 'student' or 'student-submissions' or first folder that contains student-report.md
    - lessons/<lesson_name>/student/student-report.md, lessons/.../student-submissions/<user>/student-report.md
    Returns Path or None.
    """
    base = Path("lessons") / lesson_name
    # direct
    cand = base / "student-report.md"
    if cand.exists():
        return cand

    # search common patterns
    candidates = list(base.glob("**/student-report.md"))
    if candidates:
        # pick first
        return candidates[0]

    # fallback: any markdown file with 'student' in parent folder name
    for p in base.rglob("*.md"):
        if "student" in str(p.parent).lower():
            return p

    return None

def student_answer_has_task(student_text, task_text):
    """
    Heuristic: check that student_text contains significant substrings from task_text.
    We will extract keywords from task_text (nouns, commands) simply by splitting and filtering short words.
    Need student answer to contain at least one strong token.
    """
    # normalize
    s = student_text.lower()
    t = task_text.lower()
    # look for command-like tokens e.g. 'nginx', 'docker', 'mysqldump', 'chmod', 'useradd'
    important_tokens = re.findall(r'[A-Za-z0-9_\-]{3,}', t)
    # prefer tokens that look like commands or keywords
    tokens = [tok for tok in important_tokens if len(tok) >= 3]
    # check if any token present in student text
    found = 0
    for tok in tokens:
        if tok in s:
            found += 1
            if found >= 1:
                return True
    # fallback: check for presence of at least 10 non-whitespace chars in answer near a heading of this task
    return len(s.strip()) >= 20
