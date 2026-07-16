# open-portal

A terminal-based project switcher. Keep your favorite projects one command away — jump straight to them, open them in your editor, and let open-portal auto-detect their Git branch and language.

```
 ___________ _____ _   _  ______ ___________ _____ ___   _
|  _  | ___ \  ___| \ | | | ___ \  _  | ___ \_   _/ _ \ | |
| | | | |_/ / |__ |  \| | | |_/ / | | | |_/ / | |/ /_\ \| |
| | | |  __/|  __|| . ` | |  __/| | | |    /  | ||  _  || |
\ \_/ / |   | |___| |\  | | |   \ \_/ / |\ \  | || | | || |____
 \___/\_|   \____/\_| \_/ \_|    \___/\_| \_| \_/\_| |_/\_____/
```

## Features

- **Instant switching** — `open-portal <name>` opens any tracked project in your configured editor, no subcommand needed
- **Zero-friction adding** — `cd` into any project and run `open-portal add .` (or just `open-portal add`) to track it
- **Interactive TUI** — run bare `open-portal` for an arrow-key browser with search, add, delete and favorite shortcuts
- **Auto-detection** — Git branch and primary language are detected automatically when you add a project
- **Directory scanning** — `open-portal scan <dir>` walks a folder and picks up every project it finds
- **Favorites & recents** — pin the projects you use most, or jump back into whatever you opened last
- **Cross-platform** — pure Python, works the same on Windows and Linux

## Install

```
pipx install git+https://github.com/giovanniromero-dev/open-portal.git
```

`pip install git+...` or `uv tool install git+...` work the same way. Requires Python 3.9+ and Git.

## Usage

```
open-portal <name>           # shortcut: open a project directly
open-portal                  # interactive TUI (arrows to move, enter to open)
open-portal list              # list saved projects
open-portal open <name>       # open a project in your editor
open-portal add <path>        # track a new project (defaults to the current directory: open-portal add .)
open-portal remove <name>     # stop tracking a project
open-portal favorite <name>   # toggle favorite status
open-portal search <query>    # search projects by name
open-portal recent            # show recently opened projects
open-portal scan <directory>  # find and add every project under a directory
open-portal info <name>       # show details for a project
open-portal editor <command>  # set the default editor (code, cursor, zed, ...)
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

Projects are stored in `~/.open-portal/config.json`. A project is recognized by common markers: `.git`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, `composer.json`, `pyproject.toml`, `requirements.txt`.

## Development

```
python -m venv .venv
.venv/Scripts/activate       # .venv/bin/activate on Linux/Mac
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
