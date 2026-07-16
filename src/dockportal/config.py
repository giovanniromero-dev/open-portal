from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

CONFIG_DIR = Path.home() / ".dockportal"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Project:
    name: str
    path: str
    favorite: bool = False
    git_branch: str | None = None
    language: str | None = None
    last_opened: str | None = None
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    editor: str | None = None


@dataclass
class Config:
    projects: list[Project] = field(default_factory=list)
    default_editor: str = "code"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load() -> Config:
    if not CONFIG_FILE.exists():
        return Config()
    data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    projects = [Project(**p) for p in data.get("projects", [])]
    return Config(projects=projects, default_editor=data.get("default_editor", "code"))


def save(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "projects": [asdict(p) for p in config.projects],
        "default_editor": config.default_editor,
    }
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def find(config: Config, name: str) -> Project | None:
    for p in config.projects:
        if p.name == name:
            return p
    return None


def add(config: Config, project: Project) -> None:
    existing = find(config, project.name)
    if existing is not None:
        config.projects.remove(existing)
    config.projects.append(project)


def remove(config: Config, name: str) -> bool:
    project = find(config, name)
    if project is None:
        return False
    config.projects.remove(project)
    return True


def toggle_favorite(config: Config, name: str) -> Project | None:
    project = find(config, name)
    if project is None:
        return None
    project.favorite = not project.favorite
    return project


def touch_last_opened(config: Config, name: str) -> None:
    project = find(config, name)
    if project is not None:
        project.last_opened = _now()


def search(config: Config, query: str) -> list[Project]:
    q = query.lower()
    return [p for p in config.projects if q in p.name.lower()]


def sorted_projects(config: Config) -> list[Project]:
    return sorted(config.projects, key=lambda p: (not p.favorite, p.name.lower()))


def recent(config: Config, limit: int = 10) -> list[Project]:
    opened = [p for p in config.projects if p.last_opened is not None]
    opened.sort(key=lambda p: p.last_opened, reverse=True)
    return opened[:limit]
