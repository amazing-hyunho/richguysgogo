# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-24**
- 생성 시각(UTC): `2026-07-24T00:52:23.310639+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.41% / KOSDAQ -3.00%
- **미국 지수**: S&P500 -1.21% / NASDAQ -2.15% / DOW -0.97%
- **환율/변동성**: USD/KRW 1478.49 (-0.38%) / VIX 18.7
- **시장 요약 노트**: KOSPI -3.41%, USD/KRW 1478.49. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -9448억 / 기관 -4468억 / 개인 +14099억
- **일간 매크로**: 미10년 4.70% / 미2년 3.80% / 2-10 0.90%p / DXY 101.44
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.73% / Core CPI YoY 2.81% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.42%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI -3.41%, KOSDAQ -3.0% 급락과 외국인 -9448억 순매도, 기관도 동반 매도하며 개인만 대규모 매수로 대응.
  ↳ 출처: `CORE_SIGNALS, flow_data, macro_daily`
- USD/KRW 1478.49로 고환율 지속, VIX 18.7로 변동성 확대, 20일 누적 KOSPI -24.86%로 하락세 심화.
  ↳ 출처: `CORE_SIGNALS, macro_daily, news`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 시장 전반에 위험회피 분위기가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 크게 하락하며 약세장이 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도와 변동성 지표 상승이 위험회피 심리를 반영합니다.
- 핵심 주장: 환율과 글로벌 불확실성도 부담 요인으로 작용하고 있습니다.

### 수급 담당자
- 한줄 요약: 공급 우위의 외국인 매도세에 개인이 단기적으로 흡수하는 불안정한 수급 구간입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고환율, 연준/금리, 경기/성장 둔화 우려가 복합적으로 작용.
- 핵심 주장: KOSPI에서 외국인 매도 집중, USD/KRW 상승과 동반된 FX-driven 유출이 주된 원인.
- 핵심 주장: 개인 매수는 레버리지 추격성 성격이 강하며, 20일 누적 하락세 속 지속성에 의문.

### 섹터 담당자
- 한줄 요약: 시장 전반에 걸친 강한 매도세와 변동성 확대가 우려됩니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 약 -25% 급락하며 시장 전반에 심각한 약세가 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나며 투자심리가 크게 위축되었습니다.
- 핵심 주장: 환율 급등과 글로벌 불확실성으로 추가 하락 위험이 높아진 상황입니다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 구조적 위험 신호가 뚜렷합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큼
- 핵심 주장: 외국인 대규모 순매도 지속
- 핵심 주장: 단기 반전 신호는 없음

### 이익모멘텀 담당자
- 한줄 요약: 20일 누적 하락과 외국인 매도세로 실적 전망이 악화되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 약화가 지속되고 있습니다.
- 핵심 주장: 추가적인 실적 하향 조정 위험이 큽니다.

### 브레드스 담당자
- 한줄 요약: 시장 내부 확산 약화와 하락 추세가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 시장 하락세가 광범위하게 확산되고 있음.
- 핵심 주장: 20일 누적 하락폭이 매우 크고, 반전 신호는 없음.

### 유동성 담당자
- 한줄 요약: 유동성 악화와 외국인 이탈로 위험회피 국면입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큽니다.
- 핵심 주장: 외국인 대규모 순매도와 변동성 상승이 확인됩니다.
- 핵심 주장: 정책 및 환율 불확실성으로 유동성 위축이 뚜렷합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '시장 전반에 위험회피 분위기가 강하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.41%, foreign_net=-9448억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.volatility.vix, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.note, snapshot.news_headlines
- [수급 담당자] 저는 수급 담당자 입장에서 '공급 우위의 외국인 매도세에 개인이 단기적으로 흡수하는 불안정한 수급 구간입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.41%, usdkrw=1478.49입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 걸친 강한 매도세와 변동성 확대가 우려됩니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.41%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note, snapshot.markets.fx.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.vix_5d_avg
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 구조적 위험 신호가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-9448억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.note, snapshot.markets.kr.kospi_pct
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '20일 누적 하락과 외국인 매도세로 실적 전망이 악화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-9448억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.note, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 내부 확산 약화와 하락 추세가 뚜렷합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.breadth_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.markets.kr.kospi_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 악화와 외국인 이탈로 위험회피 국면입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-9448억, kospi_change_pct=-3.41%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.kospi_change_pct, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.macro.daily.usdkrw, snapshot.news_headlines
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.41%, USD/KRW 1478.49(-0.38%), VIX 18.7, 외국인 -9448억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 구조적 위험 신호 해석: 다수=RISK_OFF: 외국인 매도와 누적 하락, 변동성 확대에 따라 위험회피 국면 진입., 소수=RISK_ON: 구조적 위험 신호가 뚜렷하나, 단기 반전 신호 부재로 즉각적 방향 전환은 유보., 에이전트=[risk]
  - 의미: 구조적 위험 신호 해석에 따라 추가 하락 대비 전략과 저점 매수 시점 판단이 달라질 수 있음.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 20일간 크게 하락하며 약세장이 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도와 변동성 지표 상승이 위험회피 심리를 반영합니다.",
    "환율과 글로벌 불확실성도 부담 요인으로 작용하고 있습니다."
  ],
  "korean_comment": "시장 전반에 위험회피 분위기가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.note",
    "snapshot.news_headlines",
    "snapshot.macro.daily.usdkrw"
  ],
  "confidence": "HIGH"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인 대규모 순매도는 고환율, 연준/금리, 경기/성장 둔화 우려가 복합적으로 작용.",
    "KOSPI에서 외국인 매도 집중, USD/KRW 상승과 동반된 FX-driven 유출이 주된 원인.",
    "개인 매수는 레버리지 추격성 성격이 강하며, 20일 누적 하락세 속 지속성에 의문."
  ],
  "korean_comment": "공급 우위의 외국인 매도세에 개인이 단기적으로 흡수하는 불안정한 수급 구간입니다.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 최근 20일간 약 -25% 급락하며 시장 전반에 심각한 약세가 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나며 투자심리가 크게 위축되었습니다.",
    "환율 급등과 글로벌 불확실성으로 추가 하락 위험이 높아진 상황입니다."
  ],
  "korean_comment": "시장 전반에 걸친 강한 매도세와 변동성 확대가 우려됩니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.note",
    "snapshot.markets.fx.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre-analysis_agent",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 큼",
    "외국인 대규모 순매도 지속",
    "단기 반전 신호는 없음"
  ],
  "korean_comment": "시장 전반에 구조적 위험 신호가 뚜렷합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.market_summary.note",
    "snapshot.markets.kr.kospi_pct"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 약화가 지속되고 있습니다.",
    "추가적인 실적 하향 조정 위험이 큽니다."
  ],
  "korean_comment": "20일 누적 하락과 외국인 매도세로 실적 전망이 악화되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.note",
    "snapshot.cumulative_context.note"
  ]
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "시장 하락세가 광범위하게 확산되고 있음.",
    "20일 누적 하락폭이 매우 크고, 반전 신호는 없음."
  ],
  "korean_comment": "시장 내부 확산 약화와 하락 추세가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.markets.kr.kospi_pct"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 큽니다.",
    "외국인 대규모 순매도와 변동성 상승이 확인됩니다.",
    "정책 및 환율 불확실성으로 유동성 위축이 뚜렷합니다."
  ],
  "korean_comment": "유동성 악화와 외국인 이탈로 위험회피 국면입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.macro.daily.usdkrw",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```