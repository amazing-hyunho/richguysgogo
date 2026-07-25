from __future__ import annotations

"""Phase 4 monthly HTML report (design doc section 11.3).

Read-only aggregation over already-computed Phase 4 tables
(`industry_cycle_signal`, `industry_signal_reason`, `industry_virtual_position`,
`data_quality_event`). Nothing here computes a new score or changes a
weight -- section 11.3's closing line is enforced by construction:
"자동으로 가중치를 변경하지 않는다. 변경안은 백테스트와 승인 후 새
model_version으로 적용한다." `model_change_notes` is always a plain
observation string, never an applied config change.

Required sections (design doc 11.3):
1. 한 달간 발생·해제된 신호           -> `state_change_events`
2. 이전 신호의 상대수익률              -> `performance` (from the virtual-portfolio ledger)
3. 가장 잘 맞은 산업과 가장 크게 틀린 산업 -> `best_industry` / `worst_industry`
4. 오판에 기여한 지표                  -> `worst_industry_top_reasons`
5. 데이터 누락과 공급자 장애            -> `data_quality_events`
6. 모델 변경 제안                     -> `model_change_notes` (observation only)
"""

import html
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import cycle_repository, repository as industry_repository, virtual_portfolio


def _industry_name_lookup(db_path: Path | None) -> Dict[str, str]:
    try:
        rows = industry_repository.list_industries(db_path=db_path)
    except Exception:
        return {}
    return {r["industry_id"]: (r.get("name_kr") or r.get("name_en") or r["industry_id"]) for r in rows}


