from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_MARKERS = [
    ".git",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "composer.json",
    "pyproject.toml",
    "requirements.txt",
]

_LANGUAGE_MARKERS = [
    ("tsconfig.json", "TypeScript"),
    ("package.json", "JavaScript"),
    ("Cargo.toml", "Rust"),
    ("go.mod", "Go"),
    ("pom.xml", "Java"),
    ("build.gradle", "Java"),
    ("composer.json", "PHP"),
    ("pyproject.toml", "Python"),
    ("requirements.txt", "Python"),
    ("Gemfile", "Ruby"),
]


def is_project_dir(path: Path) -> bool:
    return any((path / marker).exists() for marker in PROJECT_MARKERS)


def detect_language(path: Path) -> str | None:
    for marker, language in _LANGUAGE_MARKERS:
        if (path / marker).exists():
            return language
    return None


def detect_git_branch(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def find_projects(root: Path, max_depth: int = 3) -> list[Path]:
    found: list[Path] = []
    root = root.resolve()

    def _walk(directory: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if is_project_dir(directory):
            found.append(directory)
            return
        try:
            children = [c for c in directory.iterdir() if c.is_dir() and not c.name.startswith(".")]
        except PermissionError:
            return
        for child in children:
            _walk(child, depth + 1)

    try:
        top_children = [c for c in root.iterdir() if c.is_dir() and not c.name.startswith(".")]
    except PermissionError:
        return found
    for child in top_children:
        _walk(child, 1)
    return found
