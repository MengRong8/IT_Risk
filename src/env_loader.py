from __future__ import annotations

import os
import shlex
from pathlib import Path


def load_dotenv_exports(path: Path = Path(".env")) -> list[str]:
    """Load simple KEY=value or export KEY=value lines from a local .env file."""
    if not path.exists():
        return []

    loaded: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = shlex.split(raw_value, comments=False, posix=True)
        os.environ[key] = value[0] if value else ""
        loaded.append(key)
    return loaded
