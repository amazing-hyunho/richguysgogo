from __future__ import annotations

"""Import an Investment Thesis JSON draft into SQLite.

Usage:
    python scripts/import_thesis.py path/to/thesis.json
"""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import connect, init_db


DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import a Thesis Monitor JSON draft.")
    parser.add_argument("json_path", help="Path to thesis JSON file exported from dashboard.")
    return parser.parse_args()


def _json_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = [v.strip() for v in value.split(",") if v.strip()]
    return json.dumps(value, ensure_ascii=False)


def _infer_thesis_type(text: str) -> str:
    lower = text.lower()
    if re.search(r"금리|채권|yield|rate|fed|연준", lower):
        return "rates"
    if re.search(r"환율|원달러|달러|usd|dxy|currency", lower):
        return "currency"
    if re.search(r"물가|인플레|cpi|pce", lower):
        return "inflation"
    if re.search(r"신용|스프레드|oas|하이일드|credit", lower):
        return "credit"
    if re.search(r"실적|eps|영업이익|마진|earnings", lower):
        return "earnings"
    if re.search(r"수급|외국인|기관|liquidity|유동성", lower):
        return "liquidity"
    if re.search(r"섹터|업종|cycle|사이클", lower):
        return "sector_cycle"
    return "macro"


def _infer_indicators(text: str) -> list[dict[str, object]]:
    lower = text.lower()
    out: list[dict[str, object]] = []

    def add(key: str, direction: str, weight: float = 1.0, description: str = "") -> None:
        if not any(item["indicator_key"] == key for item in out):
            out.append(
                {
                    "indicator_key": key,
                    "expected_direction": direction,
                    "weight": weight,
                    "lookback_days": 20,
                    "description": description,
                }
            )

    if re.search(r"환율|원달러|usdkrw", lower):
        add("usdkrw", "down", 1.0, "원화 안정 여부")
    if re.search(r"달러|dxy", lower):
        add("dxy", "down", 1.0, "달러 강세 완화 여부")
    if re.search(r"금리|yield|채권|fed|연준", lower):
        add("us_10y_yield", "down", 0.8, "장기금리 부담")
        add("us_real_10y_yield", "down", 0.8, "실질금리 부담")
    if re.search(r"변동성|공포|vix|리스크", lower):
        add("vix", "down", 1.0, "시장 스트레스 완화")
    if re.search(r"신용|스프레드|oas|하이일드", lower):
        add("hy_oas", "down", 1.0, "신용위험 완화")
    if re.search(r"외국인|수급|코스피", lower):
        add("foreign_flow_kospi_20d", "up", 1.2, "외국인 KOSPI 수급 확인")
    if re.search(r"수출|반도체|한국", lower):
        add("korea_export_yoy", "up", 1.0, "한국 수출 모멘텀")
    if re.search(r"물가|인플레|cpi", lower):
        add("cpi_yoy", "down", 0.8, "물가 압력 완화")
    if re.search(r"pce", lower):
        add("pce_yoy", "down", 0.8, "PCE 압력 완화")
    if re.search(r"경기|제조|pmi", lower):
        add("pmi", "up", 0.8, "제조업 경기 확인")
    if re.search(r"나스닥|ai|반도체|성장주|테크", lower):
        add("nasdaq_return_20d", "up", 1.0, "성장주 가격 확인")
    if re.search(r"코스피|한국주식|국내증시", lower):
        add("kospi_return_20d", "up", 1.0, "국내 지수 가격 확인")
    if not out:
        add("vix", "down", 0.7, "시장 위험도")
        add("dxy", "down", 0.7, "달러 유동성")
        add("foreign_flow_kospi_20d", "up", 1.0, "국내 수급 확인")
        add("kospi_return_20d", "up", 0.8, "가격 확인")
    return out


