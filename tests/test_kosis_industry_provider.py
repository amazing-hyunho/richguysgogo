from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.tools import kosis_industry_provider as provider


def _fake_response(status_code=200, json_payload=None):
    resp = mock.Mock()
    resp.status_code = status_code
    resp.json.return_value = json_payload if json_payload is not None else []
    return resp


class FetchKosisSeriesTests(unittest.TestCase):
    def test_missing_api_key_returns_none(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("KOSIS_API_KEY", None)
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1")
        self.assertIsNone(result)

    def test_parses_monthly_period_rows(self) -> None:
        payload = [
            {"PRD_DE": "202401", "DT": "123.4"},
            {"PRD_DE": "202402", "DT": "125.0"},
        ]
        with mock.patch.dict("os.environ", {"KOSIS_API_KEY": "fakekey"}), mock.patch(
            "committee.tools.kosis_industry_provider.requests.get", return_value=_fake_response(json_payload=payload)
        ):
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1", prd_se="M")
        self.assertEqual(
            result,
            [
                {"observed_at": "2024-01-01", "value": 123.4},
                {"observed_at": "2024-02-01", "value": 125.0},
            ],
        )

    def test_parses_quarterly_period_rows(self) -> None:
        payload = [{"PRD_DE": "2024Q2", "DT": "50.0"}]
        with mock.patch.dict("os.environ", {"KOSIS_API_KEY": "fakekey"}), mock.patch(
            "committee.tools.kosis_industry_provider.requests.get", return_value=_fake_response(json_payload=payload)
        ):
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1", prd_se="Q")
        self.assertEqual(result, [{"observed_at": "2024-04-01", "value": 50.0}])

    def test_parses_annual_period_rows(self) -> None:
        payload = [{"PRD_DE": "2024", "DT": "10.0"}]
        with mock.patch.dict("os.environ", {"KOSIS_API_KEY": "fakekey"}), mock.patch(
            "committee.tools.kosis_industry_provider.requests.get", return_value=_fake_response(json_payload=payload)
        ):
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1", prd_se="Y")
        self.assertEqual(result, [{"observed_at": "2024-01-01", "value": 10.0}])

    def test_drops_unparseable_value(self) -> None:
        payload = [{"PRD_DE": "202401", "DT": "not_a_number"}]
        with mock.patch.dict("os.environ", {"KOSIS_API_KEY": "fakekey"}), mock.patch(
            "committee.tools.kosis_industry_provider.requests.get", return_value=_fake_response(json_payload=payload)
        ):
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1", prd_se="M")
        self.assertEqual(result, [])

    def test_api_error_response_returns_none(self) -> None:
        payload = {"err": "50", "errMsg": "SERVICE ERROR"}
        with mock.patch.dict("os.environ", {"KOSIS_API_KEY": "fakekey"}), mock.patch(
            "committee.tools.kosis_industry_provider.requests.get", return_value=_fake_response(json_payload=payload)
        ):
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1")
        self.assertIsNone(result)

    def test_non_200_status_returns_none(self) -> None:
        with mock.patch.dict("os.environ", {"KOSIS_API_KEY": "fakekey"}), mock.patch(
            "committee.tools.kosis_industry_provider.requests.get", return_value=_fake_response(status_code=500)
        ):
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1")
        self.assertIsNone(result)

    def test_network_exception_returns_none_not_raises(self) -> None:
        with mock.patch.dict("os.environ", {"KOSIS_API_KEY": "fakekey"}), mock.patch(
            "committee.tools.kosis_industry_provider.requests.get", side_effect=RuntimeError("boom")
        ):
            result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1")
        self.assertIsNone(result)

    def test_real_environment_has_no_kosis_key_configured(self) -> None:
        """Documents the actual state of this environment (no KOSIS_API_KEY):
        the provider must isolate/skip rather than raise, exercised for real
        (no mocking) against whatever the environment currently provides."""
        result = provider.fetch_kosis_series(org_id="101", tbl_id="DT_1234", item_id="T1")
        if not provider._kosis_key():
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
