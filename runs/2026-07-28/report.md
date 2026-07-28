# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-28**
- 생성 시각(UTC): `2026-07-28T00:52:21.661850+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -7.59% / KOSDAQ -6.00%
- **미국 지수**: S&P500 +0.02% / NASDAQ -0.18% / DOW +0.51%
- **환율/변동성**: USD/KRW 1459.60 (+0.21%) / VIX 18.7
- **시장 요약 노트**: KOSPI -7.59%, USD/KRW 1459.60. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -14197억 / 기관 -1968억 / 개인 +16168억
- **일간 매크로**: 미10년 4.64% / 미2년 3.80% / 2-10 0.84%p / DXY 101.50
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.73% / Core CPI YoY 2.81% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.43%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI -7.59%, KOSDAQ -6.0% 급락과 외국인 -1.4조원 순매도, 개인 +1.6조원 순매수로 극단적 수급 불균형이 발생했습니다.
  ↳ 출처: `flow_data, macro_daily`
- USD/KRW 1459.60(+0.21%)로 원화 약세가 심화되며 외국인 자금 유출 압력이 가중되고 있습니다.
  ↳ 출처: `macro_daily, news`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 크게 하락하며 변동성이 높아졌습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 지속되고 있습니다.
- 핵심 주장: 환율과 변동성 지표도 불안정한 모습을 보이고 있습니다.

### 수급 담당자
- 한줄 요약: 외국인 환차손 회피성 매도와 개인의 저가 매수세가 충돌하는 공급우위 장세.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고환율(USD/KRW 상승)과 글로벌 금리/연준 불확실성, 그리고 최근 KOSPI 급락(-34%/20일) 누적에 따른 위험회피가 복합적으로 작용.
- 핵심 주장: 외국인 매도는 KOSPI에 집중되어 있으며, 환율 상승과 동반된 자금 유출(핵심 키워드: 고환율, 연준/금리, 경기/성장 둔화)로 FX-driven outflow 성격이 강함.
- 핵심 주장: 개인 매수세는 대규모 외국인 매도 물량을 흡수하는 형태이나, 최근 20일간의 급락과 변동성 확대(국내 변동성 직접 판단 제한적, VKOSPI 미제공)로 인해 지속 가능성은 낮음.

### 섹터 담당자
- 한줄 요약: 국내 증시는 전방위적 위험 회피 국면입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락률이 -34%로 극심한 약세장이다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 지속되고 있다.
- 핵심 주장: 환율과 변동성 지표도 위험 회피 심리를 반영한다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 걸친 구조적 위험 신호가 명확합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락 -34%로 심각한 약세
- 핵심 주장: 외국인 대규모 순매도 지속
- 핵심 주장: 환율 급등세로 투자심리 위축

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀 약화가 단기 이슈를 넘어 구조적으로 이어질 수 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락으로 실적 모멘텀 약화 신호.
- 핵심 주장: 외국인 대규모 순매도는 실적 전망 하향 압력.
- 핵심 주장: 실적 추정치 하향 및 가이던스 악화 우려 지속.

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸쳐 하락 압력이 강하게 확산되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 단기 및 중장기적으로 급락세가 지속되고 있습니다.
- 핵심 주장: 시장 내 확산도(breadth)와 내부 흐름이 매우 취약한 상태입니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.

### 유동성 담당자
- 한줄 요약: 유동성 및 정책 환경이 위험회피(RISK_OFF) 국면입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큽니다.
- 핵심 주장: 외국인 대규모 순매도와 환율 상승이 유동성 악화 신호입니다.
- 핵심 주장: 변동성(VIX)도 높아 위험회피 심리가 강합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-7.59%, foreign_net=-14197억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.fx.usdkrw, snapshot.markets.volatility.vix, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 환차손 회피성 매도와 개인의 저가 매수세가 충돌하는 공급우위 장세.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.note, snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.news_headlines, snapshot.macro.daily.usdkrw, snapshot.macro.daily.us10y, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '국내 증시는 전방위적 위험 회피 국면입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14197억, institution_net=-1968억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.usdkrw, snapshot.markets.volatility.vix, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 걸친 구조적 위험 신호가 명확합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14197억, usdkrw=1459.60입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀 약화가 단기 이슈를 넘어 구조적으로 이어질 수 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14197억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.note, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸쳐 하락 압력이 강하게 확산되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14197억, institution_net=-1968억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.kospi_change_pct, snapshot.markets.kr.kosdaq_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 및 정책 환경이 위험회피(RISK_OFF) 국면입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14197억, usdkrw=1459.60입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.note
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -7.59%, USD/KRW 1459.60(+0.21%), VIX 18.7, 외국인 -14197억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 위험 국면 해석: 다수=RISK_OFF: 외국인 대규모 순매도, 고환율, 변동성 확대 등으로 위험회피 심리가 지배적이라는 의견(6명), 소수=RISK_ON: 구조적 위험 신호가 명확하나, 일부는 단기 반등 가능성도 배제하지 않음(1명, risk), 에이전트=[risk]
  - 의미: 소수 의견은 극단적 하락 이후 기술적 반등 가능성을 시사하나, 대다수는 추가 하락 리스크에 더 무게를 둠.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 20일간 크게 하락하며 변동성이 높아졌습니다.",
    "외국인과 기관의 대규모 순매도세가 지속되고 있습니다.",
    "환율과 변동성 지표도 불안정한 모습을 보이고 있습니다."
  ],
  "korean_comment": "시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인 대규모 순매도는 고환율(USD/KRW 상승)과 글로벌 금리/연준 불확실성, 그리고 최근 KOSPI 급락(-34%/20일) 누적에 따른 위험회피가 복합적으로 작용.",
    "외국인 매도는 KOSPI에 집중되어 있으며, 환율 상승과 동반된 자금 유출(핵심 키워드: 고환율, 연준/금리, 경기/성장 둔화)로 FX-driven outflow 성격이 강함.",
    "개인 매수세는 대규모 외국인 매도 물량을 흡수하는 형태이나, 최근 20일간의 급락과 변동성 확대(국내 변동성 직접 판단 제한적, VKOSPI 미제공)로 인해 지속 가능성은 낮음."
  ],
  "korean_comment": "외국인 환차손 회피성 매도와 개인의 저가 매수세가 충돌하는 공급우위 장세.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.note",
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.news_headlines",
    "snapshot.macro.daily.usdkrw",
    "snapshot.macro.daily.us10y",
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
    "KOSPI 20일 누적 하락률이 -34%로 극심한 약세장이다.",
    "외국인과 기관의 대규모 순매도세가 지속되고 있다.",
    "환율과 변동성 지표도 위험 회피 심리를 반영한다."
  ],
  "korean_comment": "국내 증시는 전방위적 위험 회피 국면입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.volatility.vix",
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
    "KOSPI 20일 누적 하락 -34%로 심각한 약세",
    "외국인 대규모 순매도 지속",
    "환율 급등세로 투자심리 위축"
  ],
  "korean_comment": "시장 전반에 걸친 구조적 위험 신호가 명확합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.market_summary.kospi_change_pct",
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
    "KOSPI 20일 누적 급락으로 실적 모멘텀 약화 신호.",
    "외국인 대규모 순매도는 실적 전망 하향 압력.",
    "실적 추정치 하향 및 가이던스 악화 우려 지속."
  ],
  "korean_comment": "실적 모멘텀 약화가 단기 이슈를 넘어 구조적으로 이어질 수 있습니다.",
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
    "KOSPI와 KOSDAQ 모두 단기 및 중장기적으로 급락세가 지속되고 있습니다.",
    "시장 내 확산도(breadth)와 내부 흐름이 매우 취약한 상태입니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다."
  ],
  "korean_comment": "시장 전반에 걸쳐 하락 압력이 강하게 확산되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.market_summary.kospi_change_pct",
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
    "KOSPI 20일 누적 하락폭이 매우 큽니다.",
    "외국인 대규모 순매도와 환율 상승이 유동성 악화 신호입니다.",
    "변동성(VIX)도 높아 위험회피 심리가 강합니다."
  ],
  "korean_comment": "유동성 및 정책 환경이 위험회피(RISK_OFF) 국면입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```