from __future__ import annotations

"""Phase 4 monthly HTML report CLI (dry-run by default).

Reads `industry_cycle_signal`, `industry_signal_reason`,
`industry_virtual_position`, and `data_quality_event` -- never recomputes
them -- and either:
- prints a short summary of what the report would contain (default; no file
  written), or
- writes `docs/industry_monthly_reports/<period_start>_<period_end>.html`
  plus a `latest.html` copy, only when `--execute` is passed.

Defaults `--period-start`/`--period-end` to the previous full calendar month
relative to `--as-of` (today by default), matching design doc section 3's
"성과·오판 분석: 월 1회" cadence.
"""

import argparse
import calendar
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import cycle_model_config, monthly_report

OUTPUT_DIR = ROOT_DIR / "docs" / "industry_monthly_reports"
DB_PATH = ROOT_DIR / "data" / "investment.db"


def _previous_month_bounds(as_of: date) -> tuple[str, str]:
    first_of_this_month = as_of.replace(day=1)
    last_day_prev_month = first_of_this_month - date.resolution
    period_start = last_day_prev_month.replace(day=1)
    return period_start.isoformat(), last_day_prev_month.isoformat()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build (and optionally write) the Phase 4 monthly HTML report.")
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Reference date used to pick the default previous-month window.")
    default_start, default_end = _previous_month_bounds(date.today())
    parser.add_argument("--period-start", default=default_start, help="Report window start (YYYY-MM-DD), inclusive.")
    parser.add_argument("--period-end", default=default_end, help="Report window end (YYYY-MM-DD), inclusive.")
    parser.add_argument(
        "--cycle-model-config",
        default=str(cycle_model_config.CYCLE_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_model.json.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write the HTML report file. Without this flag, only prints a summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = cycle_model_config.load_cycle_model_config(Path(args.cycle_model_config))
    model_version = cfg["model_version"]

    report = monthly_report.build_monthly_report(
        model_version, period_start=args.period_start, period_end=args.period_end, db_path=DB_PATH
    )

    perf = report["performance"]
    print(
        f"build_industry_monthly_report_plan period={args.period_start}~{args.period_end} "
        f"model_version={model_version} execute={args.execute}"
    )
    print(f"  state_change_events={len(report['state_change_events'])}")
    print(f"  virtual_portfolio open={perf.get('open_count', 0)} closed={perf.get('closed_count', 0)}")
    print(f"  best_industry={(report['best_industry'] or {}).get('position', {}).get('industry_id')}")
    print(f"  worst_industry={(report['worst_industry'] or {}).get('position', {}).get('industry_id')}")
    print(f"  data_quality_events={len(report['data_quality_events'])}")
    print(f"  model_change_notes={report['model_change_notes']}")

    if not args.execute:
        print("build_industry_monthly_report_dry_run_only (pass --execute to actually write the HTML file)")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html_out = monthly_report.render_monthly_report_html(report)
    dated_path = OUTPUT_DIR / f"{args.period_start}_{args.period_end}.html"
    dated_path.write_text(html_out, encoding="utf-8")
    latest_path = OUTPUT_DIR / "latest.html"
    latest_path.write_text(html_out, encoding="utf-8")
    print(f"build_industry_monthly_report_done wrote={dated_path} and {latest_path}")


if __name__ == "__main__":
    main()
