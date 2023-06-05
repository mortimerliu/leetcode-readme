from __future__ import annotations

import argparse
import os
import re
from functools import lru_cache
from subprocess import CalledProcessError
from subprocess import check_output
from typing import Any
from typing import Iterator
from typing import Sequence

LEETCODE_URL: str = "https://leetcode.com/problems/{question}/description/"
GITHUB_URL: str = "https://github.com/mortimerliu/LeetCode/blob/main/algorithms/{lang}/{level}/{filename}"

README_TEMPLATE = """# Welcome to my LeetCode Solutions

This repo collects my solutions to LeetCode questions in Python. Will add solutions in Java gradually.

Will add new problems from weekly and biweekly contests once the contests are over.

## Algorithms

| # | Title | Solution | Difficulty |
|---| ----- | -------- | ---------- |
{table}

## Weekly & BiWeekly Contest

+ [Weekly 291](https://leetcode.com/contest/weekly-contest-291)
+ [Weekly 292](https://leetcode.com/contest/weekly-contest-292)
+ [Weekly 293](https://leetcode.com/contest/weekly-contest-293)
+ [Weekly 294](https://leetcode.com/contest/weekly-contest-294)
+ [Biweekly 79](https://leetcode.com/contest/biweekly-contest-79/)
+ [Weekly 295](https://leetcode.com/contest/weekly-contest-295)
+ [Weekly 302](https://leetcode.com/contest/weekly-contest-302)
+ [Weekly 303](https://leetcode.com/contest/weekly-contest-303)
"""

DirEntry = os.DirEntry[str]


class Question:
    def __init__(self, file: DirEntry, level: str | None = None):
        self.file = file
        self.filename = file.name
        self.id = _extract_question_id(file)
        self.name = _extract_question_name(file)
        self.lc_name = _name_to_lc_name(self.name)
        self.level = level or _extract_question_level(file)
        self.lang: list[str] = []
        self.leetcode_url = LEETCODE_URL.format(question=self.lc_name)

    def __hash__(self) -> int:
        return hash(self.id)


def list_dirs(dir: str | DirEntry) -> Iterator[DirEntry]:
    for entry in os.scandir(dir):
        if entry.is_dir():
            yield entry


def list_files(dir: str | DirEntry) -> Iterator[DirEntry]:
    for entry in os.scandir(dir):
        if entry.is_file():
            yield entry


def list_questions(target_dir: str) -> list[Question]:
    questions: dict[int, Question] = {}
    for lang in list_dirs(target_dir):
        for level in list_dirs(lang):
            for file in list_files(level):
                try:
                    question_id = _extract_question_id(file)
                    if question_id not in questions:
                        questions[question_id] = Question(file, level.name)
                    questions[question_id].lang.append(lang.name)
                except ValueError:
                    print(f"Skipping filename: {file.name}")
    return sorted(questions.values(), reverse=True, key=lambda q: q.id)


def _name_to_lc_name(name: str) -> str:
    return "-".join(
        [seg.lower() for seg in re.findall("[0-9A-Z]+[^A-Z]*", name)],
    )


def _extract_question_level(filepath: str | DirEntry) -> str:
    filepath = filepath.path if isinstance(filepath, os.DirEntry) else filepath
    match = re.search(
        r".+/(easy|medium|hard)/\d+\.[0-9a-zA-Z]+\.[a-z]+",
        filepath,
    )
    if match:
        return match.group(1)
    raise ValueError(f"Invalid filepath: {filepath}")


def _extract_question_id(filename: str | DirEntry) -> int:
    filename = filename.name if isinstance(filename, os.DirEntry) else filename
    match = re.search(r"(\d+)\..+", filename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Invalid filename: {filename}")


def _extract_question_name(filename: str | DirEntry) -> str:
    filename = filename.name if isinstance(filename, os.DirEntry) else filename
    match = re.search(r"\d+\.([0-9a-zA-Z]+)\..+", filename)
    if match:
        return match.group(1)
    raise ValueError(f"Invalid filename: {filename}")


def build_readme(questions: list[Question]) -> str:
    table = []
    for question in questions:
        row = f"| {question.id} | [{question.name}]({question.leetcode_url}) |"
        ans = []
        for lang in sorted(question.lang):
            lang_url = GITHUB_URL.format(
                lang=lang,
                level=question.level,
                filename=question.filename,
            )
            ans.append(f"[{lang}]({lang_url})")
        row += ", ".join(ans) + f" | {question.level} |\n"
        table.append(row)
    return README_TEMPLATE.format(table="".join(table))


def read_readme(readme: str) -> str:
    with open(readme) as f:
        lines = f.readlines()
    return "".join(lines)


def write_readme(content: str, readme: str) -> Any:
    with open(readme, "w") as f:
        f.write(content)


@lru_cache(maxsize=1)
def root() -> str:
    """returns the absolute path of the repository root"""
    try:
        base = check_output("git rev-parse --show-toplevel", shell=True)
    except CalledProcessError:
        raise OSError("Current working directory is not a git repository")
    return base.decode("utf-8").strip()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Update README.md")
    add = parser.add_argument
    add("filenames", nargs="*", help="Filenames to check.")
    _ = parser.parse_args(argv)

    target_dir = os.path.join(root(), "algorithms")
    readme_file = os.path.join(root(), "README.md")
    questions = list_questions(target_dir)
    content = build_readme(questions)
    if content == read_readme(readme_file):
        print("README.md is up-to-date")
        return 0
    write_readme(content, readme_file)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
