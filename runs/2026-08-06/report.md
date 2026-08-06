# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-08-06**
- 생성 시각(UTC): `2026-08-06T00:52:28.131000+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=0, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.45% / KOSDAQ -0.65%
- **미국 지수**: S&P500 -0.17% / NASDAQ -0.83% / DOW +0.49%
- **환율/변동성**: USD/KRW 1428.89 (-0.29%) / VIX 15.8
- **시장 요약 노트**: KOSPI -3.45%, USD/KRW 1428.89. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -7957억 / 기관 +466억 / 개인 +7262억
- **일간 매크로**: 미10년 4.62% / 미2년 3.72% / 2-10 0.89%p / DXY 99.66
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.73% / Core CPI YoY 2.81% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.40%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI -3.45% 급락, 외국인 -7957억 순매도 등 수급 불안이 심화되었습니다.
  ↳ 출처: `flow_data, macro_daily, news`
- 연준 매파 발언과 금리 인상 우려가 투자심리 위축에 결정적 역할을 했습니다.
  ↳ 출처: `news, macro_daily`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 시장 전반에 불확실성이 확대되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 20일간 크게 하락하며 변동성이 높아졌습니다.
- 핵심 주장: 외국인 자금 유출과 금리 인상 우려가 시장에 부담을 주고 있습니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안 지속.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 금리/연준, 고환율, 인플레이션 우려가 복합적으로 작용.
- 핵심 주장: KOSPI 중심 외국인 매도세는 USD/KRW 상승과 연준 매파 발언 영향이 크며, FX-driven 유출 성격이 강함.
- 핵심 주장: 개인 매수세는 단기 급락에 따른 저가매수 시도이나, 최근 20일 누적 하락과 변동성 고려 시 지속성은 낮음.

### 섹터 담당자
- 한줄 요약: 시장 전반에 위험회피 심리가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 -16% 하락하며 약세가 지속되고 있습니다.
- 핵심 주장: 외국인 대규모 순매도와 변동성 확대가 뚜렷합니다.
- 핵심 주장: 금리 인상 우려와 매파적 연준 발언이 투자심리를 위축시키고 있습니다.

### 리스크 담당자
- 한줄 요약: 단기 급락이 있었으나 누적 지표상 과도한 위험 신호는 아직 아니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 급락했으나 최근 5일간 강한 반등세가 있었다.
- 핵심 주장: 외국인 대규모 순매도와 변동성 확대가 확인된다.
- 핵심 주장: 20일 누적 하락폭이 크지만, 즉각적인 추가 위험 신호는 제한적이다.

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 전환 신호는 아직 부족합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀은 단기 반등에도 불구하고 여전히 약세입니다.
- 핵심 주장: 외국인 대규모 순매도와 20일 누적 하락이 실적 추정치 하향 압력으로 작용합니다.

### 브레드스 담당자
- 한줄 요약: 시장 전반의 확산도가 매우 약화된 상태입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 최근 20일간 큰 하락세를 보임.
- 핵심 주장: 시장 내 확산도(breadth) 약화와 외국인 대규모 순매도 지속.
- 핵심 주장: 단기 반등 후 재차 하락세로 전환, 시장 내부 확산도 매우 부진.

### 유동성 담당자
- 한줄 요약: 유동성과 정책 불확실성으로 위험회피 국면이 지속되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락과 외국인 대규모 순매도는 유동성 악화 신호입니다.
- 핵심 주장: 연준 매파 발언과 금리 인상 우려로 정책 불확실성이 높아졌습니다.
- 핵심 주장: 환율 변동성은 낮지만, 전반적 위험회피 심리가 강합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '시장 전반에 불확실성이 확대되고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.45%, foreign_net=-7957억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안 지속.' 의견을 유지합니다. 근거 숫자는 usdkrw=1428.89, kospi_change_pct=-3.45%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.usdkrw, snapshot.market_summary.kospi_change_pct, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.macro.daily.dxy, snapshot.cumulative_context.kospi_20d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 위험회피 심리가 강하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-7957억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.news_headlines, snapshot.macro.daily.vix
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 급락이 있었으나 누적 지표상 과도한 위험 신호는 아직 아니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.45%, foreign_net=-7957억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note, snapshot.news_headlines, snapshot.markets.volatility.vix
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 전환 신호는 아직 부족합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-7957억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.note, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 확산도가 매우 약화된 상태입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-7957억, kospi_change_pct=-3.45%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성과 정책 불확실성으로 위험회피 국면이 지속되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-7957억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.news_headlines, snapshot.macro.structural.fed_funds_rate, snapshot.macro.daily.vix, snapshot.cumulative_context.vix_5d_avg
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.45%, USD/KRW 1428.89(-0.29%), VIX 15.8, 외국인 -7957억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 단기 위험 신호 해석: 다수=외국인 대규모 순매도와 변동성 확대에 따라 위험회피(RISK_OFF) 국면이 지속된다는 의견, 소수=단기 급락에도 불구하고 최근 5일간 반등세가 있었고, 과도한 위험 신호는 아직 아니라는 의견, 에이전트=[risk]
  - 의미: 단기 반등 가능성에 대한 해석 차이로, 추가 하락 또는 기술적 반등 시점 판단에 영향을 미침

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 20일간 크게 하락하며 변동성이 높아졌습니다.",
    "외국인 자금 유출과 금리 인상 우려가 시장에 부담을 주고 있습니다."
  ],
  "korean_comment": "시장 전반에 불확실성이 확대되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW Pre-Analysis Agent (Korean Market)",
  "core_claims": [
    "외국인 대규모 순매도는 금리/연준, 고환율, 인플레이션 우려가 복합적으로 작용.",
    "KOSPI 중심 외국인 매도세는 USD/KRW 상승과 연준 매파 발언 영향이 크며, FX-driven 유출 성격이 강함.",
    "개인 매수세는 단기 급락에 따른 저가매수 시도이나, 최근 20일 누적 하락과 변동성 고려 시 지속성은 낮음."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안 지속.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.usdkrw",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
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
    "KOSPI는 최근 20일간 -16% 하락하며 약세가 지속되고 있습니다.",
    "외국인 대규모 순매도와 변동성 확대가 뚜렷합니다.",
    "금리 인상 우려와 매파적 연준 발언이 투자심리를 위축시키고 있습니다."
  ],
  "korean_comment": "시장 전반에 위험회피 심리가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.news_headlines",
    "snapshot.macro.daily.vix"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI가 단기 급락했으나 최근 5일간 강한 반등세가 있었다.",
    "외국인 대규모 순매도와 변동성 확대가 확인된다.",
    "20일 누적 하락폭이 크지만, 즉각적인 추가 위험 신호는 제한적이다."
  ],
  "korean_comment": "단기 급락이 있었으나 누적 지표상 과도한 위험 신호는 아직 아니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.note",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀은 단기 반등에도 불구하고 여전히 약세입니다.",
    "외국인 대규모 순매도와 20일 누적 하락이 실적 추정치 하향 압력으로 작용합니다."
  ],
  "korean_comment": "실적 추정치 상향 전환 신호는 아직 부족합니다.",
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
    "KOSPI와 KOSDAQ 모두 최근 20일간 큰 하락세를 보임.",
    "시장 내 확산도(breadth) 약화와 외국인 대규모 순매도 지속.",
    "단기 반등 후 재차 하락세로 전환, 시장 내부 확산도 매우 부진."
  ],
  "korean_comment": "시장 전반의 확산도가 매우 약화된 상태입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 20일 누적 하락과 외국인 대규모 순매도는 유동성 악화 신호입니다.",
    "연준 매파 발언과 금리 인상 우려로 정책 불확실성이 높아졌습니다.",
    "환율 변동성은 낮지만, 전반적 위험회피 심리가 강합니다."
  ],
  "korean_comment": "유동성과 정책 불확실성으로 위험회피 국면이 지속되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines",
    "snapshot.macro.structural.fed_funds_rate",
    "snapshot.macro.daily.vix",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```