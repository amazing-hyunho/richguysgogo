from datetime import datetime, timezone
import sqlite3
import unittest
from unittest.mock import patch

from committee.industry_cycle import supply_chain_monitor as monitor

NOW=datetime(2026,9,9,12,tzinfo=timezone.utc)


class MonitorTests(unittest.TestCase):
    def test_half_year_uses_cumulative_not_second_quarter(self):
        rows=[dict(fs_div="CFS",sj_div="IS",account_nm="매출액",thstrm_amount="94",thstrm_add_amount="167",frmtrm_amount="80",frmtrm_add_amount="118",rcept_no="20260813001263",currency="KRW"),
              dict(fs_div="OFS",sj_div="IS",account_nm="매출액",thstrm_amount="999")]
        f=monitor.normalize_financials(rows,year="2026",report="11012",now=NOW)
        self.assertEqual(f["basis"],"CFS")
        self.assertEqual(f["metrics"][0]["value"],167)
        self.assertEqual(f["metrics"][0]["prior"],118)
        self.assertAlmostEqual(f["metrics"][0]["change_pct"],41.53)
        self.assertEqual(f["published_at"],"2026-08-13")

    def test_loss_base_and_missing_values_do_not_create_growth(self):
        rows=[dict(fs_div="OFS",sj_div="IS",account_nm="영업이익",thstrm_amount="-",frmtrm_amount="-10")]
        f=monitor.normalize_financials(rows,year="2026",report="11013",now=NOW)
        self.assertIsNone(f["metrics"][0]["value"])
        self.assertIsNone(f["metrics"][0]["change_pct"])
        self.assertIsNone(monitor.number("NaN"))

    def test_missing_ytd_is_not_replaced_with_standalone_quarter(self):
        rows=[dict(fs_div="CFS",sj_div="IS",account_nm="매출액",thstrm_amount="94",frmtrm_amount="80")]
        f=monitor.normalize_financials(rows,year="2026",report="11012",now=NOW)
        self.assertIsNone(f["metrics"][0]["value"])
        self.assertTrue(f["metrics"][0]["missing_cumulative"])

    def test_news_future_undated_unsafe_duplicate_and_old_filtered(self):
        def item(link,dt,title="기업 수주 - 언론"):
            return dict(link=link,title=title,published_at=dt)
        rows=[item("https://a.test/1","2026-09-08"), item("https://b.test/2","2026-09-08"),
              item("https://a.test/future","2026-09-10","future"),item("https://a.test/none",None,"none"),
              item("javascript:alert(1)","2026-09-08","unsafe"),item("https://a.test/old","2026-07-01","old")]
        self.assertEqual(len(monitor.normalize_news(rows,now=NOW)),1)

    def test_first_seen_survives_refresh(self):
        old=[dict(link="https://a.test",title="수주",published_at="2026-09-08",first_seen_at="2026-09-08T01:00:00+00:00")]
        new=[{**old[0],"first_seen_at":NOW.isoformat()}]
        self.assertEqual(monitor.merge_news(old,new,NOW)[0]["first_seen_at"],old[0]["first_seen_at"])

    def test_dart_failure_does_not_expose_url_or_key(self):
        with patch("committee.tools.dart_client._request_dart_json",side_effect=RuntimeError("url?crtfc_key=SECRET")):
            result=monitor.fetch_financials("12345678",NOW)
        self.assertEqual(result,{"status":"error","error_type":"RuntimeError"})

    def test_company_news_disambiguates_similar_names(self):
        rows=[("흥국생명 수주","https://a.test",NOW),("흥국 롤러 수주","https://b.test",NOW)]
        with patch("committee.tools.news_digest.fetch_google_news_items",return_value=rows):
            result=monitor.fetch_news("흥국",NOW,["흥국"],["흥국생명"])
        self.assertEqual([r["title"] for r in result["items"]],["흥국 롤러 수주"])

    def test_transformed_macro_is_percent_not_dollars_and_future_vintage_excluded(self):
        conn=sqlite3.connect(":memory:");conn.row_factory=sqlite3.Row
        conn.execute("CREATE TABLE indicator_observation(indicator_id,observed_at,value,published_at,known_at,vintage_at,created_at)")
        conn.execute("CREATE TABLE daily_macro(date,usdkrw,us10y,oil_wti,hy_oas,data_date,published_at,observed_at)")
        conn.executemany("INSERT INTO indicator_observation VALUES(?,?,?,?,?,?,?)",[
            ("us_machinery_orders","2026-07-01",15,"2026-08-26","2026-08-26","2026-08-26","2026-08-26"),
            ("us_machinery_orders","2026-07-01",99,"2026-09-10","2026-09-10","2026-09-10","2026-09-10"),
            ("us_machinery_orders","2026-06-01",14,"2026-07-26","2026-07-26","2026-07-26","2026-07-26")])
        row=monitor.macro_context(conn,NOW)["indicators"]["us_machinery_orders"]
        self.assertEqual(row["display_unit"],"%")
        self.assertEqual(row["change_unit"],"%p")
        self.assertEqual(row["latest"]["value"],15)
        self.assertEqual(row["change"],1)
        conn.close()


if __name__=="__main__":unittest.main()
