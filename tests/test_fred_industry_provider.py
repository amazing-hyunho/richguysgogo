from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.tools import fred_industry_provider as provider


def _fake_response(status_code=200, json_payload=None):
    resp = mock.Mock()
    resp.status_code = status_code
    resp.json.return_value = json_payload or {}
    return resp


class FetchInitialReleasesTests(unittest.TestCase):
    def test_missing_api_key_returns_none(self) -> None:
        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value=None):
            result = provider.fetch_fred_series_initial_releases("INDPRO")
        self.assertIsNone(result)

    def test_parses_observations_and_drops_dot_values(self) -> None:
        payload = {
            "observations": [
                {"date": "2026-01-01", "value": "100.5", "realtime_start": "2026-02-01"},
                {"date": "2026-02-01", "value": ".", "realtime_start": "2026-03-01"},
                {"date": "2026-03-01", "value": "101.2", "realtime_start": "2026-04-01"},
            ]
        }
        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value="fakekey"), mock.patch(
            "committee.tools.fred_industry_provider.requests.get", return_value=_fake_response(json_payload=payload)
        ):
            result = provider.fetch_fred_series_initial_releases("INDPRO")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"observed_at": "2026-01-01", "value": 100.5, "published_at": "2026-02-01"})
        self.assertEqual(result[1]["observed_at"], "2026-03-01")

    def test_uses_output_type_4_for_initial_release(self) -> None:
        captured = {}

        def _fake_get(url, params=None, timeout=None):
            captured["params"] = params
            return _fake_response(json_payload={"observations": []})

        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value="fakekey"), mock.patch(
            "committee.tools.fred_industry_provider.requests.get", side_effect=_fake_get
        ):
            provider.fetch_fred_series_initial_releases("INDPRO")
        self.assertEqual(captured["params"]["output_type"], 4)

    def test_non_200_status_returns_none(self) -> None:
        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value="fakekey"), mock.patch(
            "committee.tools.fred_industry_provider.requests.get", return_value=_fake_response(status_code=500)
        ):
            result = provider.fetch_fred_series_initial_releases("INDPRO")
        self.assertIsNone(result)

    def test_network_exception_returns_none_not_raises(self) -> None:
        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value="fakekey"), mock.patch(
            "committee.tools.fred_industry_provider.requests.get", side_effect=RuntimeError("boom")
        ):
            result = provider.fetch_fred_series_initial_releases("INDPRO")
        self.assertIsNone(result)


class FetchAsOfTests(unittest.TestCase):
    def test_missing_api_key_returns_none(self) -> None:
        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value=None):
            result = provider.fetch_fred_series_as_of("INDPRO", "2024-06-01")
        self.assertIsNone(result)

    def test_uses_realtime_window_pinned_to_as_of(self) -> None:
        captured = {}

        def _fake_get(url, params=None, timeout=None):
            captured["params"] = params
            return _fake_response(json_payload={"observations": []})

        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value="fakekey"), mock.patch(
            "committee.tools.fred_industry_provider.requests.get", side_effect=_fake_get
        ):
            provider.fetch_fred_series_as_of("INDPRO", "2024-06-01")
        self.assertEqual(captured["params"]["realtime_start"], "2024-06-01")
        self.assertEqual(captured["params"]["realtime_end"], "2024-06-01")

    def test_published_at_defaults_to_as_of(self) -> None:
        payload = {"observations": [{"date": "2024-01-01", "value": "50.1"}]}
        with mock.patch("committee.tools.fred_industry_provider.fred_api_key", return_value="fakekey"), mock.patch(
            "committee.tools.fred_industry_provider.requests.get", return_value=_fake_response(json_payload=payload)
        ):
            result = provider.fetch_fred_series_as_of("INDPRO", "2024-06-01")
        self.assertEqual(result, [{"observed_at": "2024-01-01", "value": 50.1, "published_at": "2024-06-01"}])


if __name__ == "__main__":
    unittest.main()
