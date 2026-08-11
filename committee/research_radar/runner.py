from __future__ import annotations

"""File boundary for loading inputs and writing deterministic artifacts."""

import json
import os
from pathlib import Path
import tempfile

from committee.research_radar.models import RadarReport, RadarValidationError, ThemeInput
from committee.research_radar.report import render_markdown
from committee.research_radar.scoring import analyze_theme


def load_theme_input(path: Path, *, as_of_override: str | None = None) -> ThemeInput:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RadarValidationError(f"invalid JSON in {path}: {exc.msg}") from exc
    except OSError as exc:
        raise RadarValidationError(f"unable to read {path}: {exc}") from exc
    return ThemeInput.from_dict(payload, as_of_override=as_of_override)


def analyze_file(path: Path, *, as_of_override: str | None = None) -> RadarReport:
    return analyze_theme(load_theme_input(path, as_of_override=as_of_override))


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def write_report_artifacts(report: RadarReport, *, output_root: Path) -> tuple[Path, Path]:
    output_dir = output_root / report.as_of / "research_radar"
    json_path = output_dir / f"{report.theme_id}.json"
    markdown_path = output_dir / f"{report.theme_id}.md"
    json_content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"
    _atomic_write(json_path, json_content)
    _atomic_write(markdown_path, render_markdown(report))
    return json_path, markdown_path
