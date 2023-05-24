# leetcode-readme

A tool (and `pre-commit` hook) to automatically (re-)generate README.md 
for the [LeetCode](https://github.com/mortimerliu/LeetCode) here.

## Installation

```
pip install leetcode-readme
```

## As a `pre-commit` hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions.

Sample `.pre-commit-config.yaml`:

```
-   repo: https://github.com/mortimerliu/leetcode-readme
    rev: v0.0.1
    hooks:
    -   id: leetcode-readme
```

