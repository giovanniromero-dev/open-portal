# dockportal

Manage your favorite projects from the terminal.

## Install

```
pipx install git+https://github.com/giovannidevelopments/dockportal.git
```

## Usage

```
portal                 # interactive TUI (arrows to move, enter to open)
portal list
portal open <name>
portal add <path>
portal remove <name>
portal favorite <name>
portal search <query>
portal recent
portal scan <directory>
portal info <name>
portal editor <command> # set default editor (code, cursor, zed, ...)
```

### TUI shortcuts

| Key | Action |
| --- | --- |
| Enter | Open selected project |
| a | Add a project |
| d | Delete selected project |
| f | Toggle favorite |
| / | Search / filter |
| r | Reset filter |
| q | Quit |

## Development

```
python -m venv .venv
.venv/Scripts/activate       # .venv/bin/activate on Linux/Mac
pip install -e ".[dev]"
pytest
```

Config is stored at `~/.dockportal/config.json`.