def main() -> None:
    args = _parse_args()
    path = Path(args.json_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    text_for_inference = "\n".join([str(payload.get("title") or ""), str(payload.get("raw_study_text") or "")])
    if not payload.get("thesis_type") or payload.get("thesis_type") == "auto":
        payload["thesis_type"] = _infer_thesis_type(text_for_inference)
    if not payload.get("indicators"):
        payload["indicators"] = _infer_indicators(text_for_inference)
    if not payload.get("watch_indicators"):
        payload["watch_indicators"] = [item["indicator_key"] for item in payload["indicators"]]
    if not payload.get("news_keywords"):
        payload["news_keywords"] = list(dict.fromkeys(re.findall(r"[A-Za-z]{2,}|[가-힣]{2,}", text_for_inference)))[:12]
    init_db(DB_PATH)
    with connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO investment_thesis (
                title, raw_study_text, summary, core_claim, thesis_type, horizon, status,
                initial_confidence, current_confidence, user_position_view,
                beneficiaries_json, victims_json, watch_indicators_json, indicator_directions_json,
                catalysts_json, invalidation_conditions_json, news_keywords_json,
                created_at, updated_at
            ) VALUES (
                :title, :raw_study_text, :summary, :core_claim, :thesis_type, :horizon, :status,
                :initial_confidence, :current_confidence, :user_position_view,
                :beneficiaries_json, :victims_json, :watch_indicators_json, :indicator_directions_json,
                :catalysts_json, :invalidation_conditions_json, :news_keywords_json,
                datetime('now'), datetime('now')
            );
            """,
            {
                "title": str(payload.get("title") or "Untitled Thesis"),
                "raw_study_text": str(payload.get("raw_study_text") or ""),
                "summary": payload.get("summary"),
                "core_claim": payload.get("core_claim") or payload.get("summary"),
                "thesis_type": payload.get("thesis_type") or "macro",
                "horizon": payload.get("horizon") or "medium",
                "status": payload.get("status") or "Active",
                "initial_confidence": float(payload.get("initial_confidence") or 50),
                "current_confidence": float(payload.get("current_confidence") or payload.get("initial_confidence") or 50),
                "user_position_view": payload.get("user_position_view") or "watch",
                "beneficiaries_json": _json_text(payload.get("beneficiaries")),
                "victims_json": _json_text(payload.get("victims")),
                "watch_indicators_json": _json_text(payload.get("watch_indicators")),
                "indicator_directions_json": _json_text(payload.get("indicator_directions")),
                "catalysts_json": _json_text(payload.get("catalysts")),
                "invalidation_conditions_json": _json_text(payload.get("invalidation_conditions")),
                "news_keywords_json": _json_text(payload.get("news_keywords")),
            },
        )
        thesis_id = int(cur.lastrowid)
        for item in payload.get("indicators", []) or []:
            if not isinstance(item, dict) or not item.get("indicator_key"):
                continue
            conn.execute(
                """
                INSERT INTO thesis_indicator_map (
                    thesis_id, indicator_key, expected_direction, weight, lookback_days,
                    trigger_type, threshold, description, created_at, updated_at
                ) VALUES (
                    :thesis_id, :indicator_key, :expected_direction, :weight, :lookback_days,
                    :trigger_type, :threshold, :description, datetime('now'), datetime('now')
                );
                """,
                {
                    "thesis_id": thesis_id,
                    "indicator_key": item.get("indicator_key"),
                    "expected_direction": item.get("expected_direction") or "neutral",
                    "weight": float(item.get("weight") or 1.0),
                    "lookback_days": int(item.get("lookback_days") or 20),
                    "trigger_type": item.get("trigger_type"),
                    "threshold": item.get("threshold"),
                    "description": item.get("description"),
                },
            )
        for item in payload.get("assets", []) or []:
            if not isinstance(item, dict):
                continue
            asset_id = str(item.get("asset_id") or item.get("ticker") or "").strip()
            if not asset_id:
                continue
            conn.execute(
                """
                INSERT INTO thesis_asset_map (
                    thesis_id, asset_type, asset_id, ticker, relation_type, sensitivity,
                    confidence, note, created_at, updated_at
                ) VALUES (
                    :thesis_id, :asset_type, :asset_id, :ticker, :relation_type, :sensitivity,
                    :confidence, :note, datetime('now'), datetime('now')
                );
                """,
                {
                    "thesis_id": thesis_id,
                    "asset_type": item.get("asset_type") or "stock",
                    "asset_id": asset_id,
                    "ticker": str(item.get("ticker") or asset_id).upper(),
                    "relation_type": item.get("relation_type") or "watchlist",
                    "sensitivity": float(item.get("sensitivity") or 1.0),
                    "confidence": float(item.get("confidence") or 50),
                    "note": item.get("note"),
                },
            )
    print(f"thesis_imported id={thesis_id} title={payload.get('title') or 'Untitled Thesis'}")


if __name__ == "__main__":
    main()
