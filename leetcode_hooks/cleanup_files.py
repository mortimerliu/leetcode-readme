from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import check_output
from typing import Any
from typing import Callable
from typing import Optional

DROPBOX = Path.home().joinpath("Dropbox/LeetCode/")
LEETCODE = Path.home().joinpath("src/leetcode/")
BACKUP = Path.home().joinpath("src/leetcode/backup/")
BACKUP.mkdir(parents=True, exist_ok=True)
LC_REGEX = re.compile(r"(\d+)\.?(.*)\.([a-z]+)$")


class Filter:
    def __init__(self, func: Callable[[Path], bool]):
        self.func = func

    def __call__(self, files: list[Path]) -> list[Path]:
        return [file for file in files if self.func(file)]

    def __and__(self, other: Filter) -> Filter:
        return Filter(lambda file: self.func(file) and self.func(file))

    def __or__(self, other: Filter) -> Filter:
        return Filter(lambda file: self.func(file) or self.func(file))

    def __invert__(self) -> Filter:
        return Filter(lambda file: not self.func(file))

    def __repr__(self) -> str:
        return f"Filter({self.func})"

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self) -> int:
        return hash(self.func)


def list_files(
    path: Path,
    filters: list[Filter] | None = None,
    sort_key: Callable[[Path], int] | None = None,
) -> list[Path]:
    all_files = [
        Path(dir).joinpath(file)
        for dir, _, files in os.walk(path)
        for file in files
    ]
    if filters:
        for filter in filters:
            all_files = filter(all_files)
    if sort_key:
        all_files = sorted(all_files, key=sort_key)
    return all_files


def get_question_id(file: Path) -> int:
    match = LC_REGEX.match(file.name)
    if match:
        return int(match.group(1))
    raise ValueError(f"Invalid filename: {file.name}")


def get_to_be_removed_files() -> list[Path]:
    lc_question_filter = Filter(
        lambda file: LC_REGEX.match(file.name) is not None,
    )
    repo_files = list_files(LEETCODE, filters=[lc_question_filter])
    repo_ids = [get_question_id(file) for file in repo_files]

    dropbox_files = list_files(DROPBOX, filters=[lc_question_filter])
    lc_repo_filter = Filter(lambda file: get_question_id(file) in repo_ids)

    return lc_repo_filter(dropbox_files)


def move_to_backup(files: list[Path]) -> None:
    for file in files:
        print(f"Moving {file.name} to backup...")
        try:
            check_output(["mv", str(file), str(BACKUP)])
        except CalledProcessError as e:
            print(e)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backup old md files")
    add = parser.add_argument
    add("filenames", nargs="*", help="Filenames to check.")
    add("-d", "--dry-run", action="store_true")
    add("-c", "--confirm", action="store_true")
    args = parser.parse_args(argv)

    to_be_removed_files = get_to_be_removed_files()
    to_be_removed_files.sort(key=get_question_id)
    if args.confirm or args.dry_run:
        print("Files to be backed up:")
        for file in to_be_removed_files:
            print("\t" + file.name)
    if args.confirm:
        confirm = input("Confirm? [y/N] ")
        if confirm.lower() != "y":
            return 3
    if not args.dry_run and to_be_removed_files:
        move_to_backup(to_be_removed_files)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
