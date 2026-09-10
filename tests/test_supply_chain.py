from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from committee.industry_cycle.supply_chain import CATALOG_PATH, ROOT, load_supply_chain_dashboard_data, validate_catalog
from scripts import build_dashboard
from scripts.render_dashboard_for_pages import load_embedded_dashboard_data


class SupplyChainTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.taxonomy = json.loads((ROOT / "config/industry_taxonomy.json").read_text(encoding="utf-8"))

    def test_all_active_industries_have_sourced_maps_and_no_duplicate_company_count(self):
        data = load_supply_chain_dashboard_data(as_of="2026-09-09")
        self.assertEqual(data["summary"]["industry_count"], 25)
        self.assertEqual(data["summary"]["mapped_industry_count"], 25)
        self.assertLess(data["summary"]["company_count"], data["summary"]["relationship_count"])
        self.assertTrue(any(r["revenue_exposure"]["value_pct"] is None for r in data["relationships"]))
        self.assertGreater(data["summary"]["research_observation_count"], 0)

    def test_research_is_not_available_before_it_was_known(self):
        data = load_supply_chain_dashboard_data(as_of="2026-09-08")
        self.assertEqual(data["relationships"], [])
        self.assertEqual(data["summary"]["mapped_industry_count"], 0)

    def test_broken_references_and_unsourced_numbers_fail(self):
        mutations = [
            lambda d: d["relationships"][0].update(fact_source_ids=["missing"]),
            lambda d: d["relationships"][0]["revenue_exposure"].update(value_pct=50),
            lambda d: d["relationships"][0].update(company_id="missing"),
            lambda d: d["sources"][0].update(url="javascript:alert(1)"),
            lambda d: d["industries"].pop(),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                bad = copy.deepcopy(self.catalog)
                mutation(bad)
                with self.assertRaises(ValueError):
                    validate_catalog(bad, self.taxonomy)

    def test_indirect_and_service_relationships_remain_distinct(self):
        for r in self.catalog["relationships"]:
            if r["industry_id"] in {"shipping", "airlines"}:
                self.assertEqual(r["directness"], "indirect")
            if r["industry_id"] in {"banks", "securities", "software_cloud"}:
                self.assertEqual(r["role"], "service")

    def test_dashboard_roundtrip_keeps_existing_payload_and_safe_research(self):
        data = {"industry_cycle": {"as_of": "2026-09-06"}, "supply_chain": self.catalog}
        data["supply_chain"]["companies"][0]["name"] = '</script><script>alert("x")</script>'
        html = build_dashboard.build_dashboard_html(data)
        self.assertNotIn("__SUPPLY_CHAIN_PANEL__", html)
        self.assertNotIn('</script><script>alert("x")', html)
        self.assertIn('id="tab-supply-chain"', html)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dashboard.html"
            path.write_text(html, encoding="utf-8")
            self.assertEqual(load_embedded_dashboard_data(path), data)


if __name__ == "__main__":
    unittest.main()
