"""Refreshable supplier financials, news metadata and macro observations.

Raw DART account rows are retained for audit. News never changes a score or a
verified relationship. A failed refresh preserves last-good data explicitly.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import json
import math
from pathlib import Path
import re
import sqlite3

from committee.industry_cycle.supply_chain import ROOT, load_supply_chain_dashboard_data

SNAPSHOT_PATH = ROOT / "data/supply_chain_monitor.json"
EVENTS = {
    "수주·투자": ["수주", "계약", "증설", "투자", "발주", "CAPEX"],
    "실적·수요": ["실적", "매출", "가동률", "생산", "재고", "수요", "출하"],
    "정책·위험": ["관세", "규제", "제재", "취소", "중단", "파업", "리콜"],
    "원가·금융": ["금리", "환율", "유가", "구리", "원가", "가격", "스프레드"],
}
MACRO_QUERIES = {
    "rates_fx": '금리 환율 연준 한국은행 when:28d',
    "energy_cost": '유가 천연가스 구리 원자재 when:28d',
    "trade_policy": '관세 수출규제 제조업 when:28d',
}
INDICATOR_LABELS = dict(zip(
    "us_industrial_production_index us_manufacturers_new_orders us_manufacturers_inventories us_durable_goods_orders us_computer_electronics_orders us_computer_electronics_unfilled_orders us_computer_electronics_production us_semiconductor_production us_semiconductor_ppi us_data_hosting_revenue us_software_publishers_revenue us_machinery_orders us_machinery_production us_electrical_equipment_orders us_electrical_equipment_production us_auto_sales us_auto_production us_auto_inventories us_motor_vehicle_parts_production us_transportation_equipment_orders us_raw_steel_production us_steel_orders us_primary_metals_production us_chemical_production global_copper_price global_aluminum_price us_wti_oil_price us_brent_oil_price us_refinery_output us_refinery_ppi us_henry_hub_gas_price us_electric_gas_utilities_production global_uranium_price us_nuclear_power_production us_freight_transportation_index us_deep_sea_freight_ppi us_transport_warehouse_employment us_air_passenger_miles us_air_load_factor us_total_construction_spending us_housing_permits us_housing_starts us_retail_sales us_inventory_sales_ratio us_bank_loans us_bank_delinquency us_yield_curve_10y2y us_broker_margin_receivables us_m2_money_stock us_pharma_production us_healthcare_revenue us_healthcare_employment".split(),
    "미국 산업생산|미국 제조업 신규주문|미국 제조업 재고|미국 내구재 주문|미국 컴퓨터·전자제품 주문|미국 컴퓨터·전자제품 미출하주문|미국 컴퓨터·전자제품 생산|미국 반도체·전자부품 생산|미국 반도체 생산자물가|미국 데이터처리·호스팅 매출|미국 소프트웨어 매출|미국 기계 신규주문|미국 기계 생산|미국 전기장비 주문|미국 전기장비 생산|미국 자동차 판매|미국 자동차 생산|미국 자동차 재고|미국 자동차·부품 생산|미국 운송장비 주문|미국 조강 생산|미국 철강 주문|미국 1차 금속 생산|미국 화학 생산|글로벌 구리 가격|글로벌 알루미늄 가격|WTI 유가|브렌트 유가|미국 정유 생산|미국 정유 생산자물가|미국 헨리허브 가스 가격|미국 전기·가스 유틸리티 생산|글로벌 우라늄 가격|미국 원자력 발전|미국 화물운송 지수|미국 외항운송 생산자물가|미국 운수·창고업 고용|미국 유상 여객마일|미국 항공 탑승률|미국 건설 지출|미국 주택 건축허가|미국 주택 착공|미국 소매판매|미국 재고판매 비율|미국 은행 대출|미국 은행 연체율|미국 장단기 금리차|미국 증권사 고객 미수금|미국 M2 통화량|미국 의약품 생산|미국 외래의료 매출|미국 헬스케어 고용".split("|")
))


def timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.replace(tzinfo=timezone.utc) if result.tzinfo is None else result.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def number(value) -> float | None:
    try:
        n = float(str(value).replace(",", ""))
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None


def financial_periods(today: date) -> list[tuple[str, str]]:
    result = []
    for year in [today.year, today.year - 1]:
        for month, day, report in [(12, 31, "11011"), (9, 30, "11014"), (6, 30, "11012"), (3, 31, "11013")]:
            if date(year, month, day) < today:
                result.append((str(year), report))
    return result[:4]


def normalize_financials(rows: list[dict], *, year: str, report: str, now: datetime) -> dict:
    basis = "CFS" if any(r.get("fs_div") == "CFS" for r in rows) else "OFS"
    rows = [r for r in rows if r.get("fs_div") == basis]
    metrics = []
    seen = set()
    for r in rows:
        key = r.get("account_nm", "")
        if key in seen:
            continue
        seen.add(key)
        if key not in {"매출액", "영업이익", "영업이익(손실)", "당기순이익", "당기순이익(손실)", "자산총계", "부채총계", "자본총계"}:
            continue
        flow = r.get("sj_div") == "IS"
        cumulative = flow and number(r.get("thstrm_add_amount")) is not None
        current = number(r.get("thstrm_add_amount") if cumulative else r.get("thstrm_amount"))
        prior = number(r.get("frmtrm_add_amount") if cumulative else r.get("frmtrm_amount"))
        if flow and report in {"11012", "11014"} and not cumulative:
            # A standalone quarter must never be labeled half-year/YTD.
            current = prior = None
        metrics.append({"name": key, "value": current, "prior": prior, "unit": r.get("currency", "KRW"),
                        "comparison": "전년 동기 누적" if flow else "전기말",
                        "period_basis": "누적" if flow else "기말",
                        "missing_cumulative":flow and report in {"11012","11014"} and not cumulative,
                        "change_pct": round((current/prior-1)*100, 2) if current is not None and prior is not None and prior > 0 else None,
                        "negative_base_note": prior is not None and prior <= 0})
    receipt = next((r.get("rcept_no") for r in rows if r.get("rcept_no")), None)
    return {"status": "ok" if metrics else "empty", "year": year, "report_code": report, "basis": basis,
            "period": year + " " + {"11011":"연간", "11014":"3분기 누적", "11012":"반기 누적", "11013":"1분기"}[report],
            "published_at": f"{receipt[:4]}-{receipt[4:6]}-{receipt[6:8]}" if receipt else None,
            "known_at": now.isoformat(), "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receipt}" if receipt else None,
            "metrics": metrics, "raw_accounts": rows}


def fetch_financials(corp_code: str | None, now: datetime) -> dict:
    from committee.tools.dart_client import _request_dart_json
    if not corp_code:
        return {"status": "missing_corp_code"}
    try:
        for year, report in financial_periods(now.date()):
            payload = _request_dart_json("fnlttSinglAcnt.json", {"corp_code":corp_code,"bsns_year":year,"reprt_code":report}, timeout=12)
            rows = payload.get("list", [])
            if rows:
                return normalize_financials(rows, year=year, report=report, now=now)
        return {"status":"no_filing"}
    except Exception as exc:
        # requests exceptions may contain API credentials in their URL.
        return {"status":"error", "error_type":type(exc).__name__}


def normalize_news(items: list[dict], *, now: datetime, days: int = 28, limit: int = 12) -> list[dict]:
    result = []
    titles = set()
    links = set()
    for item in sorted(items, key=lambda x: x.get("published_at") or "", reverse=True):
        published = timestamp(item.get("published_at"))
        if published is None or not now - timedelta(days=days) <= published <= now:
            continue
        link = item.get("link", "")
        title_key = re.sub(r"\W", "", item.get("title", "").rsplit(" - ", 1)[0]).lower()
        if not link.startswith(("https://", "http://")) or not title_key or title_key in titles or link in links:
            continue
        titles.add(title_key); links.add(link)
        result.append({**item, "published_at":published.isoformat(), "tags":[k for k,terms in EVENTS.items() if any(t.lower() in item["title"].lower() for t in terms)],
                       "evidence_level":"headline_only"})
        if len(result) >= limit:
            break
    return result


def fetch_news(query: str, now: datetime, required_names: list[str] | None = None, exclusions: list[str] | None = None) -> dict:
    from committee.tools.news_digest import fetch_google_news_items
    try:
        rows = fetch_google_news_items(query, limit=35, timeout=10)
        items = [{"title":title,"link":link,"published_at":dt.isoformat() if dt else None,
                  "source":title.rsplit(" - ",1)[-1], "first_seen_at":now.isoformat(), "last_seen_at":now.isoformat()}
                 for title,link,dt in rows if (not required_names or any(n.replace(" ","").lower() in title.replace(" ","").lower() for n in required_names))
                 and not any(term in title for term in (exclusions or []))]
        result = normalize_news(items, now=now)
        return {"status":"ok" if result else "empty", "query":query, "items":result}
    except Exception as exc:
        return {"status":"error", "error_type":type(exc).__name__, "query":query, "items":[]}


def merge_news(previous: list[dict], current: list[dict], now: datetime) -> list[dict]:
    old = {x["link"]: x for x in previous}
    for item in current:
        old[item["link"]] = {**item, "first_seen_at":old.get(item["link"], {}).get("first_seen_at", item.get("first_seen_at", now.isoformat()))}
    return normalize_news(list(old.values()), now=now)


def macro_context(conn: sqlite3.Connection, now: datetime) -> dict:
    config = json.loads((ROOT / "config/industry_indicators.json").read_text(encoding="utf-8"))
    result = {}
    for ind in config["indicators"]:
        if not ind.get("active"):
            continue
        candidates = conn.execute("SELECT observed_at,value,published_at,known_at,vintage_at,created_at FROM indicator_observation WHERE indicator_id=? AND value IS NOT NULL ORDER BY observed_at DESC,COALESCE(vintage_at,known_at) DESC", (ind["indicator_id"],)).fetchall()
        history, seen = [], set()
        for row in candidates:
            r = dict(row)
            observed, known = timestamp(r["observed_at"]), timestamp(r["known_at"] or r["published_at"])
            if not observed or not known or observed > now or known > now or r["observed_at"] in seen:
                continue
            if number(r["value"]) is None:
                continue
            seen.add(r["observed_at"]); history.append(r)
            if len(history) == 13:
                break
        latest = history[0] if history else None
        age = (now.date()-date.fromisoformat(latest["observed_at"][:10])).days if latest else None
        threshold = {"daily":10,"weekly":21,"monthly":100,"quarterly":200}.get(ind["frequency"],100)
        previous = history[1] if len(history)>1 else None
        change = latest["value"]-previous["value"] if previous else None
        result[ind["indicator_id"]] = {**ind, "source_url":f"https://fred.stlouisfed.org/series/{ind['series_id']}",
            "name":INDICATOR_LABELS.get(ind["indicator_id"], ind["description"]),
            "display_unit":"%" if ind["transform"] in {"yoy_pct","mom_pct"} else ind["unit"],
            "change_unit":"%p" if ind["transform"] in {"yoy_pct","mom_pct"} or ind["unit"]=="percent" else ind["unit"],
            "value_label":{"yoy_pct":"전년 동기 대비", "mom_pct":"직전 기간 대비", "level":"수준"}[ind["transform"]],
            "latest":latest,"history":list(reversed(history)),"change":change,"age_days":age,
            "status":"missing" if not latest else "stale" if age>threshold else "available",
            "interpretation":"미국·글로벌 산업 대리지표. 한국 공급사의 직접 수요를 증명하지 않습니다. 전년비의 전기 대비 변화는 %p입니다. 날짜는 기존 수집 DB 기록 기준입니다."}
    by_industry = {}
    for m in config["industry_indicator_mappings"]:
        if m["indicator_id"] not in result or m.get("valid_from", "0001-01-01") > now.date().isoformat() or (m.get("valid_to") and m["valid_to"] < now.date().isoformat()):
            continue
        by_industry.setdefault(m["industry_id"], []).append(m["indicator_id"])
    common = []
    for field,label,unit,meaning in [
        ("usdkrw","달러/원 환율","원","수출 환산매출과 수입 원가에 서로 다른 영향"),
        ("us10y","미국 10년 국채금리","%","설비투자 금융비용·할인율의 배경"),
        ("oil_wti","WTI 유가","USD/bbl","에너지·운송 비용; 정유마진과는 다른 지표"),
        ("hy_oas","미국 하이일드 스프레드","%","기업 자금조달·신용 위험의 배경")]:
        rows=conn.execute(f"SELECT date,{field} AS value,data_date,published_at,observed_at FROM daily_macro WHERE {field} IS NOT NULL AND date<=? ORDER BY date DESC LIMIT 12",(now.date().isoformat(),)).fetchall()
        history=[dict(r) for r in rows if not r["published_at"] or (timestamp(r["published_at"]) and timestamp(r["published_at"])<=now)]
        for r in history:r["observed_at"] = r["data_date"] or r["date"]
        latest=history[0] if history else None
        age=(now.date()-date.fromisoformat(latest["observed_at"][:10])).days if latest else None
        common.append({"indicator_id":field,"name":label,"display_unit":unit,"latest":latest,"history":list(reversed(history)),
                       "status":"missing" if not latest else "stale" if age>10 else "available","interpretation":meaning,
                       "source_label":"기존 daily_macro 저장값; 지표별 원출처·개별 발표시각 미보존","age_days":age})
    return {"indicators":result,"by_industry":by_industry,"common":common}


def build_monitor(*, now: datetime | None = None, db_path: Path = ROOT / "data/investment.db", previous: dict | None = None, network_news: bool = True, network_financials: bool = True) -> dict:
    now = now or datetime.now(timezone.utc)
    previous = previous or {}
    catalog = load_supply_chain_dashboard_data()
    conn = sqlite3.connect(db_path.resolve().as_uri()+"?mode=ro",uri=True)
    conn.row_factory = sqlite3.Row
    codes = {r["stock_code"]:r["dart_corp_code"] for r in conn.execute("SELECT stock_code,dart_corp_code FROM dart_company_code")}
    macro = macro_context(conn, now)
    industry_news = {}
    since = (now-timedelta(days=28)).isoformat()
    for i in catalog["industries"]:
        rows = [dict(r) for r in conn.execute("SELECT title,link,source,published_at,collected_at AS first_seen_at FROM industry_news WHERE industry_id=? AND published_at>=?",(i["industry_id"],since))]
        industry_news[i["industry_id"]] = normalize_news(rows,now=now,limit=6)
    local_news = {c["company_id"]:[dict(r) for r in conn.execute("SELECT title,link,source,published_at,collected_at AS first_seen_at FROM stock_news WHERE ticker=? AND published_at>=?",(c["ticker"],since))] for c in catalog["companies"]}
    conn.close()
    def collect(c):
        cid = c["company_id"]
        aliases = [c["name"], *c.get("news_aliases",[])]
        query = '('+' OR '.join('"'+s+'"' for s in aliases)+') (수주 OR 실적 OR 공급 OR 계약 OR 가동률 OR 증설 OR 재고) -상한가 -관련주 when:28d'
        exclusions=c.get("news_exclusions",[])
        query += ' '+ ' '.join('-"'+word+'"' for word in exclusions)
        news = fetch_news(query,now,aliases,exclusions) if network_news else {"status":"not_requested","items":[]}
        old = previous.get("companies",{}).get(cid,{})
        financials = fetch_financials(codes.get(c["ticker"]),now) if network_financials else {"status":"not_requested"}
        attempt = financials["status"]
        if attempt != "ok" and old.get("financials",{}).get("metrics"):
            financials = {**old["financials"],"status":"cached","last_attempt_status":attempt}
        return cid, {"name":c["name"],"ticker":c["ticker"],"financials":financials,
            "news_status":news["status"],"query":query,
            "news":[n for n in merge_news(old.get("news",[]),local_news[cid]+news["items"],now) if not any(x in n["title"] for x in exclusions)]}
    with ThreadPoolExecutor(max_workers=4) as pool:
        companies = dict(pool.map(collect,catalog["companies"]))
    global_news = {}
    for topic,query in MACRO_QUERIES.items():
        current = fetch_news(query,now) if network_news else {"status":"not_requested","items":[]}
        current["items"] = merge_news(previous.get("macro_news",{}).get(topic,{}).get("items",[]),current["items"],now)
        global_news[topic] = current
    changes=[]
    for cid, company in companies.items():
        old=previous.get("companies",{}).get(cid,{})
        old_links={n["link"] for n in old.get("news",[])}
        count=sum(n["link"] not in old_links for n in company["news"])
        if count:changes.append({"company_id":cid,"kind":"news","label":company["name"]+f" 새로 확보한 기사 {count}건"})
        if company["financials"].get("source_url") and company["financials"].get("source_url")!=old.get("financials",{}).get("source_url"):
            changes.append({"company_id":cid,"kind":"filing","label":company["name"]+" 재무 공시 갱신"})
    for iid, indicator in macro["indicators"].items():
        old=previous.get("macro",{}).get("indicators",{}).get(iid,{}).get("latest")
        latest=indicator["latest"]
        if latest and (not old or (latest["observed_at"],latest["value"])!=(old["observed_at"],old["value"])):
            changes.append({"indicator_id":iid,"kind":"macro","label":indicator["name"]+" 관측값 갱신"})
    return {"schema_version":1,"generated_at":now.isoformat(),"previous_generated_at":previous.get("generated_at"),"changes":changes,"window_days":28,"companies":companies,
        "industry_news":industry_news,"macro":macro,"macro_news":global_news,
        "collection_note":"기업 뉴스는 기업명 검색·직접 언급 기준, 산업 뉴스는 기존 산업 수집 자료입니다. 제목만 수집하며 사건의 사실·호재·악재를 확정하지 않습니다.",
        "summary":{"companies":len(companies),"financials":sum(bool(v["financials"].get("metrics")) for v in companies.values()),
                   "company_news":sum(len(v["news"]) for v in companies.values()),"indicators":sum(v["latest"] is not None for v in macro["indicators"].values()),
                   "news_errors":sum(v["news_status"]=="error" for v in companies.values()),
                   "financial_errors":sum(v["financials"]["status"]=="error" or v["financials"].get("last_attempt_status")=="error" for v in companies.values())}}


def load_monitor(path: Path = SNAPSHOT_PATH) -> dict:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("unsupported monitor schema")
    return payload


def save_monitor(payload: dict, path: Path = SNAPSHOT_PATH) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)+"\n"
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(serialized,encoding="utf-8");tmp.replace(path)
    stamp = datetime.fromisoformat(payload["generated_at"])
    archive = ROOT / "runs" / stamp.date().isoformat() / "supply_chain" / (stamp.strftime("%H%M%S%f")+".json")
    archive.parent.mkdir(parents=True,exist_ok=True)
    archive.write_text(serialized,encoding="utf-8")
