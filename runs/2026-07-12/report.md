# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-12**
- 생성 시각(UTC): `2026-07-12T00:53:32.997959+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=5, RISK_ON=0, RISK_OFF=2
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +2.52% / KOSDAQ +5.47%
- **미국 지수**: S&P500 +0.42% / NASDAQ +0.29% / DOW +0.29%
- **환율/변동성**: USD/KRW 1502.98 (-0.51%) / VIX 15.0
- **시장 요약 노트**: KOSPI 2.52%, USD/KRW 1502.98. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -4791억 / 기관 +17139억 / 개인 -12018억
- **일간 매크로**: 미10년 4.57% / 미2년 3.69% / 2-10 0.87%p / DXY 100.97
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.33%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI 2.52%, KOSDAQ 5.47% 급등에도 20일 누적 하락률 -9.07%로 중기 약세가 지속되고 있습니다.
  ↳ 출처: `macro_daily, flow_data, cumulative_context`
- 외국인 -4791억 순매도, 기관 +1.7조 순매수로 수급 주도권이 기관에 넘어갔으나, 외국인 매도세는 지속되고 있습니다.
  ↳ 출처: `flow_data, korean_market_flow_breakdown`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 반등에도 누적 하락과 외국인 매도세는 경계가 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI는 단기 반등에도 불구하고 20일 누적 하락세가 뚜렷합니다.
- 핵심 주장: 외국인 순매도와 높은 변동성 평균이 위험 신호로 해석됩니다.
- 핵심 주장: 거시지표와 뉴스는 불확실성이 여전히 높음을 시사합니다.

### 수급 담당자
- 한줄 요약: 기관 주도 매수, 외국인 동반 매도, 개인은 반등 추격 매수세로 전환된 수급 구간.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: 핵심 키워드: 금리/연준, 반도체/AI, 환율/달러, 인플레이션.
- 핵심 주장: 외국인 순매도는 최근 반등에도 불구하고 고점 부담 및 금리·환율 불확실성(금리/연준, 환율/달러) 영향이 크며, KOSPI와 KOSDAQ 모두에서 동시 매도.
- 핵심 주장: 개인 매수세는 최근 하락장(-9%/20일) 이후 반등 추격 성격이 강하고, 기관이 주도적으로 매수하며 수급을 흡수하는 구도.

### 섹터 담당자
- 한줄 요약: 단기 반등에도 불구하고 중기적 위험 신호가 남아 있습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 급등했으나 20일 누적 하락폭이 여전히 크다.
- 핵심 주장: 기관 매수세가 강하게 유입되었으나 외국인은 순매도세를 지속하고 있다.
- 핵심 주장: 환율 안정과 변동성 하락이 긍정적이나, 추세 반전 신호는 아직 부족하다.

### 리스크 담당자
- 한줄 요약: 단기 반등에도 누적 하락과 외국인 매도는 주의 요인입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 반등했으나 20일 누적 하락폭이 크다
- 핵심 주장: 외국인 순매도 지속, 변동성은 낮은 편
- 핵심 주장: 시장 전반 리스크 신호는 제한적

### 이익모멘텀 담당자
- 한줄 요약: 실적 추세 반전 신호는 아직 부족합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀 개선 신호는 아직 뚜렷하지 않음
- 핵심 주장: 기관 매수세에도 외국인 순매도 지속
- 핵심 주장: 20일 누적 KOSPI 하락세로 실적 추세 반전 미약

### 브레드스 담당자
- 한줄 요약: 단기 반등에도 불구하고 중기적으로는 확산이 약한 상태입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI와 KOSDAQ 모두 단기 반등이 강하게 나타남.
- 핵심 주장: 20일 누적 하락폭이 여전히 크고, 시장 내부 확산은 제한적임.
- 핵심 주장: 기관 중심 매수세이나 외국인 매도세가 지속됨.

### 유동성 담당자
- 한줄 요약: 유동성 개선 신호는 제한적이며, 정책 불확실성이 큽니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 정책 긴축 우려와 외국인 순매도 지속으로 유동성 환경이 보수적입니다.
- 핵심 주장: 환율 하락에도 불구하고 변동성은 낮지 않으며, 누적 KOSPI 약세가 뚜렷합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 5명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 반등에도 누적 하락과 외국인 매도세는 경계가 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4791억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.news_headlines, snapshot.market_summary.note
- [수급 담당자] 저는 수급 담당자 입장에서 '기관 주도 매수, 외국인 동반 매도, 개인은 반등 추격 매수세로 전환된 수급 구간.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.52%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.news_headlines, snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 반등에도 불구하고 중기적 위험 신호가 남아 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.52%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.news_headlines
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 반등에도 누적 하락과 외국인 매도는 주의 요인입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.52%, foreign_net=-4791억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추세 반전 신호는 아직 부족합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.flow_summary.note, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '단기 반등에도 불구하고 중기적으로는 확산이 약한 상태입니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.note, snapshot.phase_two_signals.breadth_signal_score, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct, snapshot.cumulative_context.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 개선 신호는 제한적이며, 정책 불확실성이 큽니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4791억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.news_headlines, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.macro.daily.vix, snapshot.macro.structural.fed_funds_rate
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +2.52%, USD/KRW 1502.98(-0.51%), VIX 15.0, 외국인 -4791억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 시장 방향성 전환 여부: 다수=단기 반등에도 중기 약세 신호가 우세하므로 성급한 방향 전환은 경계, 소수=일부(매크로, 유동성 담당자)는 정책 불확실성 및 외국인 매도세를 근거로 위험회피(RISK_OFF) 강조, 에이전트=[macro, liquidity]
  - 의미: 정책 이벤트(금리 인상 등)와 외국인 매도세가 지속될 경우, 단기 반등이 추세 전환으로 이어지지 않을 수 있음

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 단기 반등에도 불구하고 20일 누적 하락세가 뚜렷합니다.",
    "외국인 순매도와 높은 변동성 평균이 위험 신호로 해석됩니다.",
    "거시지표와 뉴스는 불확실성이 여전히 높음을 시사합니다."
  ],
  "korean_comment": "단기 반등에도 누적 하락과 외국인 매도세는 경계가 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.news_headlines",
    "snapshot.market_summary.note"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market)",
  "core_claims": [
    "핵심 키워드: 금리/연준, 반도체/AI, 환율/달러, 인플레이션.",
    "외국인 순매도는 최근 반등에도 불구하고 고점 부담 및 금리·환율 불확실성(금리/연준, 환율/달러) 영향이 크며, KOSPI와 KOSDAQ 모두에서 동시 매도.",
    "개인 매수세는 최근 하락장(-9%/20일) 이후 반등 추격 성격이 강하고, 기관이 주도적으로 매수하며 수급을 흡수하는 구도."
  ],
  "korean_comment": "기관 주도 매수, 외국인 동반 매도, 개인은 반등 추격 매수세로 전환된 수급 구간.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.news_headlines",
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.us10y",
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
    "KOSPI가 단기 급등했으나 20일 누적 하락폭이 여전히 크다.",
    "기관 매수세가 강하게 유입되었으나 외국인은 순매도세를 지속하고 있다.",
    "환율 안정과 변동성 하락이 긍정적이나, 추세 반전 신호는 아직 부족하다."
  ],
  "korean_comment": "단기 반등에도 불구하고 중기적 위험 신호가 남아 있습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.news_headlines"
  ],
  "confidence": "MED"
}
```
### 리스크 담당자
```text
{"agent_name": "RISK pre-analysis agent", "core_claims": ["KOSPI가 단기 반등했으나 20일 누적 하락폭이 크다", "외국인 순매도 지속, 변동성은 낮은 편", "시장 전반 리스크 신호는 제한적"], "korean_comment": "단기 반등에도 누적 하락과 외국인 매도는 주의 요인입니다.", "regime_tag": "NEUTRAL", "evidence_ids": ["snapshot.cumulative_context.kospi_20d_cum_pct", "snapshot.market_summary.kospi_change_pct", "snapshot.flow_summary.foreign_net", "snapshot.cumulative_context.vix_5d_avg", "snapshot.cumulative_context.note"], "confidence": "MED"}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 개선 신호는 아직 뚜렷하지 않음",
    "기관 매수세에도 외국인 순매도 지속",
    "20일 누적 KOSPI 하락세로 실적 추세 반전 미약"
  ],
  "korean_comment": "실적 추세 반전 신호는 아직 부족합니다.",
  "regime_tag": "NEUTRAL",
  "confidence": "MED",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.note"
  ]
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI와 KOSDAQ 모두 단기 반등이 강하게 나타남.",
    "20일 누적 하락폭이 여전히 크고, 시장 내부 확산은 제한적임.",
    "기관 중심 매수세이나 외국인 매도세가 지속됨."
  ],
  "korean_comment": "단기 반등에도 불구하고 중기적으로는 확산이 약한 상태입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "정책 긴축 우려와 외국인 순매도 지속으로 유동성 환경이 보수적입니다.",
    "환율 하락에도 불구하고 변동성은 낮지 않으며, 누적 KOSPI 약세가 뚜렷합니다."
  ],
  "korean_comment": "유동성 개선 신호는 제한적이며, 정책 불확실성이 큽니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.news_headlines",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.macro.daily.vix",
    "snapshot.macro.structural.fed_funds_rate"
  ],
  "confidence": "HIGH"
}
```