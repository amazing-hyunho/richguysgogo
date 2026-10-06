from datetime import datetime
import json
from pathlib import Path
import sqlite3
import subprocess
import unittest

from committee.tools.korea_macro_provider import month_offset, parse_history
from scripts.sync_korea_macro import collect, KST
from scripts.build_dashboard import build_dashboard_html

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / 'config/korea_macro_indicators.json').read_text(encoding='utf-8'))[0]


def response():
    return {'StatisticSearch': {'list_total_count': 2, 'row': [
        {'STAT_CODE': SPEC['table'], 'ITEM_CODE1': SPEC['items'][0], 'UNIT_NAME': SPEC['source_unit'], 'TIME': p, 'DATA_VALUE': '100'}
        for p in ['202607', '202608']]}}


class KoreaMacroTests(unittest.TestCase):
    def test_calendar_and_identity(self):
        self.assertEqual(month_offset('202601', -1), '202512')
        self.assertEqual(len(parse_history(response(), SPEC, '202607', '202610')), 2)
        p = response(); p['StatisticSearch']['row'][0]['ITEM_CODE2'] = 'different'
        with self.assertRaisesRegex(ValueError, 'identity'):
            parse_history(p, SPEC, '202607', '202610')

    def test_reject_bad_values_dates_units_and_truncation(self):
        for field, value in [('DATA_VALUE', 'NaN'), ('DATA_VALUE', 'Infinity'), ('TIME', '202613'), ('TIME', '202609'), ('UNIT_NAME', '2015=100')]:
            p = response(); p['StatisticSearch']['row'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                parse_history(p, SPEC, '202607', '202610')
        p = response(); p['StatisticSearch']['list_total_count'] = 3
        with self.assertRaises(ValueError): parse_history(p, SPEC, '202607', '202610')

    def test_missing_duplicate_or_future_month(self):
        for period in ['202607', '202610', '202611']:
            p = response(); p['StatisticSearch']['row'][1]['TIME'] = period
            with self.assertRaises(ValueError): parse_history(p, SPEC, '202607', '202610')

    def test_failure_retains_history_and_success_stamp(self):
        conn = sqlite3.connect(':memory:')
        now = datetime(2026, 10, 6, tzinfo=KST)
        history = [{'period': month_offset('202011', i), 'value': 100.0 + i} for i in range(70)]
        payload, failed = collect(conn, [SPEC], now, lambda *_: history)
        self.assertEqual(failed, 0)
        def fail(*_): raise ValueError('https://private/key/secret')
        later = datetime(2026, 10, 7, tzinfo=KST)
        payload, failed = collect(conn, [SPEC], later, fail)
        self.assertEqual(failed, 1)
        entry = payload['indicators'][0]
        self.assertEqual(entry['history'], history)
        self.assertEqual(entry['succeeded_at'], now.isoformat())
        self.assertEqual(entry['error'], 'collection_failed')
        self.assertNotIn('secret', json.dumps(payload))
        history[-1]['value'] = 222.0
        payload, failed = collect(conn, [SPEC], later, lambda *_: history)
        self.assertEqual(payload['indicators'][0]['history'][-1]['value'], 222.0)
        self.assertIsNone(payload['indicators'][0]['error'])
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM korea_macro_observation').fetchone()[0], 70)

    def test_regression_and_partial_series_failure(self):
        conn = sqlite3.connect(':memory:')
        now = datetime(2026, 10, 6, tzinfo=KST)
        history = [{'period': month_offset('202011', i), 'value': float(i)} for i in range(70)]
        second = {**SPEC, 'id': 'second'}
        collect(conn, [SPEC, second], now, lambda *_: history)
        def mixed(spec, *_): return history[:-1] if spec['id'] == SPEC['id'] else history
        payload, failed = collect(conn, [SPEC, second], now, mixed)
        self.assertEqual(failed, 1)
        self.assertEqual(payload['indicators'][0]['error'], 'source_regressed')
        self.assertIsNone(payload['indicators'][1]['error'])

    def test_js_calendar_signal_and_status(self):
        script = (ROOT / 'docs/korea_macro.js').read_text(encoding='utf-8') + '''
const assert = require('node:assert/strict');
assert.equal(krShift('202601', -1), '202512');
let h = [{period:'202501',value:100},{period:'202511',value:120},{period:'202601',value:110}];
let c = krChanges(h,h[2]);
assert.equal(c.mom,null); assert.ok(Math.abs(c.yoy-10)<1e-8);
assert.equal(krSignal({comparison:'delta',direction:-1},{delta:0.2}).label,'− 부정 신호');
assert.equal(krSignal({comparison:'delta',direction:-1},{delta:-0.2}).label,'＋ 긍정 신호');
assert.equal(krSignal({comparison:'yoy',direction:0},{yoy:3}).label,'맥락 확인');
const spec={history:[{period:'202608',value:100}],succeeded_at:'2026-10-06T09:00:00+09:00',lag_months:2};
const now=new Date('2026-10-06T10:00:00+09:00');
assert.equal(krStatus(spec,now),'정상 · 다음 발표 대기');
assert.equal(krStatus({...spec,error:'failed'},now),'수집 실패 · 기존 자료 유지');
assert.equal(krStatus({...spec,lag_months:1},now),'자료 지연 확인 필요');
assert.equal(krStatus(spec,new Date('2026-10-10T10:00:00+09:00')),'수집 확인 필요');
'''
        subprocess.run(['node', '-e', script], check=True, capture_output=True)

    def test_build_embeds_panel_and_escapes_payload(self):
        html = build_dashboard_html({'korea_macro': {'error': '</script><img onerror=1>'}})
        self.assertIn('id="tab-korea-macro"', html)
        self.assertIn('function krChanges(', html)
        self.assertNotIn('/* KOREA_MACRO_SCRIPT */', html)
        self.assertNotIn('</script><img onerror=1>', html)


if __name__ == '__main__':
    unittest.main()