def compute_state_change_events(
    model_version: str, *, period_start: str, period_end: str, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    """Every confirmed-state transition (new confirmation, or a release back
    to no-confirmation) whose `as_of` falls within `[period_start, period_end]`.

    Compares each row's `confirmed_state` to its own `previous_confirmed_state`
    field (already computed and stored by the state machine at signal time),
    so this never re-derives point-in-time state itself.
    """
    try:
        all_signals = cycle_repository.list_cycle_signals(model_version=model_version, db_path=db_path)
    except Exception:
        return []

    events: List[Dict[str, Any]] = []
    for sig in all_signals:
        as_of = sig.get("as_of")
        if as_of is None or not (period_start <= as_of <= period_end):
            continue
        confirmed = sig.get("confirmed_state")
        previous = sig.get("previous_confirmed_state")
        if sig.get("confirmation_status") == "confirmed" and confirmed != previous:
            events.append(
                {
                    "industry_id": sig["industry_id"], "as_of": as_of, "event": "newly_confirmed",
                    "state": confirmed, "previous_state": previous,
                }
            )
        elif confirmed is None and previous is not None:
            events.append(
                {
                    "industry_id": sig["industry_id"], "as_of": as_of, "event": "released",
                    "state": confirmed, "previous_state": previous,
                }
            )
    events.sort(key=lambda e: (e["as_of"], e["industry_id"]))
    return events


def _best_worst_industry(positions: List[Dict[str, Any]]) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Rank by the longest-horizon excess return actually available for each
    position (12m preferred, falling back to 6m/3m/1m), so a report early in
    the ledger's life doesn't silently exclude every open position."""
    scored = []
    for p in positions:
        for months in (12, 6, 3, 1):
            value = p.get(f"excess_return_{months}m")
            if value is not None:
                scored.append((value, months, p))
                break
    if not scored:
        return None, None
    scored.sort(key=lambda t: t[0])
    worst = scored[0]
    best = scored[-1]
    return (
        {"excess_return": best[0], "horizon_months": best[1], "position": best[2]},
        {"excess_return": worst[0], "horizon_months": worst[1], "position": worst[2]},
    )


def build_monthly_report(
    model_version: str, *, period_start: str, period_end: str, db_path: Path | None = None
) -> Dict[str, Any]:
    """Assemble the full monthly report payload. Every sub-section degrades to
    an empty list/None rather than raising if its source table has no rows
    yet (integration rule: 빈 상태를 정상 렌더링)."""
    names = _industry_name_lookup(db_path)

    state_change_events = compute_state_change_events(
        model_version, period_start=period_start, period_end=period_end, db_path=db_path
    )
    for e in state_change_events:
        e["industry_name"] = names.get(e["industry_id"], e["industry_id"])

    try:
        performance = virtual_portfolio.summarize_portfolio_performance(
            model_version, today=period_end, db_path=db_path
        )
    except Exception as exc:
        performance = {"positions": [], "open_count": 0, "closed_count": 0, "error": str(exc)}

    best, worst = _best_worst_industry(performance.get("positions", []))
    worst_reasons: List[Dict[str, Any]] = []
    if worst is not None:
        worst_industry_id = worst["position"].get("industry_id")
        worst_as_of = worst["position"].get("entry_as_of")
        try:
            worst_reasons = cycle_repository.list_signal_reasons(
                worst_industry_id, worst_as_of, model_version, db_path=db_path
            )[:5]
        except Exception:
            worst_reasons = []

    try:
        all_dq_events = industry_repository.list_data_quality_events(db_path=db_path)
    except Exception:
        all_dq_events = []
    data_quality_events = [
        e for e in all_dq_events
        if e.get("detected_at") and period_start <= str(e["detected_at"])[:10] <= period_end
    ]

    sample_size = performance.get("six_month_sample_size", 0)
    if sample_size and sample_size >= 5:
        model_change_notes = (
            f"6개월 표본 {sample_size}건 확보. 백테스트/워크포워드 검증 없이 가중치를 임의로 바꾸지 않습니다 "
            "-- Phase 5에서 정식으로 검토하세요."
        )
    else:
        model_change_notes = (
            f"6개월 성과 표본이 아직 {sample_size}건뿐입니다. 데이터가 더 쌓이기 전에는 모델 변경을 제안하지 않습니다."
        )

    return {
        "model_version": model_version,
        "period_start": period_start,
        "period_end": period_end,
        "state_change_events": state_change_events,
        "performance": performance,
        "best_industry": best,
        "worst_industry": worst,
        "worst_industry_top_reasons": worst_reasons,
        "data_quality_events": data_quality_events,
        "model_change_notes": model_change_notes,
    }


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _pct(value: Optional[float]) -> str:
    if value is None:
        return "누적 중 (INSUFFICIENT_DATA)"
    return f"{value * 100:+.1f}%"


def _render_state_change_events(events: List[Dict[str, Any]]) -> str:
    if not events:
        return '<p class="empty">이번 기간에 새로 확정되거나 해제된 신호가 없습니다.</p>'
    rows = "".join(
        f"<tr><td>{_e(e['as_of'])}</td><td>{_e(e['industry_name'])}</td>"
        f"<td>{_e(e['event'])}</td><td>{_e(e['previous_state'])} → {_e(e['state'])}</td></tr>"
        for e in events
    )
    return f"""<table><thead><tr><th>기준일</th><th>산업</th><th>이벤트</th><th>상태 변화</th></tr></thead>
    <tbody>{rows}</tbody></table>"""


def _render_positions(positions: List[Dict[str, Any]]) -> str:
    if not positions:
        return '<p class="empty">가상 포트폴리오에 기록된 신호가 아직 없습니다.</p>'
    rows = []
    for p in positions:
        rows.append(
            f"<tr><td>{_e(p.get('industry_id'))}</td><td>{_e(p.get('status'))}</td>"
            f"<td>{_e(p.get('entry_as_of'))}</td><td>{_e(p.get('exit_as_of') or '-')}</td>"
            f"<td>{_e(p.get('exit_reason') or '-')}</td>"
            f"<td>{_pct(p.get('excess_return_1m'))}</td><td>{_pct(p.get('excess_return_3m'))}</td>"
            f"<td>{_pct(p.get('excess_return_6m'))}</td><td>{_pct(p.get('excess_return_12m'))}</td></tr>"
        )
    return f"""<table><thead><tr><th>산업</th><th>상태</th><th>진입일</th><th>청산일</th><th>청산사유</th>
    <th>1개월 초과수익</th><th>3개월 초과수익</th><th>6개월 초과수익</th><th>12개월 초과수익</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table>"""


def _render_best_worst(label: str, entry: Optional[Dict[str, Any]]) -> str:
    if entry is None:
        return f'<div class="card"><div class="card-label">{_e(label)}</div><p class="empty">아직 판단할 데이터가 없습니다.</p></div>'
    pos = entry["position"]
    return (
        f'<div class="card"><div class="card-label">{_e(label)}</div>'
        f'<div class="card-value">{_e(pos.get("industry_id"))}</div>'
        f'<div class="card-sub">{entry["horizon_months"]}개월 초과수익 {_pct(entry["excess_return"])}</div></div>'
    )


def _render_reasons(reasons: List[Dict[str, Any]]) -> str:
    if not reasons:
        return '<p class="empty">근거 데이터가 없습니다.</p>'
    items = "".join(
        f"<li>{_e(r.get('component_key'))}: 기여도 {_e(r.get('contribution'))} ({_e(r.get('direction'))})</li>"
        for r in reasons
    )
    return f"<ul>{items}</ul>"


def _render_data_quality(events: List[Dict[str, Any]]) -> str:
    if not events:
        return '<p class="empty">이번 기간에 기록된 데이터 품질 이벤트가 없습니다.</p>'
    rows = "".join(
        f"<tr><td>{_e(str(e.get('detected_at'))[:10])}</td><td>{_e(e.get('provider'))}</td>"
        f"<td>{_e(e.get('target'))}</td><td>{_e(e.get('event_type'))}</td><td>{_e(e.get('severity'))}</td>"
        f"<td>{_e(e.get('message'))}</td></tr>"
        for e in events
    )
    return f"""<table><thead><tr><th>발생일</th><th>공급자</th><th>대상</th><th>이벤트 유형</th><th>심각도</th><th>메시지</th></tr></thead>
    <tbody>{rows}</tbody></table>"""


def render_monthly_report_html(report: Dict[str, Any]) -> str:
    """Render `build_monthly_report`'s output as a standalone, self-contained
    HTML document (no external JS/CSS dependency, safe to archive as a static
    file per month)."""
    perf = report.get("performance") or {}
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>산업 사이클 월간 리포트 {_e(report.get('period_start'))} ~ {_e(report.get('period_end'))}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Noto Sans KR", sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:24px; }}
  .container {{ max-width: 980px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin-bottom: 4px; }}
  .subtitle {{ color:#94a3b8; font-size:13px; margin-bottom:28px; }}
  h2 {{ font-size:16px; border-bottom:1px solid #334155; padding-bottom:8px; margin-top:32px; }}
  table {{ width:100%; border-collapse: collapse; font-size:13px; margin-top:10px; }}
  th, td {{ border-bottom:1px solid #334155; padding:6px 8px; text-align:left; }}
  th {{ color:#94a3b8; font-weight:600; }}
  .empty {{ color:#94a3b8; font-size:13px; font-style:italic; }}
  .card-grid {{ display:flex; gap:12px; margin-top:10px; }}
  .card {{ flex:1; background:#1e293b; border:1px solid #334155; border-radius:10px; padding:12px 14px; }}
  .card-label {{ font-size:11px; color:#94a3b8; text-transform:uppercase; }}
  .card-value {{ font-size:16px; font-weight:800; margin-top:4px; }}
  .card-sub {{ font-size:12px; color:#cbd5e1; margin-top:4px; }}
  .notes {{ margin-top:10px; padding:12px 14px; background:#1e293b; border:1px solid #334155; border-radius:10px; font-size:13px; line-height:1.5; }}
</style>
</head>
<body>
<div class="container">
  <h1>산업 사이클 월간 리포트</h1>
  <div class="subtitle">기간: {_e(report.get('period_start'))} ~ {_e(report.get('period_end'))} · 모델: {_e(report.get('model_version'))}</div>

  <h2>1. 이번 달 발생·해제된 신호</h2>
  {_render_state_change_events(report.get('state_change_events', []))}

  <h2>2. 가상 포트폴리오 신호별 성과</h2>
  <div class="card-sub">보유 중 {perf.get('open_count', 0)}건 · 청산 완료 {perf.get('closed_count', 0)}건 · 6개월 표본 {perf.get('six_month_sample_size', 0)}건 · 6개월 적중률 {_pct(perf.get('hit_rate_6m'))}</div>
  {_render_positions(perf.get('positions', []))}

  <h2>3. 가장 잘 맞은 산업 · 가장 크게 틀린 산업</h2>
  <div class="card-grid">
    {_render_best_worst('가장 잘 맞은 산업', report.get('best_industry'))}
    {_render_best_worst('가장 크게 틀린 산업', report.get('worst_industry'))}
  </div>

  <h2>4. 오판에 기여한 지표 (가장 크게 틀린 산업 기준)</h2>
  {_render_reasons(report.get('worst_industry_top_reasons', []))}

  <h2>5. 데이터 누락과 공급자 장애</h2>
  {_render_data_quality(report.get('data_quality_events', []))}

  <h2>6. 모델 변경 제안</h2>
  <div class="notes">{_e(report.get('model_change_notes'))}</div>
</div>
</body>
</html>
"""
