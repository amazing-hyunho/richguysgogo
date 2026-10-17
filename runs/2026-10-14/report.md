# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-14**
- 생성 시각(UTC): `2026-10-14T00:52:46.594364+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=3, RISK_ON=1, RISK_OFF=3
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +1.65% / KOSDAQ +0.57%
- **미국 지수**: S&P500 -0.08% / NASDAQ -0.15% / DOW +0.03%
- **환율/변동성**: USD/KRW 1340.88 (-0.06%) / VIX 15.3
- **시장 요약 노트**: KOSPI 1.65%, USD/KRW 1340.88. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -1798억 / 기관 -414억 / 개인 +1184억
- **일간 매크로**: 미10년 5.22% / 미2년 4.06% / 2-10 1.16%p / DXY 102.17
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.71% / Core CPI YoY 2.76% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.20% / 기준금리 3.75% / 실질금리 2.89%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 6135.05로 1.65% 상승했지만 5일 -12.693%, 20일 -9.928%이며 반전 신호도 확인되지 않았습니다.
  ↳ 출처: `market_data, cumulative_context`
- 외국인 -1798억원, 기관 -414억원으로 매도 우위가 이어졌고 외국인 매도는 KOSDAQ에 -1590억원 집중됐습니다.
  ↳ 출처: `flow_data, korean_market_flow_breakdown`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표와 단기 시장 흐름이 엇갈려 신중한 접근이 필요합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 반등했으나 최근 20일 누적 하락폭이 여전히 큽니다.
- 핵심 주장: 한국 월별 지표는 심리·고용·수출은 긍정적이나 생산·소비는 부진하여 혼조입니다.
- 핵심 주장: 외국인 순매도와 수급 불안이 지속되어 단기 위험회피 심리가 남아 있습니다.

### 수급 담당자
- 한줄 요약: 외국인 매도세가 KOSDAQ에 집중되며, 개인이 단기 반등에 적극적으로 대응하는 구간입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 외국인 순매도는 KOSDAQ 중심으로, 고금리/연준, 반도체/AI, 고환율 이슈가 복합적으로 작용.
- 핵심 주장: KOSPI는 외국인 매도 약화, 개인은 KOSDAQ에서 레버리지성 추격매수 성격이 강함.
- 핵심 주장: 국내 변동성 직접 판단 제한적 (VKOSPI 미제공), 단기 반등에도 누적 하락폭 커 수급 불안정 지속.

### 섹터 담당자
- 한줄 요약: 단기 반등에도 불구하고 중기적으론 하락세와 수급 부담이 크다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 단기 급락(-12.7%) 이후 반등세이나, 20일 누적 하락폭이 여전히 크다.
- 핵심 주장: 외국인 순매도와 기관 매도세가 지속되어 수급은 부정적이다.
- 핵심 주장: 한국 경기지표는 혼조, 생산·소비 부진, 수출·고용은 긍정 신호가 혼재한다.

### 리스크 담당자
- 한줄 요약: 중기적으로 하락세와 수급 불안이 이어지고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락세 지속
- 핵심 주장: 생산·소비 지표 부진, 심리 지표는 개선
- 핵심 주장: 외국인 순매도 및 수급 불안정

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 전환 신호는 아직 뚜렷하지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락에도 실적 모멘텀 반전 신호 미약
- 핵심 주장: 외국인·기관 동반 순매도, 이익 추정치 상향 근거 부족
- 핵심 주장: 단기 반등은 수급·심리 영향, 실적 추세 개선 확인 안 됨

### 브레드스 담당자
- 한줄 요약: 지수 반등에도 시장 내부 확산과 수급은 여전히 미약합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 단기 반등에도 중기 하락세 지속
- 핵심 주장: 수급·확산 약화, 시장 전반 확실한 회복 신호 부족

### 유동성 담당자
- 한줄 요약: 유동성 환경이 보수적으로 유지되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락과 외국인 순매도 지속
- 핵심 주장: 달러/원 환율은 안정적이나 유동성 개선 신호 미약
- 핵심 주장: 정책·금리 불확실성 지속, 위험회피 심리 우세

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표와 단기 시장 흐름이 엇갈려 신중한 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+1.65%, foreign_net=-1798억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도세가 KOSDAQ에 집중되며, 개인이 단기 반등에 적극적으로 대응하는 구간입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+1.65%, dxy=102.17입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.macro.daily.us10y, snapshot.macro.daily.dxy, snapshot.news_headlines, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 반등에도 불구하고 중기적으론 하락세와 수급 부담이 크다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+1.65%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.korea_macro_context, snapshot.market_summary.kospi_change_pct
- [리스크 담당자] 저는 리스크 담당자 입장에서 '중기적으로 하락세와 수급 불안이 이어지고 있습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.korea_macro_context, snapshot.flow_summary.note, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 전환 신호는 아직 뚜렷하지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-1798억, institution_net=-414억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수 반등에도 시장 내부 확산과 수급은 여전히 미약합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-1798억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 환경이 보수적으로 유지되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-1798억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.macro.daily.vix, snapshot.phase_two_signals.liquidity_signal_score, snapshot.news_headlines
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +1.65%, USD/KRW 1340.88(-0.06%), VIX 15.3, 외국인 -1798억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 시장 위험 국면: 다수=매크로·수급·섹터 담당자는 중립, 이익모멘텀·브레드스·유동성 담당자는 위험회피에 가까운 신중론을 제시했습니다., 소수=리스크 담당자는 위험선호 태그를 제시했습니다., 에이전트=[리스크 담당자]
  - 의미: 리스크 담당자의 세부 근거도 누적 하락과 수급 불안을 지적해 태그와 주장 사이에 충돌이 있으며, 공격적 비중 확대 근거로 사용하기 어렵습니다.
- 당일 상승의 의미: 다수=대다수는 KOSPI 1.65% 상승을 누적 하락 이후의 단기 반등으로 평가했습니다., 소수=명시적인 추세 전환 주장은 없으며 위험선호 해석만 제한적으로 존재합니다., 에이전트=[리스크 담당자]
  - 의미: 외국인·기관 동반 매도와 반전 신호 부재가 이어져 지수 상승만으로 중기 방향을 바꾸면 추격 위험이 커집니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 단기 반등했으나 최근 20일 누적 하락폭이 여전히 큽니다.",
    "한국 월별 지표는 심리·고용·수출은 긍정적이나 생산·소비는 부진하여 혼조입니다.",
    "외국인 순매도와 수급 불안이 지속되어 단기 위험회피 심리가 남아 있습니다."
  ],
  "korean_comment": "중기 지표와 단기 시장 흐름이 엇갈려 신중한 접근이 필요합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인 순매도는 KOSDAQ 중심으로, 고금리/연준, 반도체/AI, 고환율 이슈가 복합적으로 작용.",
    "KOSPI는 외국인 매도 약화, 개인은 KOSDAQ에서 레버리지성 추격매수 성격이 강함.",
    "국내 변동성 직접 판단 제한적 (VKOSPI 미제공), 단기 반등에도 누적 하락폭 커 수급 불안정 지속."
  ],
  "korean_comment": "외국인 매도세가 KOSDAQ에 집중되며, 개인이 단기 반등에 적극적으로 대응하는 구간입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 단기 급락(-12.7%) 이후 반등세이나, 20일 누적 하락폭이 여전히 크다.",
    "외국인 순매도와 기관 매도세가 지속되어 수급은 부정적이다.",
    "한국 경기지표는 혼조, 생산·소비 부진, 수출·고용은 긍정 신호가 혼재한다."
  ],
  "korean_comment": "단기 반등에도 불구하고 중기적으론 하락세와 수급 부담이 크다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.korea_macro_context",
    "snapshot.market_summary.kospi_change_pct"
  ],
  "confidence": "MED"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI 20일 누적 하락세 지속",
    "생산·소비 지표 부진, 심리 지표는 개선",
    "외국인 순매도 및 수급 불안정"
  ],
  "korean_comment": "중기적으로 하락세와 수급 불안이 이어지고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 20일 누적 하락에도 실적 모멘텀 반전 신호 미약",
    "외국인·기관 동반 순매도, 이익 추정치 상향 근거 부족",
    "단기 반등은 수급·심리 영향, 실적 추세 개선 확인 안 됨"
  ],
  "korean_comment": "실적 추정치 상향 전환 신호는 아직 뚜렷하지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.kospi_change_pct",
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
    "KOSPI 단기 반등에도 중기 하락세 지속",
    "수급·확산 약화, 시장 전반 확실한 회복 신호 부족"
  ],
  "korean_comment": "지수 반등에도 시장 내부 확산과 수급은 여전히 미약합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 20일 누적 하락과 외국인 순매도 지속",
    "달러/원 환율은 안정적이나 유동성 개선 신호 미약",
    "정책·금리 불확실성 지속, 위험회피 심리 우세"
  ],
  "korean_comment": "유동성 환경이 보수적으로 유지되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.vix",
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```