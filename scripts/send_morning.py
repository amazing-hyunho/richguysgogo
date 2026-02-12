from __future__ import annotations

# Morning sender for latest report markdown.

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.adapters.telegram_sender import send_report


def main() -> None:
    """Send the latest report.md via Telegram or console."""
    runs_dir = ROOT_DIR / "runs"
    latest_dir = _latest_run_dir(runs_dir)
    if latest_dir is None:
        print("No runs found.")
        return

    report_path = latest_dir / "report.md"
    if not report_path.exists():
        print("report.md not found.")
        return

    text = report_path.read_text(encoding="utf-8")
    send_report(text)


def _latest_run_dir(runs_dir: Path) -> Path | None:
    """Return the latest run directory by name."""
    if not runs_dir.exists():
        return None
    dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda path: path.name)[-1]


if __name__ == "__main__":
    main()
