#!/usr/bin/env python3
"""Render the Pages dashboard with the latest template and existing payload."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts import build_dashboard  # noqa: E402


def load_embedded_dashboard_data(path: Path) -> dict[str, object]:
    html = path.read_text(encoding="utf-8")
    marker = "const _dash = "
    start = html.find(marker)
    if start == -1:
        raise ValueError("dashboard_missing_embedded_data")
    payload, _ = json.JSONDecoder().raw_decode(html[start + len(marker) :])
    if not isinstance(payload, dict):
        raise ValueError("dashboard_embedded_data_is_not_an_object")
    return payload


def refresh_meeting_data(data: dict) -> None:
    """A checkout can lag the already-built HTML when only news was published."""
    incoming = build_dashboard.load_latest_committee()
    current = data.get("latest_committee") or {}
    if str(incoming.get("market_date", "")) < str(current.get("market_date", "")):
        return
    # Never discard a valid report for an incomplete same-day artifact.
    if not incoming.get("sugeup_narrative") and current.get("sugeup_narrative"):
        return
    data["latest_committee"] = incoming
    data["latest_stances"] = build_dashboard.load_latest_stances()
    data["latest_debate_minutes"] = build_dashboard.load_latest_debate_minutes()
    data["recent_meeting_timeline"] = build_dashboard.load_recent_meeting_timeline()
    data["meeting_handoff"] = build_dashboard.load_handoff_context()


def main() -> None:
    output_path = build_dashboard.OUTPUT_PATH
    data = load_embedded_dashboard_data(output_path)
    data["korea_macro"] = build_dashboard.load_korea_macro_data()
    # Meetings are file-backed; refresh them on Pages even when the DB is absent.
    refresh_meeting_data(data)
    data["research_radar"] = build_dashboard.load_research_radar_dashboard_data()
    data["supply_chain"] = build_dashboard.load_supply_chain_dashboard_data()
    output_path.write_text(build_dashboard.build_dashboard_html(data), encoding="utf-8")
    print(f"Pages dashboard rendered: {output_path}")


if __name__ == "__main__":
    main()
