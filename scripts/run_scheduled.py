"""Run an existing batch with UTF-8 output and per-run logs on Windows."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"sync_all.py", "sync_weekly.py", "run_news_hourly.py", "send_morning.py"}


def main() -> int:
    startup = "--startup" in sys.argv
    if startup:
        sys.argv.remove("--startup")
    if len(sys.argv) < 2 or sys.argv[1] not in ALLOWED:
        raise SystemExit("Specify an existing scheduled batch script.")
    script = sys.argv[1]
    sys.path.insert(0, str(ROOT))
    from committee.core.env_loader import load_project_env

    load_project_env(ROOT)
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # Background jobs must use saved credentials without prompting for input.
    os.environ["GIT_TERMINAL_PROMPT"] = "0"
    os.environ["GCM_INTERACTIVE"] = "never"
    log_dir = Path(os.environ["LOCALAPPDATA"]) / "richguysgogo" / "autorun"
    log_dir.mkdir(parents=True, exist_ok=True)
    # Keep a second sign-in launcher from starting the same batch concurrently.
    import msvcrt

    lock = (log_dir / f"{Path(script).stem}.lock").open("a+b")
    lock.seek(0)
    if not lock.read(1):
        lock.write(b"0")
        lock.flush()
    lock.seek(0)
    try:
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        lock.close()
        return 0
    if startup:
        # Give the desktop, OneDrive and network time to become available.
        time.sleep(60)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    log_path = log_dir / f"{Path(script).stem}-{stamp}.log"
    python = Path(sys.executable).with_name("python.exe")
    with log_path.open("w", encoding="utf-8") as log:
        print(f"Started {script} at {datetime.now().isoformat()}", file=log, flush=True)
        try:
            result = subprocess.run(
                [str(python), "-X", "utf8", "-u", str(ROOT / "scripts" / script), *sys.argv[2:]],
                cwd=ROOT,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            code = result.returncode
        except Exception:
            import traceback

            traceback.print_exc(file=log)
            code = 1
        print(f"Finished at {datetime.now().isoformat()}, exit={code}", file=log)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
