# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-06**
- 생성 시각(UTC): `2026-07-06T00:53:31.339885+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.
- **국면 투표**: NEUTRAL=5, RISK_ON=1, RISK_OFF=1
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 확인된 모멘텀 주도주 중심으로 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] 변동성 한도를 기준으로 포지션 규모를 조절합니다.
- [OpsGuidanceLevel.AVOID/회피] 과열된 돌파 구간 추격 매수는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +2.34% / KOSDAQ -1.72%
- **미국 지수**: S&P500 +0.00% / NASDAQ -0.80% / DOW +1.14%
- **환율/변동성**: USD/KRW 1530.98 (-0.05%) / VIX 16.1
- **시장 요약 노트**: KOSPI 2.34%, USD/KRW 1530.98. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -2715억 / 기관 -2372억 / 개인 +4758억
- **일간 매크로**: 미10년 4.49% / 미2년 3.67% / 2-10 0.82%p / DXY 100.86
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.26%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_ON.
  ↳ 출처: `regime_tuner`
- KOSPI는 +2.34% 급등(8277.7pt)했으나, 외국인(-2715억)·기관(-2372억) 동반 순매도, 개인만 +4758억 순매수.
  ↳ 출처: `flow_data, macro_daily`
- USD/KRW 환율은 1530.98원(-0.05%)로 고점 유지, VIX는 16.1로 안정적이나, 최근 5일간 KOSPI는 -0.86%로 단기 변동성 확대.
  ↳ 출처: `macro_daily, flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 반등에도 불구하고 외국인 매도와 변동성에 유의해야 합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 강한 상승세를 보였으나 단기 변동성도 큽니다.
- 핵심 주장: 외국인과 기관의 순매도세가 지속되고 있어 유입 모멘텀은 약합니다.
- 핵심 주장: 거시지표와 시장 흐름을 종합하면 신중한 접근이 필요합니다.

### 수급 담당자
- 한줄 요약: 외국인 차익실현 매물에 개인이 적극적으로 유입되는 구간입니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: 외국인 순매도는 KOSDAQ에서 집중적으로 발생, KOSPI는 상대적으로 약함.
- 핵심 주장: 핵심 키워드: 고환율, 금리/연준, 반도체/AI, 인플레이션.
- 핵심 주장: 외국인 매도는 최근 KOSPI 20일 누적 강세(12.24%)에 따른 차익실현 성격이 강하며, 개인 매수는 레버리지 추종 가능성 높음.

### 섹터 담당자
- 한줄 요약: 개인 투자자의 강한 매수세가 시장을 지지하고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 12% 이상 상승하며 강한 상승세를 보임.
- 핵심 주장: 외국인과 기관의 동반 순매도에도 불구하고 개인 매수세가 시장을 견인.
- 핵심 주장: 단기 변동성은 높으나, 중기적으로는 상승 모멘텀이 유지됨.

### 리스크 담당자
- 한줄 요약: 단기 변동성은 있으나 중장기 위험 신호는 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 12% 이상 상승
- 핵심 주장: 5일간 변동성은 크지만 반전 신호 없음
- 핵심 주장: 외국인 순매도와 개인 순매수 집중

### 이익모멘텀 담당자
- 한줄 요약: 실적 추세 개선 신호는 아직 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀 신호는 부재하며, 최근 강한 상승은 실적 상향과 무관함.
- 핵심 주장: 외국인·기관 매도세와 5일간 KOSPI 약세는 실적 기대 약화로 해석됨.
- 핵심 주장: 20일 누적 강세는 단기적 유동성 효과로, 실적 추세 변화는 확인되지 않음.

### 브레드스 담당자
- 한줄 요약: 지수 급등에도 내부 확산은 약해 신중함이 필요합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 단기 급등 후 변동성 확대 구간에 진입했습니다.
- 핵심 주장: KOSDAQ와 외국인 수급은 약세로, 시장 확산도는 제한적입니다.

