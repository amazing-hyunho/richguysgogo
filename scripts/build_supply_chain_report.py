"""Validate the catalogue and render a portable, source-linked research report."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from committee.industry_cycle.supply_chain import load_supply_chain_dashboard_data


def main() -> None:
    data = load_supply_chain_dashboard_data()
    companies = {c["company_id"]: c for c in data["companies"]}
    sources = {s["source_id"]: s for s in data["sources"]}
    lines = ["# 산업별 소부장 조사 지도", "", f"조사 확인일: {data['research_as_of']}", "",
             "상태: 25개 산업의 초기 지도. 전수조사·투자 적합성 평가·사이클 시차 검증은 완료되지 않았습니다.", ""]
    lines += [f"- {m}" for m in data["methodology"]]
    for i in data["industries"]:
        lines += ["", f"## {i['research_order']}. {i['name']}", "", i["focus"], "",
                  "전달 가설: " + " → ".join(i["chain"]), "", "확장 순서: " + i["research_path"], ""]
        for r in data["relationships"]:
            if r["industry_id"] != i["industry_id"]:
                continue
            c = companies[r["company_id"]]
            lines += [f"### {c['name']} ({c['ticker']}) — {r['product']}", "", r["fact"], "",
                      "공급 대상: " + r["recipient"], "", r["relationship_note"], "",
                      "추적할 지표: " + ", ".join(r["cycle_hypothesis"]["watch_metrics"]), "",
                      "반증 조건: " + r["cycle_hypothesis"]["falsifier"], "",
                      "실적 반영 시차: 미검증. 고객별 비중은 확인 근거가 없는 경우 미확인으로 유지.", ""]
            exposure=r["revenue_exposure"]
            if exposure["value_pct"] is not None:
                lines += [f"매출 비중: {exposure['value_pct']}% · {exposure['period']} · {exposure['scope']}", ""]
            for o in c.get("research_observations",[]):
                lines += [f"- 정량 근거: {o['label']} {o['value']} {o['unit']} · {o['period']} · {o['scope']}"]
            ids = list(dict.fromkeys(r["fact_source_ids"] + [link["source_id"] for link in r["external_links"]] + [o["source_id"] for o in c.get("research_observations",[])]))
            for link in r["external_links"]:
                lines += [f"- 추가 관계: {link['name']} ({link['relationship']}) — {link['note']}"]
            for sid in ids:
                s = sources[sid]
                lines += [f"- 근거: [{s['title']}]({s['url']}) · 자료 기준 {s['data_as_of'] or '미표기'} · 공개일 {s['published_at'] or '미확인'} · 확인일 {s['accessed_at']}"]
        lines += ["", "다음 단계: " + i["next_step"]]
    dest = ROOT / "docs" / "industry_supply_chain_research.md"
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(data["summary"])
    print(f"Report generated: {dest}")


if __name__ == "__main__":
    main()
