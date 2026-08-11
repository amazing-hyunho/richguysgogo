from __future__ import annotations

"""Run weekly paper discovery and GPT interpretation for configured radar topics."""

import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.env_loader import load_project_env
from committee.research_radar.runner import _atomic_write, write_report_artifacts
from committee.research_radar.weekly import (
    InterpretationBatch,
    build_audit_payload,
    build_report,
    fetch_arxiv_papers,
    filter_papers_for_window,
    interpret_papers,
    load_weekly_config,
)
DEFAULT_CONFIG = ROOT_DIR / "config" / "research_radar_topics.json"
DEFAULT_OUTPUT_ROOT = ROOT_DIR / "runs"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="주간 미래산업 논문 수집·GPT 해석·레이더 보고서 생성")
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--lookback-days", type=int, default=None)
    parser.add_argument("--max-papers", type=int, default=None)
    parser.add_argument("--model", default=os.getenv("RESEARCH_RADAR_LLM_MODEL", "gpt-4.1"))
    parser.add_argument("--execute", action="store_true", help="네트워크·GPT 호출과 보고서 저장 실행")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    load_project_env(ROOT_DIR)
    args = _parse_args(argv)
    try:
        as_of = date.fromisoformat(args.as_of)
    except ValueError:
        print(f"research_radar_weekly_error invalid_as_of={args.as_of}", file=sys.stderr)
        return 2
    config_path = args.config if args.config.is_absolute() else ROOT_DIR / args.config
    output_root = args.output_root if args.output_root.is_absolute() else ROOT_DIR / args.output_root
    try:
        config = load_weekly_config(config_path)
    except Exception as exc:
        print(f"research_radar_weekly_error config={exc}", file=sys.stderr)
        return 2
    lookback_days = args.lookback_days or int(config.get("default_lookback_days", 28))
    max_papers = args.max_papers or int(config.get("default_max_papers", 20))
    topics = config["topics"]
    print(
        f"research_radar_weekly_plan as_of={as_of.isoformat()} topics={len(topics)} "
        f"lookback_days={lookback_days} max_papers={max_papers} model={args.model} execute={args.execute}"
    )
    if not args.execute:
        print("research_radar_weekly_dry_run_only (pass --execute to fetch papers and call GPT)")
        return 0

    try:
        from committee.tools.openai_chat import load_openai_config

        openai_config = load_openai_config()
    except Exception as exc:
        print(f"research_radar_weekly_error openai={exc}", file=sys.stderr)
        return 2

    failures = 0
    for topic in topics:
        theme_id = str(topic["theme_id"])
        try:
            fetched = fetch_arxiv_papers(
                str(topic["arxiv_query"]), max_results=max(max_papers * 3, 30)
            )
            papers = filter_papers_for_window(
                fetched, as_of=as_of, lookback_days=lookback_days
            )[:max_papers]
            print(f"research_radar_weekly_collected theme={theme_id} papers={len(papers)}")
            if papers:
                batch = interpret_papers(
                    topic,
                    papers,
                    as_of=as_of,
                    config=openai_config,
                    model=args.model,
                )
            else:
                batch = InterpretationBatch(
                    rows=(),
                    model=None,
                    input_tokens=None,
                    output_tokens=None,
                    input_hash=hashlib.sha256(
                        f"{theme_id}:{as_of.isoformat()}:no-papers".encode("utf-8")
                    ).hexdigest(),
                )
            report = build_report(topic, papers, batch.rows, as_of=as_of)
            json_path, markdown_path = write_report_artifacts(report, output_root=output_root)
            audit_path = output_root / as_of.isoformat() / "research_radar" / f"{theme_id}-weekly-audit.json"
            audit = build_audit_payload(
                topic,
                papers,
                batch,
                report,
                as_of=as_of,
                lookback_days=lookback_days,
            )
            _atomic_write(audit_path, json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
            print(
                f"research_radar_weekly_done theme={theme_id} accepted={len(report.evidence)} "
                f"status={report.status} score={report.chain_score:.2f} "
                f"json={json_path} markdown={markdown_path} audit={audit_path}"
            )
        except Exception as exc:
            failures += 1
            print(f"research_radar_weekly_failed theme={theme_id} error={exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