### 유동성 담당자
- 한줄 요약: 유동성 환경이 뚜렷이 개선되지 않아 신중한 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인과 기관의 순매도, 환율 1530원대 유지로 유동성 개선 신호 미약.
- 핵심 주장: VIX와 변동성 지표는 안정적이나, 최근 5일간 KOSPI는 약세 흐름.
- 핵심 주장: 정책·금리 불확실성 지속, 보수적 유동성 환경.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 5명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 반등에도 불구하고 외국인 매도와 변동성에 유의해야 합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-2715억, institution_net=-2372억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.flow_summary.retail_net, snapshot.markets.volatility.vix, snapshot.macro.daily.vix
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 차익실현 매물에 개인이 적극적으로 유입되는 구간입니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1530.98입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.macro.daily.vix
- [섹터 담당자] 저는 섹터 담당자 입장에서 '개인 투자자의 강한 매수세가 시장을 지지하고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.34%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note, snapshot.market_summary.kospi_change_pct
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 변동성은 있으나 중장기 위험 신호는 뚜렷하지 않습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.flow_summary.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추세 개선 신호는 아직 뚜렷하지 않습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.market_summary.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수 급등에도 내부 확산은 약해 신중함이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-2715억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kosdaq_pct, snapshot.phase_two_signals.breadth_signal_score
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 환경이 뚜렷이 개선되지 않아 신중한 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-2715억, institution_net=-2372억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.macro.daily.vix
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +2.34%, USD/KRW 1530.98(-0.05%), VIX 16.1, 외국인 -2715억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 시장 모멘텀 해석: 다수=외국인·기관 매도와 단기 변동성 확대를 근거로 신중한 중립 기조 유지, 소수=섹터 담당자·유동성 담당자는 각각 개인 매수세에 의한 상승 지속, 유동성 악화에 따른 리스크 확대를 강조, 에이전트=[sector, liquidity]
  - 의미: 개인 매수세가 시장을 단기적으로 지지할 수 있으나, 유동성 환경과 외국인 수급이 뒷받침되지 않으면 반전 위험이 상존

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 최근 20일간 강한 상승세를 보였으나 단기 변동성도 큽니다.",
    "외국인과 기관의 순매도세가 지속되고 있어 유입 모멘텀은 약합니다.",
    "거시지표와 시장 흐름을 종합하면 신중한 접근이 필요합니다."
  ],
  "korean_comment": "단기 반등에도 불구하고 외국인 매도와 변동성에 유의해야 합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.flow_summary.retail_net",
    "snapshot.markets.volatility.vix",
    "snapshot.macro.daily.vix",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market)",
  "core_claims": [
    "외국인 순매도는 KOSDAQ에서 집중적으로 발생, KOSPI는 상대적으로 약함.",
    "핵심 키워드: 고환율, 금리/연준, 반도체/AI, 인플레이션.",
    "외국인 매도는 최근 KOSPI 20일 누적 강세(12.24%)에 따른 차익실현 성격이 강하며, 개인 매수는 레버리지 추종 가능성 높음."
  ],
  "korean_comment": "외국인 차익실현 매물에 개인이 적극적으로 유입되는 구간입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.vix",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 최근 20일간 12% 이상 상승하며 강한 상승세를 보임.",
    "외국인과 기관의 동반 순매도에도 불구하고 개인 매수세가 시장을 견인.",
    "단기 변동성은 높으나, 중기적으로는 상승 모멘텀이 유지됨."
  ],
  "korean_comment": "개인 투자자의 강한 매수세가 시장을 지지하고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.note",
    "snapshot.market_summary.kospi_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI가 최근 20일간 12% 이상 상승",
    "5일간 변동성은 크지만 반전 신호 없음",
    "외국인 순매도와 개인 순매수 집중"
  ],
  "korean_comment": "단기 변동성은 있으나 중장기 위험 신호는 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.flow_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 신호는 부재하며, 최근 강한 상승은 실적 상향과 무관함.",
    "외국인·기관 매도세와 5일간 KOSPI 약세는 실적 기대 약화로 해석됨.",
    "20일 누적 강세는 단기적 유동성 효과로, 실적 추세 변화는 확인되지 않음."
  ],
  "korean_comment": "실적 추세 개선 신호는 아직 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.market_summary.note"
  ],
  "confidence": "MED"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "breadth_technical_preanalysis",
  "core_claims": [
    "KOSPI는 단기 급등 후 변동성 확대 구간에 진입했습니다.",
    "KOSDAQ와 외국인 수급은 약세로, 시장 확산도는 제한적입니다."
  ],
  "korean_comment": "지수 급등에도 내부 확산은 약해 신중함이 필요합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.phase_two_signals.breadth_signal_score"
  ],
  "confidence": "MED"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "외국인과 기관의 순매도, 환율 1530원대 유지로 유동성 개선 신호 미약.",
    "VIX와 변동성 지표는 안정적이나, 최근 5일간 KOSPI는 약세 흐름.",
    "정책·금리 불확실성 지속, 보수적 유동성 환경."
  ],
  "korean_comment": "유동성 환경이 뚜렷이 개선되지 않아 신중한 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.macro.daily.vix",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```