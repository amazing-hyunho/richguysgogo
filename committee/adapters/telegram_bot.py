from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

from committee.core.database import (
    get_last_n_market_flow,
    get_latest_stock_consensus,
    get_stock_news,
    safe_upsert_stock_news,
)
from committee.core.strategy_store import load_latest_strategy, update_strategy
from committee.core.stock_watchlist import add_stock, get_stocks, remove_stock
from committee.tools.stock_consensus_provider import fetch_stock_consensus
from committee.tools.stock_news import fetch_stock_news

ROOT_DIR = Path(__file__).resolve().parents[2]


class TelegramQABot:
    def __init__(self, token: str, allowed_chat_ids: set[str] | None = None, timeout_sec: int = 25) -> None:
        self.token = token
        self.timeout_sec = timeout_sec
        self.allowed_chat_ids = allowed_chat_ids or set()
        self.base_url = f"https://api.telegram.org/bot{token}"

    def poll_forever(self) -> None:
        print("[run_bot] polling started")
        offset = None
        while True:
            try:
                updates = self._get_updates(offset)
                for update in updates:
                    offset = update.get("update_id", 0) + 1
                    self._handle_update(update)
            except KeyboardInterrupt:
                print("[run_bot] stopped by keyboard interrupt")
                return
            except Exception as exc:  # noqa: BLE001
                print(f"[run_bot] polling_error: {exc}")
                time.sleep(2)

    def _get_updates(self, offset: int | None) -> list[dict]:
        payload = {"timeout": self.timeout_sec}
        if offset is not None:
            payload["offset"] = offset
        response = requests.get(f"{self.base_url}/getUpdates", params=payload, timeout=self.timeout_sec + 10)
        response.raise_for_status()
        body = response.json()
        if not body.get("ok"):
            raise RuntimeError(f"telegram_get_updates_failed: {body}")
        result = body.get("result", [])
        return result if isinstance(result, list) else []

    def _handle_update(self, update: dict) -> None:
        message = update.get("message") or update.get("edited_message")
        if not isinstance(message, dict):
            return
        text = message.get("text")
        if not isinstance(text, str):
            return

        chat = message.get("chat") or {}
        chat_id = str(chat.get("id", "")).strip()
        if not chat_id:
            return
        if self.allowed_chat_ids and chat_id not in self.allowed_chat_ids:
            return

        reply = answer_for_message(text)
        self._send_message(chat_id, reply)

    def _send_message(self, chat_id: str, text: str) -> None:
        for part in _split_message(text, 3500):
            payload = {"chat_id": chat_id, "text": part}
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=15)
            if response.status_code >= 300:
                print(f"telegram_send_failed[{response.status_code}]: {response.text}")


