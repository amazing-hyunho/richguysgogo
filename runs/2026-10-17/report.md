# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-17**
- 생성 시각(UTC): `2026-10-17T00:52:16.477669+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=3, RISK_ON=0, RISK_OFF=4
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +2.05% / KOSDAQ +4.46%
- **미국 지수**: S&P500 -1.09% / NASDAQ -2.14% / DOW -0.34%
- **환율/변동성**: USD/KRW 1334.89 (-0.52%) / VIX 20.0
- **시장 요약 노트**: KOSPI 2.05%, USD/KRW 1334.89. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 +2692억 / 기관 -5126억 / 개인 -6034억
- **일간 매크로**: 미10년 5.10% / 미2년 4.07% / 2-10 1.03%p / DXY 101.78
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.20% / 기준금리 3.75% / 실질금리 2.75%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 5,668.05로 2.05%, KOSDAQ는 794.78로 4.46% 상승했고 원·달러는 1,334.89원으로 0.52% 하락했다. 다만 KOSPI 5일·20일 누적 수익률은 각각 -9.37%, -19.76%다.
  ↳ 출처: `flow_data, macro_daily, cumulative_context`
- 전체 외국인은 2,692억원 순매수했지만 기관과 개인은 각각 5,126억원, 6,034억원 순매도했다. 외국인 매수는 KOSPI 3,637억원에 집중된 반면 KOSDAQ에서는 945억원 순매도였다.
  ↳ 출처: `flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 반등에도 중기 약세와 지표 혼조로 신중한 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 반등했으나 20일 누적 하락폭이 매우 커 중기 약세 국면이 지속되고 있습니다.
- 핵심 주장: 한국 월별 지표(2026년 8~9월)는 심리·고용·수출은 긍정이나 생산·소비는 부진하여 경기 방향성에 불확실성이 큽니다.
- 핵심 주장: 외국인 순매수와 원화 강세에도 불구하고, 최근 변동성 확대와 미국 증시 약세가 부담 요인입니다.

### 수급 담당자
- 한줄 요약: 외국인 저점매수와 개인의 방어적 매수세가 KOSPI 중심으로 유입되는 국면입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 외국인 매수세는 KOSPI에 집중되었으며, 저점 반등 및 환율 안정(USD/KRW 하락)이 주요 배경입니다.
- 핵심 주장: 기관은 대규모 매도, 개인은 하락장에서 추가 매수 유입이지만, 최근 20일 누적 하락(-19.8%)을 감안하면 추격성·방어적 성격이 혼재합니다.
- 핵심 주장: 핵심 키워드: 저점반등, 환율안정, 연준/금리, 미국지수 급락, 국내 변동성 직접 판단 제한적 (VKOSPI 미제공)

### 섹터 담당자
- 한줄 요약: 단기 반등에도 불구하고 중기 불확실성은 여전합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 약 -20% 급락 후 단기 반등세를 보이고 있습니다.
- 핵심 주장: 외국인 순매수와 원화 강세가 단기 심리 개선에 기여하고 있습니다.
- 핵심 주장: 중기적으로는 생산·소비 부진과 경기 혼조가 부담 요인입니다.

### 리스크 담당자
- 한줄 요약: 중기 약세 누적이 크지만 단기 반등 신호도 일부 확인됩니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큼
- 핵심 주장: 생산·소비 지표 부진, 심리·수출은 긍정
- 핵심 주장: 외국인 순매수와 원화 강세가 단기 완화 신호

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 전환 신호는 아직 뚜렷하지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 지속
- 핵심 주장: 외국인 순매수에도 실적 추정치 상향 신호는 부재
- 핵심 주장: 단기 반등은 수급·심리 영향, 실적 추세 반전 신호는 미약

### 브레드스 담당자
- 한줄 요약: 단기 반등에도 하락 추세가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크다.
- 핵심 주장: 오늘 반등에도 시장 전반 확산은 약하다.
- 핵심 주장: 수급과 변동성 지표 모두 불안정하다.

### 유동성 담당자
- 한줄 요약: 정책·유동성 환경이 위험회피(RISK_OFF) 국면에 가깝습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 변동성 상승이 위험회피 신호입니다.
- 핵심 주장: VIX와 미국 금리, 유가 등 정책 민감 지표도 불안정합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 반등에도 중기 약세와 지표 혼조로 신중한 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+2692억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw_pct, snapshot.markets.us.sp500_pct, snapshot.markets.us.nasdaq_pct, snapshot.cumulative_context.vix_5d_avg
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 저점매수와 개인의 방어적 매수세가 KOSPI 중심으로 유입되는 국면입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.05%, usdkrw=1334.89입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.market_summary.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 반등에도 불구하고 중기 불확실성은 여전합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+2692억, usdkrw=1334.89입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '중기 약세 누적이 크지만 단기 반등 신호도 일부 확인됩니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+2692억, usdkrw=1334.89입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.vix_5d_avg
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 전환 신호는 아직 뚜렷하지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+2692억, kospi_change_pct=+2.05%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.kospi_change_pct
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '단기 반등에도 하락 추세가 뚜렷합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.vix_5d_avg, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책·유동성 환경이 위험회피(RISK_OFF) 국면에 가깝습니다.' 의견을 유지합니다. 근거 숫자는 vix=20.0, dxy=101.78입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.markets.volatility.vix, snapshot.macro.daily.us10y, snapshot.macro.daily.oil_wti, snapshot.macro.daily.dxy, snapshot.market_summary.usdkrw
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI +2.05%, USD/KRW 1334.89(-0.52%), VIX 20.0, 외국인 +2692억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 단기 반등의 지속성: 다수=매크로·이익모멘텀·브레드스·유동성 담당자는 누적 하락과 변동성 확대로 방어적 기조가 필요하다고 판단한다., 소수=수급·섹터·리스크 담당자는 외국인 순매수와 원화 강세를 단기 반등의 확인 신호로 본다., 에이전트=[flow, sector, risk]
  - 의미: 현 반등이 추세 전환인지 낙폭과대 되돌림인지를 가르는 핵심이다. 핵심 수급은 긍정적이지만 20일 누적 하락과 해외 위험회피가 이를 제약한다.
