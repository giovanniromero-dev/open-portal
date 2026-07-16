from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView

from dockportal import config as cfg
from dockportal import detect
from dockportal.editor import EditorNotFoundError, open_in_editor


class InputScreen(ModalScreen[str | None]):
    DEFAULT_CSS = """
    InputScreen {
        align: center middle;
    }
    #dialog {
        width: 60;
        padding: 1 2;
        background: $panel;
        border: thick $primary;
    }
    """

    def __init__(self, prompt: str, placeholder: str = "") -> None:
        super().__init__()
        self.prompt = prompt
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.prompt)
            yield Input(placeholder=self.placeholder)

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


class ConfirmScreen(ModalScreen[bool]):
    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }
    #dialog {
        width: 60;
        padding: 1 2;
        background: $panel;
        border: thick $error;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.message)
            yield Label("[y] yes    [n/esc] no")

    def on_key(self, event) -> None:
        if event.key == "y":
            self.dismiss(True)
        elif event.key in ("n", "escape"):
            self.dismiss(False)


class ProjectListItem(ListItem):
    def __init__(self, project: cfg.Project) -> None:
        marker = "*" if project.favorite else " "
        bits = []
        if project.language:
            bits.append(project.language)
        if project.git_branch:
            bits.append(f"git:{project.git_branch}")
        extra = f"  ({', '.join(bits)})" if bits else ""
        super().__init__(Label(f"[{marker}] {project.name}{extra}"))
        self.project = project


class DockPortalApp(App[None]):
    TITLE = "DockPortal"

    CSS = """
    ListView {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("a", "add_project", "Add"),
        Binding("d", "delete_project", "Delete"),
        Binding("f", "toggle_favorite", "Favorite"),
        Binding("slash", "search", "Search"),
        Binding("r", "clear_search", "Reset filter"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config = cfg.load()
        self.filter_text = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(id="project-list")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        list_view = self.query_one("#project-list", ListView)
        list_view.clear()
        projects = cfg.sorted_projects(self.config)
        if self.filter_text:
            q = self.filter_text.lower()
            projects = [p for p in projects if q in p.name.lower()]
        for project in projects:
            list_view.append(ProjectListItem(project))
        self.sub_title = (
            f"filter: {self.filter_text}" if self.filter_text else f"{len(projects)} project(s)"
        )

    def _highlighted_project(self) -> cfg.Project | None:
        list_view = self.query_one("#project-list", ListView)
        item = list_view.highlighted_child
        if item is None or not isinstance(item, ProjectListItem):
            return None
        return item.project

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not isinstance(item, ProjectListItem):
            return
        project = item.project
        editor = project.editor or self.config.default_editor
        try:
            open_in_editor(Path(project.path), editor)
        except EditorNotFoundError as exc:
            self.notify(str(exc), severity="error")
            return
        cfg.touch_last_opened(self.config, project.name)
        cfg.save(self.config)
        self.exit()

    def action_add_project(self) -> None:
        def handle(value: str | None) -> None:
            if not value:
                return
            path = Path(value).expanduser().resolve()
            if not path.exists() or not path.is_dir():
                self.notify(f"'{value}' is not a valid directory", severity="error")
                return
            project = cfg.Project(
                name=path.name,
                path=str(path),
                git_branch=detect.detect_git_branch(path),
                language=detect.detect_language(path),
            )
            cfg.add(self.config, project)
            cfg.save(self.config)
            self.refresh_list()
            self.notify(f"Added '{project.name}'")

        self.push_screen(InputScreen("Path to add:", placeholder="~/Projects/my-app"), handle)

    def action_delete_project(self) -> None:
        project = self._highlighted_project()
        if project is None:
            self.notify("No project selected", severity="warning")
            return

        def handle(confirmed: bool | None) -> None:
            if not confirmed:
                return
            cfg.remove(self.config, project.name)
            cfg.save(self.config)
            self.refresh_list()
            self.notify(f"Removed '{project.name}'")

        self.push_screen(ConfirmScreen(f"Remove '{project.name}'?"), handle)

    def action_toggle_favorite(self) -> None:
        project = self._highlighted_project()
        if project is None:
            self.notify("No project selected", severity="warning")
            return
        cfg.toggle_favorite(self.config, project.name)
        cfg.save(self.config)
        self.refresh_list()

    def action_search(self) -> None:
        def handle(value: str | None) -> None:
            self.filter_text = value or ""
            self.refresh_list()

        self.push_screen(InputScreen("Search:", placeholder=self.filter_text), handle)

    def action_clear_search(self) -> None:
        self.filter_text = ""
        self.refresh_list()


def run_tui() -> None:
    DockPortalApp().run()
