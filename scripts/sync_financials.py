from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import (  # noqa: E402
    connect,
    upsert_dart_company,
    upsert_financial_metric,
    upsert_financial_statement,
)
from committee.tools.dart_client import fetch_dart_company_codes, fetch_financials  # noqa: E402

ACCOUNT_NAME_MAP = {
    "매출액": "revenue",
    "영업이익": "operating_income",
    "당기순이익": "net_income",
    "자산총계": "total_assets",
    "부채총계": "total_liabilities",
    "자본총계": "total_equity",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync DART annual financial data into DB.")
    parser.add_argument("year", type=int, help="Business year (e.g., 2025).")
    return parser.parse_args()


def _build_ticker_to_dart_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT tm.ticker AS ticker, dcc.dart_corp_code AS dart_corp_code
            FROM ticker_master tm
            LEFT JOIN dart_company_code dcc
              ON tm.ticker = dcc.stock_code
            """
        ).fetchall()

    for row in rows:
        ticker = str(row["ticker"] or "").strip().upper()
        dart_corp_code = str(row["dart_corp_code"] or "").strip()
        if ticker and dart_corp_code:
            mapping[ticker] = dart_corp_code
    return mapping


def _normalize_metrics(rows: list[dict]) -> dict[tuple[str, str], dict[str, float | None]]:
    normalized: dict[tuple[str, str], dict[str, float | None]] = {}

    for row in rows:
        report_code = str(row.get("report_code") or "11011").strip() or "11011"
        business_year = str(row.get("business_year") or "").strip()
        account_name = str(row.get("account_name") or "").strip()
        amount = row.get("amount")

        metric_key = ACCOUNT_NAME_MAP.get(account_name)
        if not metric_key or not business_year:
            continue

        bucket_key = (business_year, report_code)
        if bucket_key not in normalized:
            normalized[bucket_key] = {
                "revenue": None,
                "operating_income": None,
                "net_income": None,
                "total_assets": None,
                "total_liabilities": None,
                "total_equity": None,
            }
        normalized[bucket_key][metric_key] = None if amount is None else float(amount)

    return normalized


def main() -> None:
    args = _parse_args()

    corp_rows = fetch_dart_company_codes()
    print(f"sync_financials_dart_company_codes_fetched={len(corp_rows)}")

    corp_success = 0
    corp_failed = 0
    for row in corp_rows:
        try:
            upsert_dart_company(row)
            corp_success += 1
        except Exception as exc:  # noqa: BLE001
            corp_failed += 1
            print(f"sync_financials_upsert_dart_company_failed[{row.get('dart_corp_code')}]: {exc}")

    ticker_to_dart = _build_ticker_to_dart_map()
    print(f"sync_financials_ticker_mapped={len(ticker_to_dart)}")

    company_processed = 0
    company_skipped = 0
    statement_upserted = 0
    metric_upserted = 0

    with connect() as conn:
        ticker_rows = conn.execute("SELECT ticker FROM ticker_master ORDER BY ticker").fetchall()

    for row in ticker_rows:
        ticker = str(row["ticker"] or "").strip().upper()
        dart_corp_code = ticker_to_dart.get(ticker)

        if not ticker or not dart_corp_code:
            company_skipped += 1
            continue

        try:
            financial_rows = fetch_financials(dart_corp_code, args.year)
        except Exception as exc:  # noqa: BLE001
            print(f"sync_financials_fetch_failed[{ticker}][{dart_corp_code}][{args.year}]: {exc}")
            continue

        company_processed += 1

        for fin in financial_rows:
            try:
                upsert_financial_statement(
                    {
                        "ticker": ticker,
                        "business_year": fin.get("business_year") or str(args.year),
                        "report_code": fin.get("report_code") or "11011",
                        "account_name": fin.get("account_name"),
                        "amount": fin.get("amount"),
                    }
                )
                statement_upserted += 1
            except Exception as exc:  # noqa: BLE001
                print(f"sync_financials_upsert_statement_failed[{ticker}]: {exc}")

        metric_rows = _normalize_metrics(financial_rows)
        for (business_year, report_code), metric in metric_rows.items():
            try:
                upsert_financial_metric(
                    {
                        "ticker": ticker,
                        "business_year": business_year,
                        "report_code": report_code,
                        **metric,
                    }
                )
                metric_upserted += 1
            except Exception as exc:  # noqa: BLE001
                print(f"sync_financials_upsert_metric_failed[{ticker}][{business_year}][{report_code}]: {exc}")

    print(
        "sync_financials_done "
        f"year={args.year} "
        f"dart_company_success={corp_success} "
        f"dart_company_failed={corp_failed} "
        f"company_processed={company_processed} "
        f"company_skipped_no_mapping={company_skipped} "
        f"statement_upserted={statement_upserted} "
        f"metric_upserted={metric_upserted}"
    )


if __name__ == "__main__":
    main()
