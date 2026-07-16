from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


class EditorNotFoundError(Exception):
    pass


def open_in_editor(path: Path, editor: str) -> None:
    if shutil.which(editor) is None:
        raise EditorNotFoundError(
            f"Editor '{editor}' was not found in PATH. "
            f"Set a different one with: portal editor <command>"
        )
    is_windows = sys.platform == "win32"
    subprocess.Popen([editor, str(path)], close_fds=not is_windows, shell=is_windows)
