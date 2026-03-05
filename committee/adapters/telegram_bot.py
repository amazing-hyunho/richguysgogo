from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

from committee.core.strategy_store import load_latest_strategy, update_strategy

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

    return _build_answer_from_context(stripped, context)


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
