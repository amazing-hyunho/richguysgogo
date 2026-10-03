from datetime import date
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import build_dashboard as dashboard


class Today(date):
    @classmethod
    def today(cls):
        return cls(2026,10,3)


def meeting(tag='NEUTRAL'):
    return {'round_index':1,'round_conclusion':'저장된 결론',
            'minutes':[{'speaker':'macro','summary':'원래 발언','internal_regime_tag':tag}]}


class MeetingRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.patches=[patch.object(dashboard,'RUNS_DIR',self.root),patch.object(dashboard,'date',Today)]
        for p in self.patches:p.start()

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()

    def write(self,path,payload):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(payload),encoding='utf-8')

    def test_without_today_keeps_last_valid_meeting_and_marks_old(self):
        self.write('2026-10-02.json',{'debate_round':meeting()})
        result=dashboard.load_latest_debate_minutes()
        self.assertEqual(result['market_date'],'2026-10-02')
        self.assertTrue(result['stale'])
        self.assertEqual(len(result['minutes']),1)

    def test_missing_combined_file_recovers_saved_artifact(self):
        self.write('2026-10-03/debate_round.json',meeting('RISK_OFF'))
        self.write('2026-10-03/stances.json',[{'agent_name':'macro','korean_comment':'오늘 의견','core_claims':['근거']}])
        result=dashboard.load_latest_debate_minutes()
        self.assertEqual(result['source'],'saved_artifact')
        self.assertEqual(result['minutes'][0]['internal_regime_tag'],'RISK_OFF')
        self.assertEqual(result['minutes'][0]['headline'],'오늘 의견')
        self.assertFalse(result['stale'])

    def test_broken_current_json_recovers_its_artifact(self):
        (self.root/'2026-10-03.json').write_text('{broken',encoding='utf-8')
        self.write('2026-10-03/debate_round.json',meeting())
        self.assertEqual(dashboard.load_latest_debate_minutes()['source'],'saved_artifact')

    def test_missing_debate_skips_to_older_without_inventing_a_meeting(self):
        self.write('2026-10-03.json',{'stances':[{'agent_name':'macro','regime_tag':'RISK_ON'}]})
        self.write('2026-10-02.json',{'debate_round':meeting('RISK_OFF')})
        result=dashboard.load_latest_debate_minutes()
        self.assertEqual(result['market_date'],'2026-10-02')
        self.assertEqual(result['minutes'][0]['internal_regime_tag'],'RISK_OFF')

    def test_unknown_tag_is_not_defaulted_to_neutral(self):
        value=meeting();value['minutes'][0].pop('internal_regime_tag')
        self.write('2026-10-03.json',{'debate_round':value})
        self.assertIsNone(dashboard.load_latest_debate_minutes()['minutes'][0]['internal_regime_tag'])

    def test_timeline_ignores_future_and_empty_records(self):
        for day in ('2026-10-01','2026-10-02','2026-10-03','2099-01-01'):
            self.write(day+'.json',{'debate_round':meeting()})
        self.assertEqual([x['market_date'] for x in dashboard.load_recent_meeting_timeline(2)],['2026-10-03','2026-10-02'])
        self.assertEqual(dashboard.load_recent_meeting_timeline(0),[])

    @unittest.skipUnless(shutil.which('node'),'Node required for display function regression')
    def test_display_votes_history_selection_and_escaping(self):
        template=dashboard.TEMPLATE_PATH.read_text(encoding='utf-8')
        helpers=template[template.index('  function meetingOpinion('):template.index('  // ── V2 전략 가이드 탭')]
        escape=template[template.index('function escapeHtml('):template.index('\nfunction ',template.index('function escapeHtml(')+1)]
        code='''const assert = require('node:assert/strict');
        const elements={};
        const document={getElementById:id=>elements[id]||(elements[id]={addEventListener:(event,fn)=>elements[id].handler=fn})};
        function safeArr(x){return Array.isArray(x)?x:[];}
        '''+escape+helpers+'''
        assert.equal(meetingVoteSummary([{internal_regime_tag:'RISK_ON'},{internal_regime_tag:'RISK_OFF'}]).key,'mixed');
        assert.equal(meetingVoteSummary([{}]).key,'unknown');
        const latest={market_date:'2026-10-03',generated_at:'2026-10-03T00:52:27Z',minutes:[{speaker:'risk',headline:'<img src=x onerror=alert(1)>',summary:'today',internal_regime_tag:'RISK_OFF'}]};
        const previous={market_date:'2026-10-02',minutes:[{speaker:'macro',summary:'previous',internal_regime_tag:'RISK_ON'}]};
        renderCommitteeMinutes(latest,[previous]);
        assert.ok(elements['v2-minutes'].innerHTML.includes('부정 1명'));
        assert.ok(elements['v2-minutes'].innerHTML.includes('&lt;img'));
        assert.ok(!elements['v2-minutes'].innerHTML.includes('<img'));
        elements['meeting-date-select'].handler({target:{value:'1'}});
        assert.ok(elements['v2-minutes'].innerHTML.includes('previous'));
        assert.ok(elements['v2-minutes'].innerHTML.includes('선택한 과거 회의'));
        assert.ok(elements['meeting-status'].innerHTML.includes('긍정 우세'));
        renderCommitteeMinutes({},[]);
        assert.equal(elements['meeting-status'].textContent,'기록 없음');
        '''
        script=self.root/'test.js';script.write_text(code,encoding='utf-8')
        result=subprocess.run(['node',str(script)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':
    unittest.main()
