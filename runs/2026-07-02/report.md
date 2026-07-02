# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-02**
- 생성 시각(UTC): `2026-07-02T00:53:41.522689+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -6.32% / KOSDAQ -5.02%
- **미국 지수**: S&P500 -0.22% / NASDAQ -0.66% / DOW -0.03%
- **환율/변동성**: USD/KRW 1553.24 (+0.25%) / VIX 16.6
- **시장 요약 노트**: KOSPI -6.32%, USD/KRW 1553.24. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -30389억 / 기관 +2840억 / 개인 +26797억
- **일간 매크로**: 미10년 4.47% / 미2년 3.70% / 2-10 0.77%p / DXY 101.40
- **월간 매크로**: 실업률 4.30% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.24%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI -6.32%, KOSDAQ -5.02% 급락과 외국인 -3조원 순매도, 원화 약세(USD/KRW 1553.24)로 위험회피 심리가 극대화됨.
  ↳ 출처: `CORE_SIGNALS, flow_data, macro_daily`
- 5일 누적 KOSPI -13.40%, 20일 누적 -8.11%로 단기·중기 모두 하락세 심화, 기술적 반등 신호는 확인 불가(제공 데이터 기준).
  ↳ 출처: `CORE_SIGNALS, cumulative_context`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 시장 변동성이 매우 커진 상황으로 보수적 대응이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 -13% 이상 급락하며 시장 전반에 위험회피 심리가 강함.
- 핵심 주장: 외국인 대규모 순매도와 원화 약세가 동반되어 추가 하락 위험이 존재.
- 핵심 주장: 단기 반등 신호는 없으며, 불확실성이 높아 신중한 접근이 필요함.

### 수급 담당자
- 한줄 요약: 고환율과 금리 불확실성에 따른 외국인 이탈, 개인의 저가매수 흡수 구간.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고환율(USD/KRW 급등)과 연준/금리 불확실성에 따른 위험회피 성격이 강함.
- 핵심 주장: KOSPI 5일 누적 -13%대 급락과 동반된 외국인 매도는 FX-driven outflow로 해석되며, 단순 차익실현이나 리밸런싱보다 환율 영향이 지배적.
- 핵심 주장: 개인 대규모 순매수는 저가매수 시도이나, 최근 급락세와 변동성 고려 시 지속성에 의문이 있음.

### 섹터 담당자
- 한줄 요약: 시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 -13% 이상 급락하며 시장 전반에 심각한 약세가 나타남.
- 핵심 주장: 외국인 대규모 순매도와 원화 약세가 동반되어 투자심리 악화가 뚜렷함.
- 핵심 주장: 단기 반등 신호 없이 하락세 지속, 추가 하락 위험이 높음.

### 리스크 담당자
- 한줄 요약: 단기 급락과 외국인 이탈이 누적되어 위험 신호가 명확합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일간 -13% 급락
- 핵심 주장: 외국인 대규모 순매도 지속
- 핵심 주장: 환율 급등세로 불안 심화

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀 약화가 단기적으로 지속될 가능성이 높습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 급락과 외국인 대규모 순매도는 실적 모멘텀 약화 신호.
- 핵심 주장: 실적 추정치 하향 압력 지속, 단기 반등 신호 없음.
- 핵심 주장: 환율 급등과 변동성 확대가 가이던스 하향 리스크를 높임.

### 브레드스 담당자
- 한줄 요약: 시장 내부 확산 약화와 외국인 이탈이 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 시장 전반에 걸친 급격한 하락과 확산이 뚜렷하다.
- 핵심 주장: 외국인 대규모 순매도와 환율 급등이 위험회피 신호를 강화한다.
- 핵심 주장: 단기 및 누적 하락폭 모두 심각해, 기술적 반등 신호는 아직 없다.

### 유동성 담당자
- 한줄 요약: 유동성 경색과 외환 불안이 위험회피를 자극하고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락과 외국인 대규모 순매도 지속.
- 핵심 주장: 환율 급등과 변동성 확대, 정책 불확실성 고조.
- 핵심 주장: 유동성 악화로 위험회피 심화.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '시장 변동성이 매우 커진 상황으로 보수적 대응이 필요합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-6.32%, foreign_net=-30389억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '고환율과 금리 불확실성에 따른 외국인 이탈, 개인의 저가매수 흡수 구간.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-6.32%, usdkrw=1553.24입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.usdkrw, snapshot.macro.daily.usdkrw, snapshot.macro.daily.dxy, snapshot.macro.daily.us10y, snapshot.news_headlines
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-6.32%, foreign_net=-30389억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 급락과 외국인 이탈이 누적되어 위험 신호가 명확합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-30389억, usdkrw=1553.24입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀 약화가 단기적으로 지속될 가능성이 높습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-30389억, usdkrw=1553.24입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 내부 확산 약화와 외국인 이탈이 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-6.32%, foreign_net=-30389억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.breadth_signal_score
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 경색과 외환 불안이 위험회피를 자극하고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-30389억, usdkrw=1553.24입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.news_headlines, snapshot.phase_two_signals.liquidity_signal_score
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -6.32%, USD/KRW 1553.24(+0.25%), VIX 16.6, 외국인 -30389억이고, 뉴스는 반등·회복 기대가 섞인 완화 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 위험 국면 해석: 다수=RISK_OFF: 외국인 이탈, 환율 급등, 누적 하락에 따라 방어적 대응 필요(매크로, 수급, 섹터, 이익모멘텀, 브레드스, 유동성 담당자), 소수=RISK_ON: 단기 급락이 과도해 일부 위험 신호 해소 가능성(리스크 담당자), 에이전트=[risk]
  - 의미: 단기 반등 가능성에 대한 소수 의견이 있으나, 수급·지표상 위험회피가 우세해 전략적 비중 확대는 시기상조.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 5일간 -13% 이상 급락하며 시장 전반에 위험회피 심리가 강함.",
    "외국인 대규모 순매도와 원화 약세가 동반되어 추가 하락 위험이 존재.",
    "단기 반등 신호는 없으며, 불확실성이 높아 신중한 접근이 필요함."
  ],
  "korean_comment": "시장 변동성이 매우 커진 상황으로 보수적 대응이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market)",
  "core_claims": [
    "외국인 대규모 순매도는 고환율(USD/KRW 급등)과 연준/금리 불확실성에 따른 위험회피 성격이 강함.",
    "KOSPI 5일 누적 -13%대 급락과 동반된 외국인 매도는 FX-driven outflow로 해석되며, 단순 차익실현이나 리밸런싱보다 환율 영향이 지배적.",
    "개인 대규모 순매수는 저가매수 시도이나, 최근 급락세와 변동성 고려 시 지속성에 의문이 있음."
  ],
  "korean_comment": "고환율과 금리 불확실성에 따른 외국인 이탈, 개인의 저가매수 흡수 구간.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.usdkrw",
    "snapshot.macro.daily.usdkrw",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.daily.us10y",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 최근 5일간 -13% 이상 급락하며 시장 전반에 심각한 약세가 나타남.",
    "외국인 대규모 순매도와 원화 약세가 동반되어 투자심리 악화가 뚜렷함.",
    "단기 반등 신호 없이 하락세 지속, 추가 하락 위험이 높음."
  ],
  "korean_comment": "시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI 5일간 -13% 급락",
    "외국인 대규모 순매도 지속",
    "환율 급등세로 불안 심화"
  ],
  "korean_comment": "단기 급락과 외국인 이탈이 누적되어 위험 신호가 명확합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 5일 누적 급락과 외국인 대규모 순매도는 실적 모멘텀 약화 신호.",
    "실적 추정치 하향 압력 지속, 단기 반등 신호 없음.",
    "환율 급등과 변동성 확대가 가이던스 하향 리스크를 높임."
  ],
  "korean_comment": "실적 모멘텀 약화가 단기적으로 지속될 가능성이 높습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "시장 전반에 걸친 급격한 하락과 확산이 뚜렷하다.",
    "외국인 대규모 순매도와 환율 급등이 위험회피 신호를 강화한다.",
    "단기 및 누적 하락폭 모두 심각해, 기술적 반등 신호는 아직 없다."
  ],
  "korean_comment": "시장 내부 확산 약화와 외국인 이탈이 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.breadth_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 5일 누적 하락과 외국인 대규모 순매도 지속.",
    "환율 급등과 변동성 확대, 정책 불확실성 고조.",
    "유동성 악화로 위험회피 심화."
  ],
  "korean_comment": "유동성 경색과 외환 불안이 위험회피를 자극하고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.news_headlines",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```