from __future__ import annotations

# One-time migration runner:
# Convert legacy 0.0 placeholders to NULL in SQLite DB.

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import get_db_path, safe_migrate_placeholders_to_null


def main() -> None:
    db_path = get_db_path()
    counts = safe_migrate_placeholders_to_null(db_path=db_path)
    print(f"db_migration_done: {db_path}")
    for k, v in sorted(counts.items()):
        print(f"- {k}: {v} rows updated")


if __name__ == "__main__":
    main()

