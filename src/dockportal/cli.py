from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import typer

from dockportal import config as cfg
from dockportal import detect
from dockportal.banner import BANNER
from dockportal.editor import EditorNotFoundError, open_in_editor

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

app = typer.Typer(help="dockportal - manage your favorite projects from the terminal")


def _time_ago(iso: str | None) -> str:
    if iso is None:
        return "never"
    then = datetime.fromisoformat(iso)
    delta = datetime.now(timezone.utc) - then
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def _describe(project: cfg.Project) -> str:
    star = "*" if project.favorite else " "
    bits = []
    if project.language:
        bits.append(project.language)
    if project.git_branch:
        bits.append(f"git:{project.git_branch}")
    extra = f" ({', '.join(bits)})" if bits else ""
    return f"[{star}] {project.name}{extra}"


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(BANNER)
        from dockportal.tui import run_tui

        run_tui()


@app.command()
def list():
    """List saved projects."""
    config = cfg.load()
    if not config.projects:
        typer.echo("No projects yet. Add one with: portal add <path>")
        return
    projects = cfg.sorted_projects(config)
    favorites = [p for p in projects if p.favorite]
    others = [p for p in projects if not p.favorite]
    if favorites:
        typer.echo("Favorites")
        for p in favorites:
            typer.echo(f"  {_describe(p)}")
    if others:
        if favorites:
            typer.echo("")
        typer.echo("Projects")
        for p in others:
            typer.echo(f"  {_describe(p)}")


@app.command()
def open(name: str):
    """Open a project in the configured editor."""
    config = cfg.load()
    project = cfg.find(config, name)
    if project is None:
        matches = cfg.search(config, name)
        if len(matches) == 1:
            project = matches[0]
        elif len(matches) > 1:
            typer.echo(f"Multiple matches for '{name}': {', '.join(p.name for p in matches)}")
            raise typer.Exit(code=1)
        else:
            typer.echo(f"No project named '{name}'. Try: portal add <path>")
            raise typer.Exit(code=1)
    editor = project.editor or config.default_editor
    try:
        open_in_editor(Path(project.path), editor)
    except EditorNotFoundError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)
    cfg.touch_last_opened(config, project.name)
    cfg.save(config)
    typer.echo(f"Opening '{project.name}' in {editor}...")


@app.command()
def add(path: str):
    """Add a new project."""
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists() or not resolved.is_dir():
        typer.echo(f"'{path}' is not a valid directory.")
        raise typer.Exit(code=1)
    config = cfg.load()
    project = cfg.Project(
        name=resolved.name,
        path=str(resolved),
        git_branch=detect.detect_git_branch(resolved),
        language=detect.detect_language(resolved),
    )
    cfg.add(config, project)
    cfg.save(config)
    bits = []
    if project.language:
        bits.append(f"language: {project.language}")
    if project.git_branch:
        bits.append(f"git: {project.git_branch}")
    extra = f" ({', '.join(bits)})" if bits else ""
    typer.echo(f"Added '{project.name}'{extra}")


@app.command()
def remove(name: str):
    """Remove a saved project."""
    config = cfg.load()
    if cfg.find(config, name) is None:
        typer.echo(f"No project named '{name}'.")
        raise typer.Exit(code=1)
    if not typer.confirm(f"Remove '{name}' from dockportal?"):
        raise typer.Exit(code=0)
    cfg.remove(config, name)
    cfg.save(config)
    typer.echo(f"Removed '{name}'.")


@app.command()
def favorite(name: str):
    """Toggle favorite status for a project."""
    config = cfg.load()
    project = cfg.toggle_favorite(config, name)
    if project is None:
        typer.echo(f"No project named '{name}'.")
        raise typer.Exit(code=1)
    cfg.save(config)
    state = "favorited" if project.favorite else "unfavorited"
    typer.echo(f"'{project.name}' {state}.")


@app.command()
def search(query: str):
    """Search projects by name."""
    config = cfg.load()
    matches = cfg.search(config, query)
    if not matches:
        typer.echo(f"No projects matching '{query}'.")
        return
    for p in matches:
        typer.echo(f"  {_describe(p)}")


@app.command()
def recent(limit: int = 10):
    """Show recently opened projects."""
    config = cfg.load()
    projects = cfg.recent(config, limit=limit)
    if not projects:
        typer.echo("No projects opened yet.")
        return
    for p in projects:
        typer.echo(f"  {p.name} - {_time_ago(p.last_opened)}")


@app.command()
def scan(directory: str):
    """Scan a directory for projects."""
    root = Path(directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        typer.echo(f"'{directory}' is not a valid directory.")
        raise typer.Exit(code=1)
    config = cfg.load()
    found = detect.find_projects(root)
    added, skipped = 0, 0
    for path in found:
        if cfg.find(config, path.name) is not None:
            skipped += 1
            continue
        project = cfg.Project(
            name=path.name,
            path=str(path),
            git_branch=detect.detect_git_branch(path),
            language=detect.detect_language(path),
        )
        cfg.add(config, project)
        added += 1
    cfg.save(config)
    typer.echo(f"Scan complete: {added} added, {skipped} already tracked.")


@app.command()
def info(name: str):
    """Show detailed info about a project."""
    config = cfg.load()
    project = cfg.find(config, name)
    if project is None:
        typer.echo(f"No project named '{name}'.")
        raise typer.Exit(code=1)
    typer.echo(f"Name:        {project.name}")
    typer.echo(f"Path:        {project.path}")
    typer.echo(f"Favorite:    {'yes' if project.favorite else 'no'}")
    typer.echo(f"Language:    {project.language or 'unknown'}")
    typer.echo(f"Git branch:  {project.git_branch or 'n/a'}")
    typer.echo(f"Last opened: {_time_ago(project.last_opened)}")
    typer.echo(f"Added:       {_time_ago(project.created)}")


@app.command()
def editor(command: str):
    """Set the default editor command (e.g. code, cursor, zed)."""
    config = cfg.load()
    config.default_editor = command
    cfg.save(config)
    typer.echo(f"Default editor set to '{command}'.")


if __name__ == "__main__":
    app()