- 개인 수급의 해석: 다수=제공된 실제 수급 기준 개인은 전체 6,034억원, KOSPI 5,126억원 순매도로 반등을 추격하는 매수 주체로 보기 어렵다., 소수=수급 담당자는 개인의 방어적 매수 유입 가능성을 언급했다., 에이전트=[flow]
  - 의미: 개인 매수 전제를 두면 반등의 수급 폭을 과대평가할 수 있다. 당일 결론은 제공된 순매도 수치를 우선해야 한다.
- 국내 경기 배경: 다수=월별 국내 지표는 생산·소비 부진을 고려해 경기 회복을 단정하기 어렵다는 평가다., 소수=심리·고용·수출 개선은 내수 부진을 일부 완충할 수 있다는 해석이다., 에이전트=[sector, risk]
  - 의미: 월별 지표는 일간 주가 움직임의 직접 원인이 아니지만, 반등 이후 이익·내수 회복의 지속성을 판단하는 중기 기준이다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 단기 반등했으나 20일 누적 하락폭이 매우 커 중기 약세 국면이 지속되고 있습니다.",
    "한국 월별 지표(2026년 8~9월)는 심리·고용·수출은 긍정이나 생산·소비는 부진하여 경기 방향성에 불확실성이 큽니다.",
    "외국인 순매수와 원화 강세에도 불구하고, 최근 변동성 확대와 미국 증시 약세가 부담 요인입니다."
  ],
  "korean_comment": "단기 반등에도 중기 약세와 지표 혼조로 신중한 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre_analysis_KR",
  "core_claims": [
    "외국인 매수세는 KOSPI에 집중되었으며, 저점 반등 및 환율 안정(USD/KRW 하락)이 주요 배경입니다.",
    "기관은 대규모 매도, 개인은 하락장에서 추가 매수 유입이지만, 최근 20일 누적 하락(-19.8%)을 감안하면 추격성·방어적 성격이 혼재합니다.",
    "핵심 키워드: 저점반등, 환율안정, 연준/금리, 미국지수 급락, 국내 변동성 직접 판단 제한적 (VKOSPI 미제공)"
  ],
  "korean_comment": "외국인 저점매수와 개인의 방어적 매수세가 KOSPI 중심으로 유입되는 국면입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "MED"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 최근 20일간 약 -20% 급락 후 단기 반등세를 보이고 있습니다.",
    "외국인 순매수와 원화 강세가 단기 심리 개선에 기여하고 있습니다.",
    "중기적으로는 생산·소비 부진과 경기 혼조가 부담 요인입니다."
  ],
  "korean_comment": "단기 반등에도 불구하고 중기 불확실성은 여전합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
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
    "KOSPI 20일 누적 하락폭이 매우 큼",
    "생산·소비 지표 부진, 심리·수출은 긍정",
    "외국인 순매수와 원화 강세가 단기 완화 신호"
  ],
  "korean_comment": "중기 약세 누적이 크지만 단기 반등 신호도 일부 확인됩니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 지속",
    "외국인 순매수에도 실적 추정치 상향 신호는 부재",
    "단기 반등은 수급·심리 영향, 실적 추세 반전 신호는 미약"
  ],
  "korean_comment": "실적 추정치 상향 전환 신호는 아직 뚜렷하지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.kospi_change_pct"
  ],
  "confidence": "MED"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크다.",
    "오늘 반등에도 시장 전반 확산은 약하다.",
    "수급과 변동성 지표 모두 불안정하다."
  ],
  "korean_comment": "단기 반등에도 하락 추세가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 20일 누적 급락과 변동성 상승이 위험회피 신호입니다.",
    "VIX와 미국 금리, 유가 등 정책 민감 지표도 불안정합니다."
  ],
  "korean_comment": "정책·유동성 환경이 위험회피(RISK_OFF) 국면에 가깝습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.markets.volatility.vix",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.oil_wti",
    "snapshot.macro.daily.dxy",
    "snapshot.market_summary.usdkrw"
  ],
  "confidence": "HIGH"
}
```