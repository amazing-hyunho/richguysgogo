from contextlib import closing, nullcontext
from datetime import date
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from committee.tools import bok_trade_provider as bok
from committee.tools import naver_market_flow_provider as naver
from committee.tools.fred_monthly_provider import _parse_ism_manufacturing_pmi
from scripts import backfill_daily_macro_history as daily
from scripts import backfill_macro_indicators as advanced
from scripts import backfill_market_flow_history as flow
from scripts.audit_data import audit_database
from committee.core import database


class DataLossRegressionTests(unittest.TestCase):
    def test_nightly_flow_retry_preserves_values_and_accepts_real_zero(self):
        with closing(sqlite3.connect(':memory:')) as conn:
            conn.execute('CREATE TABLE market_flow_daily(date TEXT PRIMARY KEY, foreign_net REAL, institution_net REAL, retail_net REAL, foreign_20d REAL, foreign_60d REAL, kospi_foreign_net REAL, kospi_institution_net REAL, kospi_retail_net REAL, created_at TEXT)')
            with patch.object(database,'init_db'),patch.object(database,'connect',side_effect=lambda _:nullcontext(conn)):
                database.upsert_market_flow_daily(date='2026-09-25',foreign_net=10,foreign_20d=20)
                database.upsert_market_flow_daily(date='2026-09-25',foreign_net=None)
                self.assertEqual(conn.execute('SELECT foreign_net,foreign_20d FROM market_flow_daily').fetchone(),(10,20))
                database.upsert_market_flow_daily(date='2026-09-25',foreign_net=0)
                self.assertEqual(conn.execute('SELECT foreign_net FROM market_flow_daily').fetchone()[0],0)

    def test_daily_partial_failure_preserves_existing_and_writes_other_series(self):
        with TemporaryDirectory() as temp:
            db = Path(temp) / 'test.db'
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.execute('CREATE TABLE daily_macro(date TEXT PRIMARY KEY, us10y REAL, us2y REAL, spread_2_10 REAL, vix REAL, dxy REAL, usdkrw REAL, oil_wti REAL, created_at TEXT)')
                conn.execute("INSERT INTO daily_macro(date,us10y,oil_wti) VALUES ('2026-09-25',4.5,70)")
            def fetch(symbol, *_):
                if symbol == '^VIX': return {'2026-09-25': 19.0}
                raise RuntimeError('provider unavailable')
            args = SimpleNamespace(start_date='2026-09-25', end_date='2026-09-25', dry_run=False)
            with patch.object(daily, 'DB_PATH', db), patch.object(daily, 'init_db'), patch.object(daily, '_parse_args', return_value=args), patch.object(daily, '_fetch_series', side_effect=fetch):
                daily.main()
            with closing(sqlite3.connect(db)) as conn, conn:
                self.assertEqual(conn.execute('SELECT us10y,oil_wti,vix FROM daily_macro').fetchone(), (4.5,70,19))

    def test_advanced_missing_series_does_not_erase_other_columns(self):
        with TemporaryDirectory() as temp:
            db = Path(temp) / 'test.db'
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.execute('CREATE TABLE daily_macro(date TEXT PRIMARY KEY, vix3m REAL, vix_term_spread REAL, hy_oas REAL, ig_oas REAL, fed_balance_sheet REAL, created_at TEXT)')
                conn.execute("INSERT INTO daily_macro VALUES ('2026-09-25',20,2,3,NULL,100,'old')")
            values = dict(vix3m=None,vix_term_spread=None,hy_oas=None,ig_oas=1,fed_balance_sheet=None)
            with patch.object(advanced, 'DB_PATH', db), patch.object(advanced, 'init_db'), patch.object(advanced, 'load_project_env'), patch.object(advanced, '_fetch_row_values', return_value=values), patch('sys.argv', ['backfill']):
                advanced.main()
            with closing(sqlite3.connect(db)) as conn, conn:
                self.assertEqual(conn.execute('SELECT vix3m,hy_oas,ig_oas,fed_balance_sheet FROM daily_macro').fetchone(), (20,3,1,100))

    def test_flow_failure_preserves_history_and_rolling_totals(self):
        with TemporaryDirectory() as temp:
            db = Path(temp) / 'test.db'
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.execute('CREATE TABLE market_flow_daily(date TEXT PRIMARY KEY, foreign_net REAL, institution_net REAL, retail_net REAL, foreign_20d REAL, foreign_60d REAL, kospi_foreign_net REAL, kospi_institution_net REAL, kospi_retail_net REAL, created_at TEXT)')
                conn.execute("INSERT INTO market_flow_daily VALUES ('2026-09-25',1,2,3,20,60,4,5,6,'old')")
            args=SimpleNamespace(start_date='2026-09-25',end_date='2026-09-25',source='AUTO',dry_run=False,skip_existing=False,sleep_ms=0)
            with patch.object(flow,'DB_PATH',db),patch.object(flow,'init_db'),patch.object(flow,'_parse_args',return_value=args),patch.object(flow,'_fetch_flow',return_value=(None,'unavailable')):
                flow.main()
            with closing(sqlite3.connect(db)) as conn, conn:
                self.assertEqual(conn.execute('SELECT foreign_net,foreign_20d,foreign_60d FROM market_flow_daily').fetchone(),(1,20,60))

    def test_naver_does_not_relabel_another_days_data(self):
        response=SimpleNamespace(status_code=200,text='<tr><td>26.09.17</td><td>1</td><td>2</td><td>3</td></tr>')
        with patch.object(naver.requests,'get',return_value=response):
            with self.assertRaisesRegex(RuntimeError,'row_not_found'):
                naver._fetch_market_flow_eok('20260918','01')

    def test_missing_flow_is_not_zero(self):
        for value in ('','-','N/A'):
            with self.assertRaises(ValueError): naver._parse_eok_cell(value)
        self.assertEqual(naver._parse_eok_cell('0'),0)
        with self.assertRaises(ValueError): flow._aggregate({'market':{}})

    def test_exports_does_not_choose_imports(self):
        with patch.object(bok,'_statistic_item_list_all_rows',return_value=[{'ITEM_CODE':'T004','ITEM_NAME':'수입금액'}]):
            self.assertIsNone(bok._resolve_export_item_code('unused',timeout_sec=1))

    def test_exports_uses_new_table_and_correct_year_comparison(self):
        rows=[{'ITEM_CODE1':'T002','TIME':'202507','DATA_VALUE':'100'}, {'ITEM_CODE1':'T002','TIME':'202607','DATA_VALUE':'110'}]
        with patch.dict('os.environ',{'ECOS_API_KEY':'test','ECOS_EXPORT_ITEM_CODE':'T002'}),patch.object(bok,'_statistic_search_last_page',return_value={'StatisticSearch':{'row':rows}}) as request:
            self.assertAlmostEqual(bok.fetch_korea_export_yoy(date(2026,9,28)),10)
            self.assertTrue(request.call_args.args[1].startswith('901Y118/M/'))

    def test_pmi_parser_accepts_html_and_rejects_stale_reports(self):
        html='<h1>Manufacturing PMI<sup>®</sup> at 54.6%</h1><h2>August 2026 ISM® Manufacturing PMI® Report</h2>'
        self.assertEqual(_parse_ism_manufacturing_pmi(html,date(2026,9,28)),54.6)
        self.assertIsNone(_parse_ism_manufacturing_pmi(html.replace('August 2026','December 2025'),date(2026,9,28)))

    def test_audit_classifies_missing_stale_and_real_zero(self):
        with TemporaryDirectory() as temp:
            db=Path(temp)/'test.db'
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.execute('CREATE TABLE daily_macro(date TEXT, vix REAL, hy_oas REAL, dxy REAL)')
                conn.executemany('INSERT INTO daily_macro VALUES (?,?,?,?)',[('2026-09-01',20,None,None),('2026-09-28',None,None,0)])
            result=audit_database(db,date(2026,9,28))
            self.assertEqual({r['metric']:r['status'] for r in result['metrics']},{'vix':'stale','hy_oas':'missing','dxy':'available'})
            self.assertEqual(result['integrity'],['ok'])


if __name__ == '__main__':
    unittest.main()
