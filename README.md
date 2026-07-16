# dockportal

A terminal-based project switcher. Keep your favorite projects one command away — jump straight to them, open them in your editor, and let dockportal auto-detect their Git branch and language.

```
    ____  ____  ________ __ ____  ____  ____  _________    __
   / __ \/ __ \/ ____/ //_// __ \/ __ \/ __ \/_  __/   |  / /
  / / / / / / / /   / ,<  / /_/ / / / / /_/ / / / / /| | / /
 / /_/ / /_/ / /___/ /| |/ ____/ /_/ / _, _/ / / / ___ |/ /___
/_____/\____/\____/_/ |_/_/    \____/_/ |_| /_/ /_/  |_/_____/
```

## Features

- **Instant switching** — `portal open <name>` opens any tracked project in your configured editor
- **Interactive TUI** — run bare `portal` for an arrow-key browser with search, add, delete and favorite shortcuts
- **Auto-detection** — Git branch and primary language are detected automatically when you add a project
- **Directory scanning** — `portal scan <dir>` walks a folder and picks up every project it finds
- **Favorites & recents** — pin the projects you use most, or jump back into whatever you opened last
- **Cross-platform** — pure Python, works the same on Windows and Linux

## Install

```
pipx install git+https://github.com/giovannidevelopments/dockportal.git
```

`pip install git+...` or `uv tool install git+...` work the same way. Requires Python 3.9+ and Git.

## Usage

```
portal                    # interactive TUI (arrows to move, enter to open)
portal list                # list saved projects
portal open <name>         # open a project in your editor
portal add <path>          # track a new project
portal remove <name>       # stop tracking a project
portal favorite <name>     # toggle favorite status
portal search <query>      # search projects by name
portal recent              # show recently opened projects
portal scan <directory>    # find and add every project under a directory
portal info <name>         # show details for a project
portal editor <command>    # set the default editor (code, cursor, zed, ...)
```

### TUI shortcuts

| Key   | Action                  |
| ----- | ----------------------- |
| Enter | Open selected project   |
| a     | Add a project           |
| d     | Delete selected project |
| f     | Toggle favorite         |
| /     | Search / filter         |
| r     | Reset filter            |
| q     | Quit                    |

## Configuration

Projects are stored in `~/.dockportal/config.json`. A project is recognized by common markers: `.git`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, `composer.json`, `pyproject.toml`, `requirements.txt`.

## Development

```
python -m venv .venv
.venv/Scripts/activate       # .venv/bin/activate on Linux/Mac
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
