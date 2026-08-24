from __future__ import annotations

"""Build the weekly 미래 경제 연구소 state from verified evidence artifacts."""

import argparse
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.future_economy.collectors import (
    collect_live_policy_evidence,
    collect_market_evidence,
    collect_stored_news_evidence,
    load_historical_analogue_evidence,
)
from committee.future_economy.lifecycle import (
    FutureEconomyValidationError,
    REPORT_SCHEMA_VERSION,
    build_committee_agenda,
    build_evidence_artifact,
    build_weekly_report,
    normalize_evidence,
    radar_report_to_candidate,
)
from committee.future_economy.official_collectors import (
    collect_dart_disclosure_evidence,
    collect_official_policy_api_evidence,
    fetch_federal_register_documents,
)
from committee.core.env_loader import load_project_env
from committee.tools.dart_client import fetch_disclosures


DEFAULT_OUTPUT_ROOT = ROOT_DIR / "runs"
DEFAULT_RESEARCH_CONFIG = ROOT_DIR / "config" / "research_radar_topics.json"
DEFAULT_DOMAIN_CONFIG = ROOT_DIR / "config" / "future_economy_domains.json"
DEFAULT_HISTORICAL_CONFIG = ROOT_DIR / "config" / "future_economy_historical_analogues.json"
DEFAULT_DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="미래 경제 연구소 주간 연구 상태·위원회 안건 생성")
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--research-config", type=Path, default=DEFAULT_RESEARCH_CONFIG)
    parser.add_argument("--domain-config", type=Path, default=DEFAULT_DOMAIN_CONFIG)
    parser.add_argument("--historical-config", type=Path, default=DEFAULT_HISTORICAL_CONFIG)
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument(
        "--skip-live-policy",
        action="store_true",
        help="당일 정책 RSS 보강을 생략하고 저장된 산업 뉴스만 사용",
    )
    parser.add_argument(
        "--skip-official-policy-api",
        action="store_true",
        help="Federal Register 정부·규제 원문 API 보강 생략",
    )
    parser.add_argument(
        "--skip-dart-disclosures",
        action="store_true",
        help="DART 주요 공시 전용 수집 생략",
    )
    parser.add_argument("--execute", action="store_true", help="주간 산출물을 실제 저장")
    return parser.parse_args(argv)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_root_not_object:{path}")
    return payload


