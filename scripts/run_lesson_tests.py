#!/usr/bin/env python3
"""
Run tests for lessons changed in a PR.

Usage:
  python scripts/run_lesson_tests.py <base_sha> <head_sha>

In GitHub Actions we'll pass:
  ${{ github.event.pull_request.base.sha }} ${{ github.event.pull_request.head.sha }}
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
import sys
from pathlib import Path

def get_changed_lessons(base, head):
    # git diff base..head --name-only
    res = subprocess.run(["git", "diff", "--name-only", f"{base}..{head}"], capture_output=True, text=True)
    if res.returncode != 0:
        print("git diff failed:", res.stderr)
        return set()
    files = [l.strip() for l in res.stdout.splitlines() if l.strip()]
    lessons = set()
    for f in files:
        parts = Path(f).parts
        # look for 'lessons/<lesson-name>/...'
        if len(parts) >= 2 and parts[0] == "lessons":
            lessons.add(parts[1])
    return lessons

def main():
    if len(sys.argv) != 3:
        print("Usage: run_lesson_tests.py <base_sha> <head_sha>")
        sys.exit(1)

    base_sha = sys.argv[1]
    head_sha = sys.argv[2]

    lessons = get_changed_lessons(base_sha, head_sha)
    if not lessons:
        print("No changed lessons found between shas — nothing to test.")
        sys.exit(0)

    print("Changed lessons:", lessons)
    exit_code = 0
    for lesson in lessons:
        test_dir = Path("tests") / lesson
        if test_dir.exists():
            print(f"Running pytest for {lesson} ...")
            res = subprocess.run(["pytest", "-q", str(test_dir)], check=False)
            if res.returncode != 0:
                print(f"Tests failed for {lesson}")
                exit_code = res.returncode
        else:
            print(f"No tests directory for {lesson}, skipping")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
