from __future__ import annotations

from pathlib import Path
import os


def load_project_env(root_dir: Path) -> None:
    """Load simple KEY=VALUE pairs from project .env (best effort).

    Rules:
    - Ignores blank lines and comments.
    - Supports optional `export KEY=VALUE`.
    - Does not override already-set process env vars.
    """
    env_path = root_dir / ".env"
    if not env_path.exists():
        return

    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key:
                continue
            value = value.strip()
            if (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            os.environ.setdefault(key, value)
    except Exception:
        # Env file loading should never break pipeline execution.
        return
