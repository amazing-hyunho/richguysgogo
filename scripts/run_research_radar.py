from __future__ import annotations

"""Build a research-to-market radar report from a point-in-time evidence file.

The command is dry-run by default.  Pass ``--execute`` to write JSON and
Markdown under ``runs/<as-of>/research_radar/``.
"""

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.research_radar.models import RadarValidationError
from committee.research_radar.runner import analyze_file, write_report_artifacts


DEFAULT_INPUT = ROOT_DIR / "config" / "research_radar_transformer.json"
DEFAULT_OUTPUT_ROOT = ROOT_DIR / "runs"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score a paper-to-talent-to-capital-to-bottleneck-to-earnings evidence chain."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to research-radar-input-v1 JSON.")
    parser.add_argument(
        "--as-of",
        default=None,
        help="Optional point-in-time override (YYYY-MM-DD); future-known evidence is excluded.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Artifact root; files are written below <root>/<as-of>/research_radar/.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write JSON/Markdown. Without this flag, only print the deterministic plan.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    input_path = args.input if args.input.is_absolute() else (ROOT_DIR / args.input)
    output_root = args.output_root if args.output_root.is_absolute() else (ROOT_DIR / args.output_root)
    try:
        report = analyze_file(input_path, as_of_override=args.as_of)
    except RadarValidationError as exc:
        print(f"run_research_radar_error {exc}", file=sys.stderr)
        return 2

    print(
        f"run_research_radar_plan theme_id={report.theme_id} as_of={report.as_of} "
        f"status={report.status} chain_score={report.chain_score:.2f} "
        f"confidence={report.confidence:.2f} execute={args.execute}"
    )
    for stage in report.stages:
        print(
            f"  stage={stage.stage} score={stage.score:.2f} confidence={stage.confidence:.2f} "
            f"evidence={stage.evidence_count} passed={stage.passed}"
        )
    print(
        f"  public_companies={len(report.public_companies)} "
        f"included_evidence={len(report.evidence)} excluded_evidence={len(report.excluded_evidence)}"
    )

    if not args.execute:
        print("run_research_radar_dry_run_only (pass --execute to write JSON and Markdown)")
        return 0

    json_path, markdown_path = write_report_artifacts(report, output_root=output_root)
    print(f"run_research_radar_done json={json_path} markdown={markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
