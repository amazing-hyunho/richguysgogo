# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-01**
- 생성 시각(UTC): `2026-07-01T00:54:11.061887+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=3, RISK_ON=0, RISK_OFF=4
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -0.39% / KOSDAQ +4.08%
- **미국 지수**: S&P500 +0.79% / NASDAQ +1.52% / DOW +0.26%
- **환율/변동성**: USD/KRW 1548.63 (+0.57%) / VIX 16.5
- **시장 요약 노트**: KOSPI -0.39%, USD/KRW 1548.63. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -6275억 / 기관 +5258억 / 개인 +1535억
- **일간 매크로**: 미10년 4.42% / 미2년 3.73% / 2-10 0.69%p / DXY 101.27
- **월간 매크로**: 실업률 4.30% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.18%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 -0.39% 하락(8443.05p), 외국인 순매도 -6275억, 원/달러 환율 1548.63(+0.57%)로 위험회피 심리가 우세합니다.
  ↳ 출처: `flow_data, macro_daily, news`
- KOSDAQ은 4.08% 급등(953.55p)했으나, 시장 전반 확산세는 제한적이며 외국인 매도세가 지속되고 있습니다.
  ↳ 출처: `flow_data, macro_daily`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 국내 증시는 단기적으로 보수적 접근이 필요해 보입니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 약세를 보이고 있습니다.
- 핵심 주장: 외국인 자금 유출과 원화 약세가 지속되고 있습니다.
- 핵심 주장: 미국 증시 강세에도 국내 시장은 방어적입니다.

### 수급 담당자
- 한줄 요약: 고환율과 금리 불확실성으로 외국인 매도 우위, 개인이 단기 흡수 중이나 지속성은 약함.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 매도는 고환율(USD/KRW 상승)과 연준/금리 불확실성에 따른 FX-driven outflow가 주된 원인.
- 핵심 주장: KOSPI에서 외국인 매도가 집중되었으며, 개인은 이를 일부 흡수했으나 최근 20일간 KOSPI 약세로 지속성은 낮음.
- 핵심 주장: 국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 변동성만 반영.

### 섹터 담당자
- 한줄 요약: 시장 전반에 보수적 기조가 유지되고 있습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 약세를 보이고 있다.
- 핵심 주장: 외국인 자금 유출과 원화 약세가 지속되고 있다.
- 핵심 주장: 반도체 수출 호조에도 시장 전반은 신중한 분위기다.

### 리스크 담당자
- 한줄 요약: 단기적으로 뚜렷한 위험 신호는 없으나, 누적 약세와 외국인 매도세는 주의가 필요합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 약세를 보이고 있습니다.
- 핵심 주장: 외국인 자금이 지속적으로 유출되고 있습니다.
- 핵심 주장: 환율 상승세가 이어지고 있습니다.

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀 약화가 지속되는 구간입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 실적 모멘텀은 약화 추세가 지속되고 있음
- 핵심 주장: 외국인 순매도와 20일 누적 하락이 실적 기대치 하향을 시사
- 핵심 주장: 단기 반등 신호 없이 실적 추정치 상향 전환 근거 부족

### 브레드스 담당자
- 한줄 요약: 시장 전반의 확산세는 제한적이며, 단기 반등에도 불구하고 신중한 접근이 필요합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 약세 흐름이 지속되고 있음.
- 핵심 주장: KOSDAQ은 단기적으로 강한 반등세를 보이나, 시장 전반 확산은 제한적임.
- 핵심 주장: 외국인 순매도와 변동성 지표는 중립~약세 신호를 시사함.

### 유동성 담당자
- 한줄 요약: 유동성 및 정책 환경이 위험회피적으로 전환되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 원/달러 환율이 상승하며 외국인 자금 유출이 지속되고 있습니다.
- 핵심 주장: KOSPI 20일 누적 하락과 변동성 평균이 높아 유동성 환경이 보수적입니다.
- 핵심 주장: 연준의 금리 인상 가능성 언급으로 정책 불확실성도 높아졌습니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '국내 증시는 단기적으로 보수적 접근이 필요해 보입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-6275억, usdkrw=1548.63입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.markets.fx.usdkrw, snapshot.markets.kr.kospi_pct, snapshot.cumulative_context.note, snapshot.news_headlines, snapshot.cumulative_context.vix_5d_avg
- [수급 담당자] 저는 수급 담당자 입장에서 '고환율과 금리 불확실성으로 외국인 매도 우위, 개인이 단기 흡수 중이나 지속성은 약함.' 의견을 유지합니다. 근거 숫자는 usdkrw=1548.63, dxy=101.27입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.usdkrw, snapshot.macro.daily.usdkrw, snapshot.macro.daily.dxy, snapshot.macro.daily.us10y, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 보수적 기조가 유지되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-6275억, usdkrw=1548.63입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기적으로 뚜렷한 위험 신호는 없으나, 누적 약세와 외국인 매도세는 주의가 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-6275억, usdkrw=1548.63입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀 약화가 지속되는 구간입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-6275억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 확산세는 제한적이며, 단기 반등에도 불구하고 신중한 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-6275억, vix=16.5입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.note, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kosdaq_pct, snapshot.markets.volatility.vix, snapshot.phase_two_signals.breadth_signal_score
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 및 정책 환경이 위험회피적으로 전환되고 있습니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1548.63, foreign_net=-6275억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.usdkrw, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.news_headlines, snapshot.macro.structural.fed_funds_rate, snapshot.macro.daily.vix
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -0.39%, USD/KRW 1548.63(+0.57%), VIX 16.5, 외국인 -6275억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 전반의 위험 인식: 다수=리스크 오프(방어적) 기조 유지, 소수=중립(NEUTRAL) 의견: 단기 위험 신호는 뚜렷하지 않으나 누적 약세 주의, 에이전트=[sector, risk, breadth]
  - 의미: 단기 반등(특히 KOSDAQ)에도 불구하고, 외국인 매도와 고환율이 지속될 경우 시장 전체의 하락 압력이 이어질 수 있음

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 최근 20일간 약세를 보이고 있습니다.",
    "외국인 자금 유출과 원화 약세가 지속되고 있습니다.",
    "미국 증시 강세에도 국내 시장은 방어적입니다."
  ],
  "korean_comment": "국내 증시는 단기적으로 보수적 접근이 필요해 보입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.fx.usdkrw",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.cumulative_context.note",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인 매도는 고환율(USD/KRW 상승)과 연준/금리 불확실성에 따른 FX-driven outflow가 주된 원인.",
    "KOSPI에서 외국인 매도가 집중되었으며, 개인은 이를 일부 흡수했으나 최근 20일간 KOSPI 약세로 지속성은 낮음.",
    "국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 변동성만 반영."
  ],
  "korean_comment": "고환율과 금리 불확실성으로 외국인 매도 우위, 개인이 단기 흡수 중이나 지속성은 약함.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.usdkrw",
    "snapshot.macro.daily.usdkrw",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.daily.us10y",
    "snapshot.news_headlines",
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
    "KOSPI는 최근 20일간 약세를 보이고 있다.",
    "외국인 자금 유출과 원화 약세가 지속되고 있다.",
    "반도체 수출 호조에도 시장 전반은 신중한 분위기다."
  ],
  "korean_comment": "시장 전반에 보수적 기조가 유지되고 있습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre-analysis_agent",
  "core_claims": [
    "KOSPI는 최근 20일간 약세를 보이고 있습니다.",
    "외국인 자금이 지속적으로 유출되고 있습니다.",
    "환율 상승세가 이어지고 있습니다."
  ],
  "korean_comment": "단기적으로 뚜렷한 위험 신호는 없으나, 누적 약세와 외국인 매도세는 주의가 필요합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 실적 모멘텀은 약화 추세가 지속되고 있음",
    "외국인 순매도와 20일 누적 하락이 실적 기대치 하향을 시사",
    "단기 반등 신호 없이 실적 추정치 상향 전환 근거 부족"
  ],
  "korean_comment": "실적 모멘텀 약화가 지속되는 구간입니다.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.note"
  ]
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI는 최근 20일간 약세 흐름이 지속되고 있음.",
    "KOSDAQ은 단기적으로 강한 반등세를 보이나, 시장 전반 확산은 제한적임.",
    "외국인 순매도와 변동성 지표는 중립~약세 신호를 시사함."
  ],
  "korean_comment": "시장 전반의 확산세는 제한적이며, 단기 반등에도 불구하고 신중한 접근이 필요합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.note",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.markets.volatility.vix",
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
    "원/달러 환율이 상승하며 외국인 자금 유출이 지속되고 있습니다.",
    "KOSPI 20일 누적 하락과 변동성 평균이 높아 유동성 환경이 보수적입니다.",
    "연준의 금리 인상 가능성 언급으로 정책 불확실성도 높아졌습니다."
  ],
  "korean_comment": "유동성 및 정책 환경이 위험회피적으로 전환되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.news_headlines",
    "snapshot.macro.structural.fed_funds_rate",
    "snapshot.macro.daily.vix"
  ],
  "confidence": "HIGH"
}
```