def _load_current_radar_reports(output_root: Path, as_of: str) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in sorted((output_root / as_of / "research_radar").glob("*.json")):
        try:
            payload = _load_json(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if payload.get("schema_version") == "research-radar-report-v1":
            reports.append(payload)
    return reports


def _load_previous_report(output_root: Path, as_of: str) -> dict[str, Any] | None:
    candidates: list[tuple[str, Path, dict[str, Any]]] = []
    for path in output_root.glob("*/future_economy/weekly_report.json"):
        try:
            payload = _load_json(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        report_as_of = str(payload.get("as_of") or "")
        if payload.get("schema_version") == REPORT_SCHEMA_VERSION and report_as_of < as_of:
            candidates.append((report_as_of, path, payload))
    return max(candidates, key=lambda row: (row[0], str(row[1])))[2] if candidates else None


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(text, encoding="utf-8")
    temp_path.replace(path)


def _render_markdown(report: Mapping[str, Any], agenda: Mapping[str, Any]) -> str:
    summary = report.get("summary") or {}
    lines = [
        "# 미래 경제 연구소 · 주간 보고서",
        "",
        f"- 기준일: `{report.get('as_of') or '-'}`",
        f"- 활성 연구: **{summary.get('active', 0)}개**",
        f"- 신규/강화/약화: **{summary.get('new', 0)} / {summary.get('strengthened', 0)} / {summary.get('weakened', 0)}**",
        f"- AI 투자위원회 검토 안건: **{agenda.get('item_count', 0)}개**",
        "",
        "> 미래 성장 가설의 근거 성숙도를 추적하는 보고서이며 주문·자동매매 지시가 아닙니다.",
        "",
        "## 활성 연구 과제",
        "",
    ]
    tasks = [row for row in report.get("research_tasks", []) if isinstance(row, Mapping)]
    if not tasks:
        lines.append("- 이번 주 등록된 연구 과제가 없습니다.")
    for task in tasks:
        lines.extend([
            f"### {task.get('title') or task.get('research_id')}",
            "",
            f"- 상태: `{task.get('status')}` · 주간 변화: `{task.get('weekly_change')}`",
            f"- 근거 유형: {task.get('evidence_type_count', 0)}종 · 연구 점수: {task.get('research_score', 0)}",
            f"- 가설: {task.get('thesis') or '-'}",
            "",
        ])
        evidence = [row for row in task.get("evidence", []) if isinstance(row, Mapping)]
        for row in evidence[-5:]:
            lines.append(f"- [{row.get('title') or '근거'}]({row.get('source_url')}) — {row.get('claim') or '-'}")
        lines.append("")
    return "\n".join(lines)


def build_artifacts(
    *,
    as_of: str,
    output_root: Path,
    research_config: Mapping[str, Any],
    domain_config: Mapping[str, Any],
    historical_config: Mapping[str, Any],
    db_path: Path,
    include_live_policy: bool = False,
    official_policy_documents: list[Mapping[str, Any]] | None = None,
    dart_disclosures: list[Mapping[str, Any]] | None = None,
    prefetch_errors: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    topics = {
        str(row.get("theme_id")): dict(row)
        for row in research_config.get("topics", [])
        if isinstance(row, Mapping) and str(row.get("theme_id") or "")
    }
    discovery_domains = [
        row for row in domain_config.get("discovery_domains", []) if isinstance(row, Mapping)
    ]
    free_discovery_slots = int(domain_config.get("free_discovery_slots") or 0)
    if len(discovery_domains) > free_discovery_slots:
        raise ValueError(
            f"discovery_domains_exceed_slots:{len(discovery_domains)}>{free_discovery_slots}"
        )
    domains = {
        str(row.get("domain_id")): dict(row)
        for row in [*domain_config.get("domains", []), *discovery_domains]
        if isinstance(row, Mapping) and str(row.get("domain_id") or "")
    }
    for topic in topics.values():
        domain = domains.get(str(topic.get("domain_id") or ""), {})
        topic.setdefault("horizon_months", domain_config.get("horizon_months", 12))
        for key in (
            "research_mode",
            "transmission_chain",
            "watch_industries",
            "invalidation_conditions",
        ):
            topic.setdefault(key, domain.get(key, []))

    radar_reports = _load_current_radar_reports(output_root, as_of)
    previous = _load_previous_report(output_root, as_of)
    previous_by_domain = {
        str(row.get("domain_id") or ""): row
        for row in (previous or {}).get("research_tasks", [])
        if isinstance(row, Mapping) and str(row.get("domain_id") or "")
    }
    candidates_by_domain: dict[str, dict[str, Any]] = {}
    for radar_report in radar_reports:
        theme = radar_report.get("theme") or {}
        theme_id = str(theme.get("theme_id") or "")
        topic = dict(topics.get(theme_id, {}))
        if not topic:
            alias_domain_id = str((domain_config.get("legacy_theme_aliases") or {}).get(theme_id) or "")
            if alias_domain_id:
                topic = {"domain_id": alias_domain_id}
                domain = domains.get(alias_domain_id, {})
                topic["horizon_months"] = domain_config.get("horizon_months", 12)
                for key in (
                    "research_mode",
                    "transmission_chain",
                    "watch_industries",
                    "invalidation_conditions",
                ):
                    topic[key] = domain.get(key, [])
        candidate = radar_report_to_candidate(radar_report, as_of=as_of, topic_config=topic)
        if candidate is not None:
            domain_id = str(candidate.get("domain_id") or candidate.get("research_id") or "")
            previous_task = previous_by_domain.get(domain_id)
            if previous_task:
                candidate["research_id"] = str(previous_task.get("research_id") or candidate["research_id"])
            candidates_by_domain[domain_id] = candidate

    for topic in topics.values():
        domain_id = str(topic.get("domain_id") or topic.get("theme_id") or "")
        domain = domains.get(domain_id, {})
        if domain_id in candidates_by_domain:
            continue
        previous_task = previous_by_domain.get(domain_id)
        candidates_by_domain[domain_id] = {
            "research_id": str((previous_task or {}).get("research_id") or topic.get("theme_id") or domain_id),
            "domain_id": domain_id,
            "title": str(topic.get("name") or domain.get("name") or domain_id),
            "thesis": str(topic.get("thesis") or ""),
            "horizon_months": int(topic.get("horizon_months") or domain_config.get("horizon_months", 12)),
            "research_mode": str(topic.get("research_mode") or domain.get("research_mode") or "core"),
            "transmission_chain": list(topic.get("transmission_chain") or domain.get("transmission_chain") or []),
            "watch_industries": list(topic.get("watch_industries") or domain.get("watch_industries") or []),
            "watch_companies": [],
            "historical_analogues": [],
            "invalidation_conditions": list(
                topic.get("invalidation_conditions") or domain.get("invalidation_conditions") or []
            ),
            "evidence": [],
        }

    collector_counts = {key: 0 for key in ("policy", "research", "corporate", "market", "historical_analogy")}
    collector_errors: list[str] = list(prefetch_errors or [])
    candidates: list[dict[str, Any]] = []
    for domain_id, candidate in sorted(candidates_by_domain.items()):
        domain = domains.get(domain_id, {"domain_id": domain_id})
        current_evidence = [row for row in candidate.get("evidence", []) if isinstance(row, Mapping)]
        try:
            current_evidence.extend(
                collect_stored_news_evidence(domain=domain, as_of=as_of, db_path=db_path)
            )
        except Exception as exc:  # collector isolation is part of the weekly contract
            collector_errors.append(f"stored_news:{domain_id}:{exc}")
        try:
            current_evidence.extend(
                collect_market_evidence(domain=domain, as_of=as_of, db_path=db_path)
            )
        except Exception as exc:
            collector_errors.append(f"market:{domain_id}:{exc}")
        if include_live_policy:
            try:
                current_evidence.extend(collect_live_policy_evidence(domain=domain, as_of=as_of))
            except Exception as exc:
                collector_errors.append(f"live_policy:{domain_id}:{exc}")
        try:
            current_evidence.extend(
                collect_official_policy_api_evidence(
                    domain=domain,
                    as_of=as_of,
                    documents=list(official_policy_documents or []),
                )
            )
        except Exception as exc:
            collector_errors.append(f"official_policy_api:{domain_id}:{exc}")
        try:
            dart_evidence, watch_companies = collect_dart_disclosure_evidence(
                domain=domain,
                as_of=as_of,
                db_path=db_path,
                disclosures=list(dart_disclosures or []),
            )
            current_evidence.extend(dart_evidence)
            if watch_companies:
                company_by_key = {
                    (str(row.get("stock_code") or ""), str(row.get("source_url") or "")): dict(row)
                    for row in [*candidate.get("watch_companies", []), *watch_companies]
                    if isinstance(row, Mapping)
                }
                candidate["watch_companies"] = list(company_by_key.values())
        except Exception as exc:
            collector_errors.append(f"dart_disclosures:{domain_id}:{exc}")

        normalized_current: list[dict[str, Any]] = []
        for row in current_evidence:
            try:
                normalized = normalize_evidence(row, as_of=as_of)
            except FutureEconomyValidationError as exc:
                collector_errors.append(f"invalid_evidence:{domain_id}:{exc}")
                continue
            if normalized is not None:
                normalized_current.append(normalized)
        if not normalized_current:
            continue

        historical_rows, analogues = load_historical_analogue_evidence(
            domain_id=domain_id, as_of=as_of, payload=historical_config
        )
        normalized_historical: list[dict[str, Any]] = []
        for row in historical_rows:
            try:
                normalized = normalize_evidence(row, as_of=as_of)
            except FutureEconomyValidationError as exc:
                collector_errors.append(f"invalid_historical:{domain_id}:{exc}")
                continue
            if normalized is not None:
                normalized_historical.append(normalized)
        candidate["evidence"] = [*normalized_current, *normalized_historical]
        candidate["historical_analogues"] = analogues
        for row in candidate["evidence"]:
            evidence_type = str(row.get("evidence_type") or "")
            if evidence_type in collector_counts:
                collector_counts[evidence_type] += 1
        candidates.append(candidate)

    report = build_weekly_report(as_of=as_of, candidates=candidates, previous_report=previous)
    agenda = build_committee_agenda(report)
    evidence = build_evidence_artifact(report)
    input_hash = hashlib.sha256(
        json.dumps(
            {"as_of": as_of, "candidates": candidates, "previous": previous},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    audit = {
        "schema_version": "future-economy-audit-v1",
        "as_of": as_of,
        "radar_report_count": len(radar_reports),
        "candidate_count": len(candidates),
        "collector_counts": collector_counts,
        "collector_errors": collector_errors,
        "official_policy_document_count": len(official_policy_documents or []),
        "dart_disclosure_count": len(dart_disclosures or []),
        "previous_as_of": previous.get("as_of") if previous else None,
        "research_task_count": len(report["research_tasks"]),
        "agenda_item_count": agenda["item_count"],
        "input_hash": input_hash,
    }
    return report, agenda, evidence, audit


def main(argv: list[str] | None = None) -> int:
    load_project_env(ROOT_DIR)
    args = _parse_args(argv)
    try:
        as_of = date.fromisoformat(args.as_of).isoformat()
        output_root = args.output_root if args.output_root.is_absolute() else ROOT_DIR / args.output_root
        research_config_path = args.research_config if args.research_config.is_absolute() else ROOT_DIR / args.research_config
        domain_config_path = args.domain_config if args.domain_config.is_absolute() else ROOT_DIR / args.domain_config
        historical_config_path = (
            args.historical_config if args.historical_config.is_absolute() else ROOT_DIR / args.historical_config
        )
        db_path = args.db_path if args.db_path.is_absolute() else ROOT_DIR / args.db_path
        research_config = _load_json(research_config_path)
        domain_config = _load_json(domain_config_path)
        historical_config = _load_json(historical_config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"future_economy_weekly_error config={exc}", file=sys.stderr)
        return 2

    print(
        f"future_economy_weekly_plan as_of={as_of} domains={len(domain_config.get('domains', []))} "
        f"discovery_domains={len(domain_config.get('discovery_domains', []))} "
        f"free_discovery_slots={domain_config.get('free_discovery_slots', 0)} execute={args.execute}"
    )
    if not args.execute:
        print("future_economy_weekly_dry_run_only (pass --execute to write artifacts)")
        return 0

    official_policy_documents: list[Mapping[str, Any]] = []
    dart_disclosure_rows: list[Mapping[str, Any]] = []
    prefetch_errors: list[str] = []
    if not args.skip_official_policy_api:
        try:
            official_policy_documents = fetch_federal_register_documents(as_of=as_of)
            print(f"future_economy_official_policy_fetched documents={len(official_policy_documents)}")
        except Exception as exc:
            prefetch_errors.append(f"official_policy_api:fetch:{exc}")
            print(f"future_economy_official_policy_failed error={exc}", file=sys.stderr)
    if not args.skip_dart_disclosures:
        if os.getenv("DART_API_KEY", "").strip() or os.getenv("OPEN_DART_API_KEY", "").strip():
            try:
                end = date.fromisoformat(as_of)
                dart_disclosure_rows = fetch_disclosures(end - timedelta(days=13), end)
                print(f"future_economy_dart_fetched disclosures={len(dart_disclosure_rows)}")
            except Exception as exc:
                prefetch_errors.append(f"dart_disclosures:fetch:{exc}")
                print(f"future_economy_dart_failed error={exc}", file=sys.stderr)
        else:
            prefetch_errors.append("dart_disclosures:missing_api_key")

    report, agenda, evidence, audit = build_artifacts(
        as_of=as_of,
        output_root=output_root,
        research_config=research_config,
        domain_config=domain_config,
        historical_config=historical_config,
        db_path=db_path,
        include_live_policy=not args.skip_live_policy,
        official_policy_documents=official_policy_documents,
        dart_disclosures=dart_disclosure_rows,
        prefetch_errors=prefetch_errors,
    )
    target = output_root / as_of / "future_economy"
    _atomic_write(target / "weekly_report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(target / "committee_agenda.json", json.dumps(agenda, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(target / "evidence.json", json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(target / "audit.json", json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(target / "weekly_report.md", _render_markdown(report, agenda).rstrip() + "\n")
    print(
        f"future_economy_weekly_done research={len(report['research_tasks'])} "
        f"agenda={agenda['item_count']} evidence={evidence['evidence_count']} output={target}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
