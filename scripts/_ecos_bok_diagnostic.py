"""One-off ECOS diagnostic; do not commit secrets. Reads ECOS_API_KEY from env."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def main() -> None:
    key = os.getenv("ECOS_API_KEY", "").strip()
    if not key:
        print("ERROR: ECOS_API_KEY not set in environment")
        raise SystemExit(2)

    def get_json(path_suffix: str) -> dict:
        url = "https://ecos.bok.or.kr/api/" + path_suffix.replace(
            "{KEY}", urllib.parse.quote(key, safe="")
        )
        req = urllib.request.Request(url, headers={"User-Agent": "bok-diagnostic/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    def rows_from(payload: dict, keyname: str) -> list[dict]:
        blk = payload.get(keyname)
        if not isinstance(blk, dict):
            return []
        row = blk.get("row")
        if isinstance(row, list):
            return [x for x in row if isinstance(x, dict)]
        if isinstance(row, dict):
            return [row]
        return []

    def print_diag(title: str, payload: dict, rows: list[dict], limit: int = 10) -> None:
        print("===", title, "===")
        if not rows:
            res = payload.get("RESULT") if isinstance(payload, dict) else None
            print("  (no rows)", res)
            return
        sorted_rows = sorted(rows, key=lambda r: str(r.get("TIME") or ""), reverse=True)[:limit]
        for r in sorted_rows:
            name = str(r.get("ITEM_NAME1") or "")
            if len(name) > 50:
                name = name[:47] + "..."
            print(
                " ",
                r.get("TIME"),
                "|",
                r.get("ITEM_CODE1"),
                "|",
                name,
                "|",
                r.get("DATA_VALUE"),
            )

    for stat in ("722Y001", "817Y002", "060Y001"):
        try:
            p = get_json(f"StatisticItemList/{{KEY}}/json/kr/1/500/{stat}")
            items = rows_from(p, "StatisticItemList")
            hits = [
                x
                for x in items
                if "기준" in str(x.get("ITEM_NAME", ""))
                or "한국은행" in str(x.get("ITEM_NAME", ""))
            ]
            print("--- StatisticItemList", stat, "total items", len(items), "---")
            for x in hits[:40]:
                print(" ", x.get("ITEM_CODE"), "|", x.get("ITEM_NAME"), "|", x.get("CYCLE"))
            if stat == "722Y001" and not hits:
                print("  (no 기준/한국은행 in name; first 20 items:)")
                for x in items[:20]:
                    print(" ", x.get("ITEM_CODE"), "|", x.get("ITEM_NAME"))
        except Exception as exc:
            print("--- StatisticItemList", stat, "FAILED:", exc)

    start, end = "202001", "202604"
    payload = get_json(
        f"StatisticSearch/{{KEY}}/json/kr/1/200/722Y001/M/{start}/{end}/0101000"
    )
    rows = rows_from(payload, "StatisticSearch")
    print_diag("722Y001 monthly ITEM 0101000", payload, rows)

    for label, suffix in [
        ("no trailing item", f"StatisticSearch/{{KEY}}/json/kr/1/200/722Y001/M/{start}/{end}"),
        ("trailing slash only", f"StatisticSearch/{{KEY}}/json/kr/1/200/722Y001/M/{start}/{end}/"),
    ]:
        try:
            p = get_json(suffix)
            rows2 = rows_from(p, "StatisticSearch")
            print_diag(label, p, rows2)
        except Exception as exc:
            print("===", label, "FAILED ===", exc)


if __name__ == "__main__":
    main()
