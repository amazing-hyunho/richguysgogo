from __future__ import annotations

from datetime import date
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from committee.future_economy.official_collectors import (
    collect_dart_disclosure_evidence,
    collect_official_policy_api_evidence,
    fetch_federal_register_documents,
)
from committee.tools.dart_client import fetch_disclosures


DOMAIN = {
    "domain_id": "ai-semiconductor-datacenter",
    "evidence_keywords": ["semiconductor", "data center", "반도체"],
    "industry_ids": ["semiconductors"],
}


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


class FutureEconomyOfficialCollectorTests(unittest.TestCase):
    def test_federal_register_fetch_and_domain_mapping_keep_official_url(self) -> None:
        captured = {}

        def fake_get(url, **kwargs):
            captured["url"] = url
            captured["params"] = kwargs["params"]
            return _FakeResponse({"results": [
                {
                    "document_number": "2026-12345",
                    "title": "Semiconductor Manufacturing Incentive Rule",
                    "abstract": "A final rule for semiconductor manufacturing grants.",
                    "publication_date": "2026-08-24",
                    "html_url": "https://www.federalregister.gov/documents/2026/08/24/example",
                    "agencies": [{"name": "Department of Commerce"}],
                },
                {
                    "document_number": "2026-12346",
                    "title": "Clean Air Act Petition",
                    "abstract": "Air quality response without artificial intelligence content.",
                    "publication_date": "2026-08-24",
                    "html_url": "https://www.federalregister.gov/documents/2026/08/24/air",
                    "agencies": [{"name": "Environmental Protection Agency"}],
                },
                {
                    "document_number": "2026-12347",
                    "title": "Proposed Collection; Comment Request",
                    "abstract": "A semiconductor information collection notice.",
                    "publication_date": "2026-08-24",
                    "html_url": "https://www.federalregister.gov/documents/2026/08/24/collection",
                    "agencies": [{"name": "Department of Commerce"}],
                },
            ]})

        documents = fetch_federal_register_documents(
            as_of="2026-08-25", requester=fake_get
        )
        rows = collect_official_policy_api_evidence(
            domain=DOMAIN, as_of="2026-08-25", documents=documents
        )
        self.assertEqual(len(documents), 3)
        self.assertIn("publication_date", " ".join(captured["params"]))
        self.assertEqual(rows[0]["evidence_type"], "policy")
        self.assertEqual(rows[0]["source_kind"], "official_policy")
        self.assertTrue(rows[0]["source_url"].startswith("https://www.federalregister.gov/"))
        self.assertEqual(len(rows), 1)

    def test_dart_collector_requires_mapped_stock_and_material_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            conn = sqlite3.connect(db_path)
            try:
                conn.executescript(
                    """
                    CREATE TABLE industry_asset_map (
                        asset_id TEXT, asset_type TEXT, market TEXT, industry_id TEXT,
                        valid_from TEXT, valid_to TEXT, weight REAL
                    );
                    CREATE TABLE ticker_master (
                        ticker TEXT, market TEXT, company_name TEXT
                    );
                    """
                )
                conn.execute(
                    "INSERT INTO industry_asset_map VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("005930", "STOCK", "KR", "semiconductors", "2026-01-01", None, 0.5),
                )
                conn.execute(
                    "INSERT INTO ticker_master VALUES (?, ?, ?)",
                    ("005930", "KR", "삼성전자"),
                )
                conn.commit()
            finally:
                conn.close()
            disclosures = [
                {
                    "receipt_no": "20260824000001",
                    "receipt_date": "2026-08-24",
                    "company_name": "삼성전자",
                    "stock_code": "005930",
                    "report_name": "신규시설투자등",
                },
                {
                    "receipt_no": "20260824000002",
                    "receipt_date": "2026-08-24",
                    "company_name": "다른회사",
                    "stock_code": "999999",
                    "report_name": "단일판매ㆍ공급계약체결",
                },
            ]
            rows, companies = collect_dart_disclosure_evidence(
                domain=DOMAIN,
                as_of="2026-08-25",
                db_path=db_path,
                disclosures=disclosures,
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["source_kind"], "regulatory_filing")
            self.assertIn("20260824000001", rows[0]["source_url"])
            self.assertEqual(companies[0]["stock_code"], "005930")

    def test_dart_api_fetch_paginates_and_normalizes_receipt_date(self) -> None:
        responses = [
            {
                "status": "000",
                "total_page": 1,
                "list": [{
                    "rcept_no": "20260824000001",
                    "rcept_dt": "20260824",
                    "corp_name": "삼성전자",
                    "corp_code": "00126380",
                    "stock_code": "005930",
                    "report_nm": "신규시설투자등",
                    "corp_cls": "Y",
                }],
            },
            {"status": "013", "total_page": 0, "list": []},
        ]
        with mock.patch(
            "committee.tools.dart_client._request_dart_json", side_effect=responses
        ) as request_mock:
            rows = fetch_disclosures(
                date(2026, 8, 12), date(2026, 8, 25), max_pages_per_type=1
            )
        self.assertEqual(request_mock.call_count, 2)
        self.assertEqual(rows[0]["receipt_date"], "2026-08-24")
        self.assertEqual(rows[0]["stock_code"], "005930")


if __name__ == "__main__":
    unittest.main()
