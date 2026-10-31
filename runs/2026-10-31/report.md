# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-31**
- 생성 시각(UTC): `2026-10-31T00:52:17.566189+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.48% / KOSDAQ -3.83%
- **미국 지수**: S&P500 -1.82% / NASDAQ -2.86% / DOW -1.09%
- **환율/변동성**: USD/KRW 1338.04 (-0.41%) / VIX 19.4
- **시장 요약 노트**: KOSPI -3.48%, USD/KRW 1338.04. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -16360억 / 기관 +6149억 / 개인 +7677억
- **일간 매크로**: 미10년 4.93% / 미2년 3.97% / 2-10 0.96%p / DXY 101.96
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 3.40% / 기준금리 3.75% / 실질금리 2.59%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI -3.48%, KOSDAQ -3.83%와 외국인 -1조6360억원이 핵심 약세 신호이며, 기관·개인의 매수만으로는 수급 균형을 회복하지 못했다.
  ↳ 출처: `market_data, flow_data`
- AI 실적 실망과 연준 추가 인상 가능성이 위험회피를 강화했다. VIX 19.42는 5일 평균 18.32보다 높고 반전 신호도 없다.
  ↳ 출처: `macro_daily, news, cumulative_context`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 시장 충격과 월별 실물지표 개선이 동시에 나타나 신중한 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고, 외국인 순매도도 지속되어 단기 위험회피 심리가 강합니다.
- 핵심 주장: 한국 9월 생산·소비·투자·수출 등 실물지표는 긍정적이나, 경기·심리지표는 혼조로 중기 개선 신호가 확실하지 않습니다.
- 핵심 주장: 일별 급락과 월별 실물지표 개선이 상충하며, 단기 변동성 확대 구간으로 판단됩니다.

### 수급 담당자
- 한줄 요약: 외국인 주도 대규모 매도세에 개인 저가매수 유입, 수급 불균형 심화.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 반도체/AI 실적 실망과 글로벌 기술주 투매, 연준 금리 불확실성(금리/연준), 정책 리스크(관세/정책) 등 복합 악재에 따른 위험회피 성격이 강함.
- 핵심 주장: USD/KRW는 소폭 하락했으나, 최근 5일간 상승세(고환율)와 맞물려 외국인 매도는 FX-driven 보다는 글로벌 리스크 오프와 포트폴리오 리밸런싱(특히 KOSPI 중심) 영향이 큼.
- 핵심 주장: 개인 매수는 대형주 급락에 따른 저가매수 시도이나, 20일 누적 KOSPI -25%의 하락 추세와 변동성 확대(VIX), VKOSPI 미제공 상황에서 지속성은 제한적.

### 섹터 담당자
- 한줄 요약: 단기 약세와 수급 불안이 뚜렷하게 나타납니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고 단기 반등 신호는 약함.
- 핵심 주장: 외국인 대규모 순매도와 시장 변동성 확대가 지속됨.
- 핵심 주장: 중기 한국 경기지표는 혼조이나 생산·소비·수출은 긍정적임.

### 리스크 담당자
- 한줄 요약: 단기 급락과 외국인 매도세가 위험 신호로 판단됩니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 -25%로 하락세 지속
- 핵심 주장: 외국인 대규모 순매도와 시장 급락
- 핵심 주장: 중기 한국 경기지표는 혼조

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 하향 압력이 지속될 가능성이 높아 보입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 약화 신호가 누적되고 있습니다.
- 핵심 주장: 외국인 대규모 순매도와 시장 급락은 단기 충격을 넘어 구조적 우려를 반영합니다.

### 브레드스 담당자
- 한줄 요약: 시장 전반의 하락 확산과 수급 악화가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큽니다.
- 핵심 주장: 시장 내 확산도 약화와 외국인 대규모 순매도 지속이 확인됩니다.
- 핵심 주장: 단기 반전 신호는 아직 감지되지 않습니다.

### 유동성 담당자
- 한줄 요약: 정책·유동성 환경이 단기적으로 위험회피(Risk-off)로 전환되었습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 -25%로 유동성 경색 신호가 뚜렷합니다.
- 핵심 주장: 외국인 대규모 순매도와 변동성(VIX) 상승이 위험회피 심리를 강화합니다.
- 핵심 주장: 달러 약세에도 국내 유동성 개선 신호는 미약합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 시장 충격과 월별 실물지표 개선이 동시에 나타나 신중한 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-16360억, kospi_change_pct=-3.48%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.korea_macro_context, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 주도 대규모 매도세에 개인 저가매수 유입, 수급 불균형 심화.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.48%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.news_headlines, snapshot.macro.daily.vix, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 약세와 수급 불안이 뚜렷하게 나타납니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-16360억, vix=19.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct, snapshot.markets.volatility.vix, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 급락과 외국인 매도세가 위험 신호로 판단됩니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-16360억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct, snapshot.korea_macro_context
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 하향 압력이 지속될 가능성이 높아 보입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-16360억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 하락 확산과 수급 악화가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-16360억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책·유동성 환경이 단기적으로 위험회피(Risk-off)로 전환되었습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-16360억, vix=19.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg, snapshot.market_summary.usdkrw, snapshot.macro.daily.dxy
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.48%, USD/KRW 1338.04(-0.41%), VIX 19.4, 외국인 -16360억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 국면 분류: 다수=7명 중 6명은 외국인 매도, 지수 급락, 변동성 상승을 근거로 리스크 오프로 분류했다., 소수=리스크 담당자는 RISK_ON 태그를 제시했지만 실제 설명은 급락과 외국인 매도를 위험 신호로 평가해 태그와 논지가 상충했다., 에이전트=[risk]
  - 의미: 소수 태그보다 구체적 근거와 다수 의견을 우선해야 하며, 공격적 위험선호 전환의 근거로 해석해서는 안 된다.
- 약세의 지속성: 다수=다수는 단기 수급 불안과 반전 신호 부재를 강조했다., 소수=이익모멘텀 담당자는 단기 충격을 넘어 실적 추정치 하향과 구조적 우려로 이어질 가능성을 더 강하게 제기했다., 에이전트=[earnings]
  - 의미: 실적 하향이 실제 수치로 확인되면 단순 기술적 조정이 아닌 중기 약세로 판단을 강화해야 한다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고, 외국인 순매도도 지속되어 단기 위험회피 심리가 강합니다.",
    "한국 9월 생산·소비·투자·수출 등 실물지표는 긍정적이나, 경기·심리지표는 혼조로 중기 개선 신호가 확실하지 않습니다.",
    "일별 급락과 월별 실물지표 개선이 상충하며, 단기 변동성 확대 구간으로 판단됩니다."
  ],
  "korean_comment": "단기 시장 충격과 월별 실물지표 개선이 동시에 나타나 신중한 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.korea_macro_context",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
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
    "외국인 대규모 순매도는 반도체/AI 실적 실망과 글로벌 기술주 투매, 연준 금리 불확실성(금리/연준), 정책 리스크(관세/정책) 등 복합 악재에 따른 위험회피 성격이 강함.",
    "USD/KRW는 소폭 하락했으나, 최근 5일간 상승세(고환율)와 맞물려 외국인 매도는 FX-driven 보다는 글로벌 리스크 오프와 포트폴리오 리밸런싱(특히 KOSPI 중심) 영향이 큼.",
    "개인 매수는 대형주 급락에 따른 저가매수 시도이나, 20일 누적 KOSPI -25%의 하락 추세와 변동성 확대(VIX), VKOSPI 미제공 상황에서 지속성은 제한적."
  ],
  "korean_comment": "외국인 주도 대규모 매도세에 개인 저가매수 유입, 수급 불균형 심화.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.vix",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.usdkrw"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고 단기 반등 신호는 약함.",
    "외국인 대규모 순매도와 시장 변동성 확대가 지속됨.",
    "중기 한국 경기지표는 혼조이나 생산·소비·수출은 긍정적임."
  ],
  "korean_comment": "단기 약세와 수급 불안이 뚜렷하게 나타납니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.korea_macro_context"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK pre-analysis agent",
  "core_claims": [
    "KOSPI 20일 누적 -25%로 하락세 지속",
    "외국인 대규모 순매도와 시장 급락",
    "중기 한국 경기지표는 혼조"
  ],
  "korean_comment": "단기 급락과 외국인 매도세가 위험 신호로 판단됩니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.korea_macro_context"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 약화 신호가 누적되고 있습니다.",
    "외국인 대규모 순매도와 시장 급락은 단기 충격을 넘어 구조적 우려를 반영합니다."
  ],
  "korean_comment": "실적 추정치 하향 압력이 지속될 가능성이 높아 보입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 큽니다.",
    "시장 내 확산도 약화와 외국인 대규모 순매도 지속이 확인됩니다.",
    "단기 반전 신호는 아직 감지되지 않습니다."
  ],
  "korean_comment": "시장 전반의 하락 확산과 수급 악화가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
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
    "KOSPI 20일 누적 -25%로 유동성 경색 신호가 뚜렷합니다.",
    "외국인 대규모 순매도와 변동성(VIX) 상승이 위험회피 심리를 강화합니다.",
    "달러 약세에도 국내 유동성 개선 신호는 미약합니다."
  ],
  "korean_comment": "정책·유동성 환경이 단기적으로 위험회피(Risk-off)로 전환되었습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.market_summary.usdkrw",
    "snapshot.macro.daily.dxy"
  ],
  "confidence": "HIGH"
}
```