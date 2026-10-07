from datetime import datetime
import json
from pathlib import Path
import unittest

from committee.core.korea_macro_context import build_context, KST
from committee.agents.llm_chair import LLMChairAgent
from committee.agents.llm_pre_analysis import LLMPreAnalysisAgent
from committee.agents.macro_stub import MacroStub
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName

ROOT = Path(__file__).resolve().parents[1]


class MacroContextTests(unittest.TestCase):
    def payload(self):
        p = json.loads((ROOT / 'runs/korea_macro/latest.json').read_text(encoding='utf-8'))
        for s in p['indicators']:
            s['succeeded_at'] = '2026-10-07T09:50:00+09:00'
            s['error'] = None
        return p

    def test_current_and_inverse_direction(self):
        p = self.payload()
        s = next(x for x in p['indicators'] if x['id'] == 'kr_unemployment')
        s['history'] = [{'period':'202607','value':3}, {'period':'202608','value':2.8}]
        c = build_context(p, datetime(2026,10,7,10,tzinfo=KST))
        self.assertEqual(c['available'], 12)
        e = next(x for x in c['evidence'] if x['id'] == 'kr_unemployment')
        self.assertEqual(e['signal'], '긍정')
        self.assertEqual(e['change_unit'], '%p')
        self.assertTrue(all(x['signal'] == '맥락 확인' for x in c['evidence'] if x['id'] in ['kr_cpi','kr_ppi']))

    def test_no_future_or_stale_context(self):
        for moment in [datetime(2026,10,6,tzinfo=KST), datetime(2026,10,12,tzinfo=KST)]:
            c = build_context(self.payload(), moment)
            self.assertEqual(c['available'], 0)
            self.assertEqual(len(c['excluded']),12)

    def test_failure_and_missing_comparison_excluded(self):
        p = self.payload()
        p['indicators'][0]['error'] = 'failed'
        p['indicators'][1]['history'] = [{'period':'202608','value':100}]
        c = build_context(p, datetime(2026,10,7,10,tzinfo=KST))
        self.assertEqual(c['available'],10)
        self.assertEqual(len(c['excluded']),2)

    def test_context_reaches_both_agent_prompts(self):
        raw = json.loads((ROOT / 'runs/2026-10-03/snapshot.json').read_text(encoding='utf-8'))
        snapshot = Snapshot.model_validate(raw)
        self.assertEqual(snapshot.korea_macro_context,{})
        snapshot.korea_macro_context = build_context(self.payload(), datetime(2026,10,7,10,tzinfo=KST))
        prompt = json.loads(LLMPreAnalysisAgent(AgentName.MACRO, MacroStub())._build_user_prompt(snapshot))
        self.assertEqual(prompt['snapshot']['korea_macro_context']['available'],12)
        self.assertIn('snapshot.korea_macro_context',prompt['allowed_evidence_ids'])
        chair = json.loads(LLMChairAgent._user_prompt(snapshot, []))
        self.assertEqual(chair['indicator_context']['korea_macro_context']['available'],12)
        self.assertIn('한국 월별 지표', MacroStub().run(snapshot).core_claims[-1])


if __name__ == '__main__': unittest.main()
