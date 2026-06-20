from __future__ import annotations

"""Update Thesis Monitor daily signals from existing DB data."""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.thesis_monitor import update_thesis_signals


DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update Thesis Monitor signals.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Signal date (YYYY-MM-DD).")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    changed = update_thesis_signals(str(args.date), db_path=DB_PATH)
    print(f"thesis_signals_updated date={args.date} changed={changed}")


if __name__ == "__main__":
    main()
