import unittest
from unittest.mock import patch
from scripts.render_dashboard_for_pages import refresh_meeting_data


class ReportFreshnessTests(unittest.TestCase):
    def test_older_checkout_cannot_replace_newer_html(self):
        data = {'latest_committee': {'market_date':'2026-10-08','sugeup_narrative':'new'}, 'latest_stances': {'market_date':'2026-10-08'}}
        with patch('scripts.build_dashboard.load_latest_committee', return_value={'market_date':'2026-10-05','sugeup_narrative':'old'}):
            refresh_meeting_data(data)
        self.assertEqual(data['latest_committee']['sugeup_narrative'], 'new')
        self.assertEqual(data['latest_stances']['market_date'], '2026-10-08')

    def test_empty_same_day_does_not_erase_report(self):
        data = {'latest_committee': {'market_date':'2026-10-08','sugeup_narrative':'valid'}}
        with patch('scripts.build_dashboard.load_latest_committee', return_value={'market_date':'2026-10-08','sugeup_narrative':''}):
            refresh_meeting_data(data)
        self.assertEqual(data['latest_committee']['sugeup_narrative'], 'valid')

    def test_newer_report_refreshes(self):
        data = {'latest_committee': {'market_date':'2026-10-05','sugeup_narrative':'old'}}
        with patch('scripts.build_dashboard.load_latest_committee', return_value={'market_date':'2026-10-08','sugeup_narrative':'new'}):
            refresh_meeting_data(data)
        self.assertEqual(data['latest_committee']['sugeup_narrative'], 'new')


if __name__ == '__main__': unittest.main()
