from contextlib import closing, nullcontext
from datetime import date, timedelta
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from committee.tools import naver_market_flow_provider as provider
from committee.core import database, market_collector
from scripts import sync_market_flows as sync, build_dashboard


def api_row(day='20261002', missing=None):
    values={'8000':'-1789715000000','9000':'-101118000000','9001':'-6897000000',
            **{k:'100000000' for k in provider._INSTITUTIONS}}
    if missing: values.pop(missing)
    return {'bizdate':day,'netAmounts':[{'investorGubun':k,'diffValue':v} for k,v in values.items()]}


def response(rows):
    return Mock(**{'json.return_value':{'content':rows}})


class MarketFlowRecoveryTests(unittest.TestCase):
    def test_api_unit_and_naver_foreign_definition(self):
        parsed=provider._parse_api_investors(api_row())
        self.assertEqual(parsed,{'individual':-17897,'foreign':-1080,'institution':8})

    def test_missing_institution_and_nonfinite_are_rejected(self):
        with self.assertRaises(ValueError): provider._parse_api_investors(api_row(missing='3100'))
        row=api_row();row['netAmounts'][0]['diffValue']='NaN'
        with self.assertRaises(ValueError): provider._parse_api_investors(row)

    def test_weekend_uses_actual_trading_date(self):
        with patch.object(provider.requests,'get',return_value=response([api_row()])) as get:
            result=provider.get_korean_market_flow_naver(date(2026,10,3))
        self.assertEqual(result['date'],'2026-10-02')
        self.assertEqual(get.call_count,2)
        self.assertEqual(get.call_args.kwargs['params']['tradeType'],'KRX')

    def test_mismatched_market_dates_fail_closed(self):
        with patch.object(provider.requests,'get',side_effect=[response([api_row()]),response([api_row('20261001')])]):
            with self.assertRaisesRegex(RuntimeError,'dates_mismatch'):
                provider.fetch_korean_market_flow_history(date(2026,10,3))

    def test_future_date_rejected(self):
        with patch.object(provider.requests,'get',return_value=response([api_row()])):
            with self.assertRaises(ValueError): provider.fetch_korean_market_flow_history(date(2026,10,1))

    def test_collection_failure_never_reaches_database_write(self):
        with patch('sys.argv',['sync_market_flows']),patch.object(sync,'fetch_korean_market_flow_history',side_effect=RuntimeError('source_unavailable')),patch.object(sync,'save_history') as save:
            with self.assertRaisesRegex(RuntimeError,'source_unavailable'): sync.main()
        save.assert_not_called()

    def test_short_history_is_not_accepted_as_complete(self):
        history=[{'date':'2026-10-02','market':{}}]
        with patch('sys.argv',['sync_market_flows','--as-of','2026-10-02']),patch.object(sync,'fetch_korean_market_flow_history',return_value=history),patch.object(sync,'save_history') as save:
            with self.assertRaisesRegex(RuntimeError,'insufficient_flow_history'): sync.main()
        save.assert_not_called()

    def test_source_holiday_gap_counts_observations_not_calendar_days(self):
        days=[];d=date(2026,6,1)
        while len(days)<65:
            if d.weekday()<5 and d!=date(2026,7,17):days.append(d.isoformat())
            d+=timedelta(days=1)
        history=[{'date':d,'market':{'KOSPI':{'foreign':1,'institution':2,'individual':-3},
                                   'KOSDAQ':{'foreign':4,'institution':5,'individual':-9}}} for d in days]
        with TemporaryDirectory() as temp:
            db=Path(temp)/'test.db'
            sync.save_history(history,db)
            sync.save_history(history,db)
            with closing(sqlite3.connect(db)) as conn:
                self.assertEqual(conn.execute('SELECT count(*) FROM market_flow_daily').fetchone()[0],65)
                self.assertEqual(conn.execute('SELECT foreign_20d,foreign_60d FROM market_flow_daily ORDER BY date DESC LIMIT 1').fetchone(),(100,300))
            with patch.object(build_dashboard,'DB_PATH',db):
                current=build_dashboard.load_latest_korean_market_flow_breakdown()
                compare=build_dashboard.load_korean_market_flow_compare()
            self.assertEqual(current['market_date'],days[-1])
            self.assertEqual(current['market']['KOSDAQ']['foreign'],4)
            self.assertEqual(compare['previous_date'],days[-2])

    def test_rolling_calculation_never_looks_beyond_target_date(self):
        with closing(sqlite3.connect(':memory:')) as conn:
            conn.row_factory=sqlite3.Row
            conn.execute('CREATE TABLE market_flow_daily(date TEXT,foreign_net REAL)')
            conn.executemany('INSERT INTO market_flow_daily VALUES (?,?)',[('2026-10-01',1),('2026-10-02',999)])
            with patch.object(database,'init_db'),patch.object(database,'connect',side_effect=lambda _:nullcontext(conn)):
                self.assertEqual(database.calculate_rolling_sum('foreign_net',1,asof='2026-10-01'),1)

    def test_snapshot_weekend_is_not_written_as_a_new_flow_session(self):
        market=SimpleNamespace(kospi_pct=1,kosdaq_pct=1,kospi=1,kosdaq=1)
        snapshot=SimpleNamespace(markets=SimpleNamespace(kr=market,us=SimpleNamespace(sp500_pct=1,nasdaq_pct=1,dow_pct=1,sp500=1,nasdaq=1,dow=1),fx=SimpleNamespace(usdkrw=1,usdkrw_pct=1),volatility=SimpleNamespace(vix=1)),macro=None,
            flow_summary=SimpleNamespace(foreign_net=3,institution_net=4,retail_net=-7),
            korean_market_flow=SimpleNamespace(date='2026-10-02',market={'KOSPI':SimpleNamespace(foreign=1,institution=2,individual=-3)}))
        with patch.object(market_collector,'safe_upsert_market_daily'),patch.object(market_collector,'safe_upsert_domestic_policy_rate_daily'),patch.object(market_collector,'check_bok_base_rate',return_value=SimpleNamespace(value=2.5,status='ok')),patch.object(market_collector,'safe_upsert_market_flow_daily') as save:
            market_collector.persist_snapshot_metrics(snapshot,date(2026,10,3),{'flows':'OK'})
        self.assertEqual(save.call_args.kwargs['date'],'2026-10-02')


if __name__=='__main__':
    unittest.main()