def answer_for_message(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "질문을 입력해 주세요."

    context = _load_latest_context()
    if stripped.startswith("/strategy"):
        return _handle_strategy_command(stripped, context)
    if stripped.startswith("/flow"):
        return _handle_flow_command(stripped)
    if stripped.startswith("/consensus"):
        return _handle_consensus_command(stripped)
    if stripped.startswith("/stock"):
        return _handle_stock_command(stripped)
    if _is_foreign_flow_trend_question(stripped):
        return _format_foreign_flow_trend()

    return _build_answer_from_context(stripped, context)


def _handle_flow_command(command: str) -> str:
    if command in {"/flow", "/flow trend"}:
        return _format_foreign_flow_trend()
    return "지원 커맨드: /flow trend"


def _handle_consensus_command(command: str) -> str:
    """Handle /consensus [TICKER] command.

    Examples
    --------
    /consensus AAPL      → fetch live consensus for AAPL
    /consensus 005930    → fetch live consensus for 삼성전자
    /consensus           → show help
    """
    parts = command.strip().split()
    if len(parts) < 2:
        return (
            "종목 컨센서스 조회: /consensus TICKER\n"
            "예) /consensus AAPL\n"
            "예) /consensus 005930 (삼성전자)\n"
            "예) /consensus NVDA\n\n"
            "DB에 저장된 데이터를 먼저 확인하고, 없으면 실시간 조회합니다."
        )

    ticker = parts[1].strip().upper()

    # First try DB (fast, no network)
    stored = None
    try:
        stored = get_latest_stock_consensus(ticker)
    except Exception:
        pass

    # Live fetch (always do for freshness)
    live = None
    try:
        live = fetch_stock_consensus(ticker)
    except Exception as exc:
        live = None
        print(f"[telegram] consensus_live_failed[{ticker}]: {exc}")

    result = live or stored
    if result is None:
        return f"{ticker} 컨센서스 데이터를 가져올 수 없습니다."

    return _format_consensus(result, stored_date=stored.get("date") if stored else None)


def _handle_stock_command(command: str) -> str:
    """Handle /stock add|remove|list for the AI stock-analysis watchlist.

    Examples
    --------
    /stock add NVDA                  → 시장·회사명 자동 판별 후 등록 + 즉시 뉴스 수집
    /stock add 005930 삼성전자 KR     → 이름/시장 직접 지정
    /stock remove NVDA               → 등록 해제
    /stock list                      → 현재 워치리스트
    """
    parts = command.strip().split()
    sub = parts[1].strip().lower() if len(parts) >= 2 else ""

    if sub == "list":
        return _format_stock_list()

    if sub == "remove":
        if len(parts) < 3:
            return "사용법: /stock remove TICKER (예: /stock remove NVDA)"
        ok, msg = remove_stock(parts[2])
        if not ok:
            return "⚠️ " + msg
        build_ok, build_msg = _rebuild_dashboard()
        icon = "✅" if build_ok else "⚠️"
        return f"✅ {msg}\n{icon} {build_msg}"

    if sub == "add":
        if len(parts) < 3:
            return "사용법: /stock add TICKER [회사명] [KR|US]\n예) /stock add NVDA\n예) /stock add 005930 삼성전자 KR"
        ticker = parts[2]
        name = None
        market = None
        # 나머지 토큰: 마지막이 KR/US면 시장, 그 앞은 이름으로 해석.
        rest = parts[3:]
        if rest and rest[-1].upper() in {"KR", "US"}:
            market = rest[-1].upper()
            rest = rest[:-1]
        if rest:
            name = " ".join(rest)
        added, stock, msg = add_stock(ticker, name=name, market=market)
        if not added:
            return "⚠️ " + msg
        lines = [f"✅ {msg}"]

        # 등록 즉시 뉴스 수집.
        try:
            items = fetch_stock_news(
                ticker=stock["ticker"], name=stock["name"], market=stock["market"], limit=15
            )
            for it in items:
                safe_upsert_stock_news(
                    ticker=it.ticker,
                    link=it.link,
                    title=it.title,
                    published_at=it.published_at,
                    source=it.source,
                    company_name=it.company_name,
                    market=it.market,
                )
            lines.append(f"📰 뉴스 {len(items)}건 수집 완료.")
        except Exception as exc:  # noqa: BLE001
            lines.append(f"⚠️ 뉴스 수집은 실패했습니다(나중에 sync로 재시도): {exc}")

        build_ok, build_msg = _rebuild_dashboard()
        lines.append(("✅ " if build_ok else "⚠️ ") + build_msg)
        return "\n".join(lines)

    return (
        "AI 종목분석 워치리스트 명령\n"
        "/stock add TICKER [회사명] [KR|US] — 등록 + 즉시 뉴스 수집 + 대시보드 빌드\n"
        "/stock remove TICKER — 등록 해제 + 대시보드 빌드\n"
        "/stock list — 등록 목록"
    )


def _rebuild_dashboard(timeout_sec: int = 180) -> tuple[bool, str]:
    """Run the static dashboard build so Telegram watchlist changes show up."""
    script = ROOT_DIR / "scripts" / "build_dashboard.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"대시보드 빌드 시간초과({timeout_sec}초)."
    except Exception as exc:  # noqa: BLE001
        return False, f"대시보드 빌드 실행 실패: {exc}"

    if result.returncode == 0:
        return True, "대시보드 빌드 완료."

    detail = (result.stderr or result.stdout or "").strip().replace("\n", " ")
    if len(detail) > 500:
        detail = detail[:500] + "..."
    return False, f"대시보드 빌드 실패(exit={result.returncode}): {detail or 'no output'}"


def _format_stock_list() -> str:
    stocks = get_stocks()
    if not stocks:
        return "등록된 종목이 없습니다. /stock add TICKER 로 추가하세요."
    lines = ["📈 AI 종목분석 워치리스트"]
    for s in stocks:
        ticker = str(s.get("ticker", "?"))
        name = str(s.get("name", ""))
        market = str(s.get("market", ""))
        try:
            cnt = len(get_stock_news(ticker, limit=999))
        except Exception:
            cnt = 0
        lines.append(f"- {ticker} ({name}/{market}) · 뉴스 {cnt}건")
    return "\n".join(lines)


def _format_consensus(r: dict, stored_date: str | None = None) -> str:
    ticker = r.get("ticker", "?")
    company = r.get("company_name") or ""
    market = r.get("market", "?")
    cur = r.get("currency") or ""
    source = r.get("source") or "unknown"

    def fp(v: float | None) -> str:
        if v is None:
            return "N/A"
        if cur == "KRW":
            return f"{v:,.0f}원"
        if cur == "USD":
            return f"${v:,.2f}"
        return f"{v:,.2f}"

    def frec(key: str | None, mean: float | None) -> str:
        parts_r = []
        if key:
            parts_r.append(key.upper())
        if mean is not None:
            label = {1: "강매수", 2: "매수", 3: "보유", 4: "약보유", 5: "매도"}.get(
                round(mean), f"{mean:.1f}"
            )
            parts_r.append(f"({label})")
        return " ".join(parts_r) if parts_r else "N/A"

    lines = [f"📊 {ticker} 애널리스트 컨센서스"]
    if company:
        lines.append(f"기업명: {company} ({market})")

    cur_price = r.get("current_price")
    if cur_price is not None:
        lines.append(f"현재가: {fp(cur_price)}")

    tp_mean = fp(r.get("target_mean_price"))
    tp_hi = fp(r.get("target_high_price"))
    tp_lo = fp(r.get("target_low_price"))
    lines.append(f"목표주가(평균): {tp_mean}")
    if r.get("target_high_price") or r.get("target_low_price"):
        lines.append(f"목표주가(범위): {tp_lo} ~ {tp_hi}")

    # 현재가 대비 괴리율
    if cur_price and r.get("target_mean_price") and cur_price > 0:
        upside = (r["target_mean_price"] / cur_price - 1) * 100
        sign = "▲" if upside >= 0 else "▼"
        lines.append(f"괴리율(목표 vs 현재): {sign}{abs(upside):.1f}%")

    lines.append(f"투자의견: {frec(r.get('recommendation_key'), r.get('recommendation_mean'))}")

    analysts = r.get("num_analysts")
    if analysts is not None:
        lines.append(f"참여 애널리스트: {analysts}명")

    fwd_eps = r.get("forward_eps")
    fwd_pe = r.get("forward_pe")
    if fwd_eps is not None:
        lines.append(f"Forward EPS: {fp(fwd_eps)}")
    if fwd_pe is not None:
        lines.append(f"Forward PER: {fwd_pe:.1f}x")

    lines.append(f"데이터 출처: {source}")
    if stored_date:
        lines.append(f"DB 저장일: {stored_date}")

    return "\n".join(lines)


def _is_foreign_flow_trend_question(text: str) -> bool:
    normalized = text.replace(" ", "")
    keywords = ("외국인", "순매수", "추이")
    return all(keyword in normalized for keyword in keywords)


def _format_foreign_flow_trend(limit: int = 10) -> str:
    try:
        rows = get_last_n_market_flow(limit)
    except Exception as exc:  # noqa: BLE001
        return f"외국인 순매수 추이 조회 실패(안전 fallback): {exc}"

    valid_rows = [row for row in rows if row.get("foreign_net") is not None]
    if not valid_rows:
        return "외국인 순매수 추이 데이터가 아직 없습니다. (market_flow_daily 비어있음)"

    ordered = list(reversed(valid_rows))
    latest = ordered[-1]
    latest_value = float(latest.get("foreign_net", 0.0))

    lines = [
        f"외국인 순매수 추이 (최근 {len(ordered)}영업일, 단위: 억원)",
        f"최신: {latest.get('date', 'n/a')} {latest_value:+,.0f}억",
    ]

    for row in ordered:
        value = float(row.get("foreign_net", 0.0))
        lines.append(f"- {row.get('date', 'n/a')}: {value:+,.0f}억")

    return "\n".join(lines)


def _handle_strategy_command(command: str, context: dict) -> str:
    if command == "/strategy show":
        try:
            version, strategy = load_latest_strategy()
        except Exception as exc:  # noqa: BLE001
            return f"전략 조회 실패(안전 fallback): {exc}"

        if strategy:
            return _format_strategy(strategy=strategy, header=f"전략 버전 v{version}")

        baseline = _derive_strategy_baseline(context)
        if baseline:
            return _format_strategy(
                strategy=baseline,
                header="저장된 전략이 아직 없습니다. 최신 위원회 결과 기반 기본 전략입니다.",
                footer="원하면 /strategy set KEY=VALUE 로 확정 저장하세요.",
            )
        return "저장된 전략이 아직 없습니다. 예: /strategy set RISK=CAUTION"

    if command.startswith("/strategy set"):
        payload = command.replace("/strategy set", "", 1).strip()
        parsed = _parse_strategy_changes(payload)
        if not parsed:
            return "형식 오류: /strategy set KEY=VALUE (예: /strategy set RISK=CAUTION)"
        try:
            version, strategy = update_strategy(parsed, source="telegram")
        except Exception as exc:  # noqa: BLE001
            return f"전략 저장 실패(안전 fallback): {exc}"
        return _format_strategy(strategy=strategy, header=f"전략 저장 완료 v{version}")

    return "지원 커맨드: /strategy set KEY=VALUE, /strategy show"


def _parse_strategy_changes(payload: str) -> dict[str, str]:
    changes: dict[str, str] = {}
    for token in payload.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        k = re.sub(r"[^A-Za-z0-9_\-]", "", key.upper()).strip()
        v = value.strip()
        if not k or not v:
            continue
        changes[k] = v
    return changes


def _format_strategy(strategy: dict[str, str], header: str, footer: str = "") -> str:
    lines = [header]
    for key in sorted(strategy.keys()):
        lines.append(f"- {key}={strategy[key]}")
    if footer:
        lines.append(footer)
    return "\n".join(lines)


def _derive_strategy_baseline(context: dict) -> dict[str, str]:
    committee = context.get("committee") if isinstance(context, dict) else {}
    if not isinstance(committee, dict):
        return {}

    strategy: dict[str, str] = {}
    guidance = committee.get("ops_guidance")
    if isinstance(guidance, list):
        levels = [str(item.get("level", "")).upper() for item in guidance if isinstance(item, dict)]
        if "AVOID" in levels:
            strategy["RISK"] = "DEFENSIVE"
        elif "CAUTION" in levels:
            strategy["RISK"] = "CAUTION"
        elif "OK" in levels:
            strategy["RISK"] = "OK"

    consensus = str(committee.get("consensus", "")).lower()
    if "defensive" in consensus or "risk exposure" in consensus:
        strategy.setdefault("BIAS", "RISK_OFF")
    elif "neutral" in consensus:
        strategy.setdefault("BIAS", "NEUTRAL")

    run_name = str(context.get("run", "")).strip()
    if run_name and run_name != "n/a":
        strategy["SOURCE_RUN"] = run_name
    return strategy


def _load_latest_context() -> dict:
    latest = _latest_run_dir(ROOT_DIR / "runs")
    if latest is None:
        return {
            "run": "n/a",
            "snapshot": {},
            "committee": {},
            "report_excerpt": "리포트 없음",
        }

    snapshot = _safe_load_json(latest / "snapshot.json")
    committee = _safe_load_json(latest / "committee_result.json")
    report_excerpt = _safe_load_text(latest / "report.md", 1200)
    return {
        "run": latest.name,
        "snapshot": snapshot if isinstance(snapshot, dict) else {},
        "committee": committee if isinstance(committee, dict) else {},
        "report_excerpt": report_excerpt,
    }


def _build_answer_from_context(question: str, context: dict) -> str:
    run = context.get("run", "n/a")
    snapshot = context.get("snapshot") or {}
    committee = context.get("committee") or {}
    report_excerpt = context.get("report_excerpt", "")

    market_note = ((snapshot.get("market_summary") or {}).get("note")) if isinstance(snapshot, dict) else None
    consensus = committee.get("consensus") if isinstance(committee, dict) else None
    guidance = committee.get("ops_guidance") if isinstance(committee, dict) else []

    lines = [f"기준 데이터: runs/{run}/snapshot.json, report.md, committee_result.json"]
    lines.append(f"질문: {question}")

    if "전략" in question:
        try:
            version, strategy = load_latest_strategy()
            if strategy:
                lines.append(f"현재 전략(v{version}): " + ", ".join([f"{k}={v}" for k, v in sorted(strategy.items())]))
            else:
                baseline = _derive_strategy_baseline(context)
                if baseline:
                    lines.append("저장 전략 없음. 기본 전략: " + ", ".join([f"{k}={v}" for k, v in sorted(baseline.items())]))
                else:
                    lines.append("현재 저장된 전략 없음 (/strategy set 으로 등록 가능)")
        except Exception:
            lines.append("현재 전략 조회 실패 (fallback)")

    if consensus:
        lines.append(f"위원회 합의: {consensus}")
    else:
        lines.append("위원회 합의: n/a (fallback)")

    if market_note:
        lines.append(f"시장 요약: {market_note}")

    if isinstance(guidance, list) and guidance:
        top = []
        for item in guidance[:3]:
            if not isinstance(item, dict):
                continue
            level = item.get("level", "N/A")
            text = item.get("text", "")
            top.append(f"[{level}] {text}")
        if top:
            lines.append("운영 가이드: " + " / ".join(top))

    report_line = report_excerpt.strip().splitlines()
    if report_line:
        lines.append("리포트 발췌: " + report_line[0][:240])

    lines.append("※ 스키마/파일 이상 시 안전 fallback 데이터를 사용합니다.")
    return "\n".join(lines)


def _latest_run_dir(runs_dir: Path) -> Path | None:
    if not runs_dir.exists():
        return None
    dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda path: path.name)[-1]


def _safe_load_json(path: Path) -> dict | list:
    try:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"[run_bot] json_load_failed[{path.name}]: {exc}")
        return {}


def _safe_load_text(path: Path, max_len: int) -> str:
    try:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")[:max_len]
    except Exception as exc:  # noqa: BLE001
        print(f"[run_bot] text_load_failed[{path.name}]: {exc}")
        return ""


def _split_message(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]

    parts: list[str] = []
    current = ""
    for line in text.splitlines():
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > max_len:
            if current:
                parts.append(current)
            current = line
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts
