from __future__ import annotations

from setuptools import setup

setup(
    name="leetcode-readme",
    version="0.0.1",
    description="Generate README.md for leetcode repo",
    long_description=(
        "A tool (and `pre-commit` hook) to automatically "
        "(re-)generate README.md for the [LeetCode] "
        "(https://github.com/mortimerliu/LeetCode) here."
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/mortimerliu/leetcode-readme",
    author="Hongru Liu",
    author_email="hl3148@columbia.edu",
    license="MIT",
    license_files=["LICENSE"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.7",
    py_modules=["leetcode_readme"],
    entry_points={
        "console_scripts": [
            "leetcode-readme=leetcode_readme:main",
        ],
    },
    keywords="pre-commit, leetcode",
)
