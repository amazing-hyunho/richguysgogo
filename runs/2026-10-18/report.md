# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-18**
- 생성 시각(UTC): `2026-10-18T00:52:21.407517+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=2, RISK_ON=1, RISK_OFF=4
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +2.05% / KOSDAQ +4.46%
- **미국 지수**: S&P500 -1.09% / NASDAQ -2.14% / DOW -0.34%
- **환율/변동성**: USD/KRW 1334.77 (-0.86%) / VIX 20.0
- **시장 요약 노트**: KOSPI 2.05%, USD/KRW 1334.77. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 +2692억 / 기관 -5126억 / 개인 -6034억
- **일간 매크로**: 미10년 5.10% / 미2년 4.07% / 2-10 1.03%p / DXY 101.84
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.20% / 기준금리 3.75% / 실질금리 2.75%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 5,668.05로 2.05%, KOSDAQ은 794.78로 4.46% 상승했지만 KOSPI 5일·20일 누적 수익률은 각각 -9.371%, -19.759%입니다.
  ↳ 출처: `market_data, cumulative_context`
- 10월 16일 외국인은 2,692억원 순매수했으나 기관과 개인은 각각 5,126억원, 6,034억원 순매도해 추세적 수급 전환 여부는 추가 확인이 필요합니다.
  ↳ 출처: `flow_data, korean_market_flow_breakdown`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 반등에도 불구하고 중기적으론 약세 신호가 우세합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 반등했으나 20일 누적 하락폭이 매우 커 중기 약세 국면이 지속되고 있습니다.
- 핵심 주장: 한국 월별 지표는 심리·고용·수출은 긍정적이나 생산·소비는 부진하여 경기 방향성에 불확실성이 큽니다.
- 핵심 주장: 외국인 순매수와 원화 강세에도 불구하고, 최근 변동성 확대와 누적 하락을 감안하면 신중한 접근이 필요합니다.

### 수급 담당자
- 한줄 요약: 외국인 저점 매수와 원화 강세가 개인·기관 매도 물량을 흡수하는 수급 전환 구간입니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: 외국인 순매수는 KOSPI에 집중되었으며, 최근 급락(-20%) 이후 저점 반발 매수와 원화 강세(고환율 완화)가 주요 동인입니다.
- 핵심 주장: 기관은 대규모 매도, 개인은 레버리지 청산성 매도 성격이 강하며, 외국인 매수세가 개인·기관 매도 물량을 흡수하는 구조입니다.
- 핵심 주장: 핵심 키워드는 고환율 완화, 반도체/AI, 급락 후 반등, 국내 심리 개선입니다.

### 섹터 담당자
- 한줄 요약: 단기 반등에도 불구하고 중기 불확실성이 여전합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 약 -20% 급락 후 단기 반등세를 보이고 있습니다.
- 핵심 주장: 외국인 순매수와 원화 강세가 단기적으로 긍정적이지만, 중기적으론 변동성 확대와 경기 혼조가 부담입니다.
- 핵심 주장: 생산·소비 지표는 부진하며, 심리지표와 수출·고용만 일부 긍정적입니다.

### 리스크 담당자
- 한줄 요약: 단기 반등에도 누적 하락과 실물 부진이 부담입니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: 코스피 20일 누적 하락폭이 매우 큽니다.
- 핵심 주장: 생산·소비 지표가 전반적으로 부진합니다.
- 핵심 주장: 심리지표는 개선되고 있으나 경기 혼조 신호가 혼재합니다.

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 전환 신호는 아직 확인되지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 신호는 부재하며, 추세 반전 근거가 약함.
- 핵심 주장: 20일 누적 하락폭이 크고, 외국인 매수에도 실적 기대 상향은 제한적.
- 핵심 주장: 단기 반등은 수급·심리 영향, 실적 추정 상향 전환 신호는 없음.

### 브레드스 담당자
- 한줄 요약: 단기 반등에도 불구하고 중기 하락 추세가 우세합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고, 단기 반등에도 불구하고 하락 추세가 뚜렷함.
- 핵심 주장: 시장 내 확산도(breadth)는 단기적으로 개선 신호가 있으나, 중기적으로는 약세 국면 지속.
- 핵심 주장: 외국인 순매수와 원화 강세에도 불구하고, 전반적 시장 체력은 아직 회복되지 않음.

### 유동성 담당자
- 한줄 요약: 유동성 환경은 여전히 보수적이며 단기 반등에 과도하게 기대하기 어렵습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 원/달러 환율 하락과 외국인 순매수에도 불구하고 변동성(VIX) 상승과 최근 누적 하락폭이 큼.
- 핵심 주장: 미국 금리와 변동성 지표가 보수적 유동성 환경을 시사.
- 핵심 주장: 단기 반등에도 정책·유동성 환경은 위험회피에 가깝다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 반등에도 불구하고 중기적으론 약세 신호가 우세합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+2692억, kospi_change_pct=+2.05%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.market_summary.kospi_change_pct
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 저점 매수와 원화 강세가 개인·기관 매도 물량을 흡수하는 수급 전환 구간입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.05%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 반등에도 불구하고 중기 불확실성이 여전합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.05%, foreign_net=+2692억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 반등에도 누적 하락과 실물 부진이 부담입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.05%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.korea_macro_context, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 전환 신호는 아직 확인되지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+2692억, kospi_change_pct=+2.05%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.kospi_change_pct, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '단기 반등에도 불구하고 중기 하락 추세가 우세합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+2692억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct, snapshot.markets.fx.usdkrw_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 환경은 여전히 보수적이며 단기 반등에 과도하게 기대하기 어렵습니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1334.77, foreign_net=+2692억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.usdkrw, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix, snapshot.macro.daily.us10y, snapshot.macro.daily.dxy, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.kospi_abs_move_5d_avg
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI +2.05%, USD/KRW 1334.77(-0.86%), VIX 20.0, 외국인 +2692억이고, 뉴스는 반등·회복 기대가 섞인 완화 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 국면 판단: 다수=단기 반등에도 20일 누적 하락과 변동성 부담이 커 위험회피 국면이 이어진다는 판단입니다., 소수=외국인 KOSPI 매수와 원화 강세를 초기 수급 전환 신호로 볼 수 있다는 의견입니다., 에이전트=[flow, risk]
  - 의미: 반등 추종 여부와 포트폴리오 위험 노출 확대 시점을 좌우합니다.
- 반등의 지속 가능성: 다수=macro·earnings·breadth·liquidity는 실적 상향 신호 부재와 보수적 유동성 환경 때문에 지속성을 낮게 평가했습니다., 소수=flow는 외국인 저점 매수와 환율 하락이 기관·개인 매물을 흡수하는 구간이라고 판단했습니다., 에이전트=[flow]
  - 의미: 외국인 매수가 하루성 반발인지 중기 자금 유입인지에 따라 반등의 폭과 기간이 달라질 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 단기 반등했으나 20일 누적 하락폭이 매우 커 중기 약세 국면이 지속되고 있습니다.",
    "한국 월별 지표는 심리·고용·수출은 긍정적이나 생산·소비는 부진하여 경기 방향성에 불확실성이 큽니다.",
    "외국인 순매수와 원화 강세에도 불구하고, 최근 변동성 확대와 누적 하락을 감안하면 신중한 접근이 필요합니다."
  ],
  "korean_comment": "단기 반등에도 불구하고 중기적으론 약세 신호가 우세합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.market_summary.kospi_change_pct"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market)",
  "core_claims": [
    "외국인 순매수는 KOSPI에 집중되었으며, 최근 급락(-20%) 이후 저점 반발 매수와 원화 강세(고환율 완화)가 주요 동인입니다.",
    "기관은 대규모 매도, 개인은 레버리지 청산성 매도 성격이 강하며, 외국인 매수세가 개인·기관 매도 물량을 흡수하는 구조입니다.",
    "핵심 키워드는 고환율 완화, 반도체/AI, 급락 후 반등, 국내 심리 개선입니다."
  ],
  "korean_comment": "외국인 저점 매수와 원화 강세가 개인·기관 매도 물량을 흡수하는 수급 전환 구간입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.news_headlines",
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
    "KOSPI는 최근 20일간 약 -20% 급락 후 단기 반등세를 보이고 있습니다.",
    "외국인 순매수와 원화 강세가 단기적으로 긍정적이지만, 중기적으론 변동성 확대와 경기 혼조가 부담입니다.",
    "생산·소비 지표는 부진하며, 심리지표와 수출·고용만 일부 긍정적입니다."
  ],
  "korean_comment": "단기 반등에도 불구하고 중기 불확실성이 여전합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.korea_macro_context"
  ],
  "confidence": "MED"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "코스피 20일 누적 하락폭이 매우 큽니다.",
    "생산·소비 지표가 전반적으로 부진합니다.",
    "심리지표는 개선되고 있으나 경기 혼조 신호가 혼재합니다."
  ],
  "korean_comment": "단기 반등에도 누적 하락과 실물 부진이 부담입니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 신호는 부재하며, 추세 반전 근거가 약함.",
    "20일 누적 하락폭이 크고, 외국인 매수에도 실적 기대 상향은 제한적.",
    "단기 반등은 수급·심리 영향, 실적 추정 상향 전환 신호는 없음."
  ],
  "korean_comment": "실적 추정치 상향 전환 신호는 아직 확인되지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.kospi_change_pct",
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
    "KOSPI 20일 누적 하락폭이 매우 크고, 단기 반등에도 불구하고 하락 추세가 뚜렷함.",
    "시장 내 확산도(breadth)는 단기적으로 개선 신호가 있으나, 중기적으로는 약세 국면 지속.",
    "외국인 순매수와 원화 강세에도 불구하고, 전반적 시장 체력은 아직 회복되지 않음."
  ],
  "korean_comment": "단기 반등에도 불구하고 중기 하락 추세가 우세합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.markets.fx.usdkrw_pct"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "원/달러 환율 하락과 외국인 순매수에도 불구하고 변동성(VIX) 상승과 최근 누적 하락폭이 큼.",
    "미국 금리와 변동성 지표가 보수적 유동성 환경을 시사.",
    "단기 반등에도 정책·유동성 환경은 위험회피에 가깝다."
  ],
  "korean_comment": "유동성 환경은 여전히 보수적이며 단기 반등에 과도하게 기대하기 어렵습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg"
  ],
  "confidence": "HIGH"
}
```