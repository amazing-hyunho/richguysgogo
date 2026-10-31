# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-30**
- 생성 시각(UTC): `2026-10-30T00:52:26.372905+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.95% / KOSDAQ -2.63%
- **미국 지수**: S&P500 -0.30% / NASDAQ -1.38% / DOW -0.25%
- **환율/변동성**: USD/KRW 1338.04 (+0.04%) / VIX 17.2
- **시장 요약 노트**: KOSPI -3.95%, USD/KRW 1338.04. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -3846억 / 기관 -2298억 / 개인 +5586억
- **일간 매크로**: 미10년 4.99% / 미2년 4.00% / 2-10 0.99%p / DXY 101.82
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 3.40% / 기준금리 3.75% / 실질금리 2.64%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 5,702.92로 3.95% 하락했고 외국인 -3,846억원, 기관 -2,298억원의 동반 순매도가 개인 +5,586억원보다 방향성을 주도했습니다.
  ↳ 출처: `flow_data, market_data`
- KOSPI 5일 누적은 +3.076%지만 20일 누적은 -21.534%이고 반전 신호도 없어, 하루 낙폭만으로 추세 전환을 판단하기 어렵습니다.
  ↳ 출처: `cumulative_context`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 불확실성과 단기 위험회피 신호가 동시에 나타납니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고, 단기 반전 신호는 없습니다.
- 핵심 주장: 한국 월별 지표는 생산·소비 부진과 수출·고용 개선이 혼재되어 중기 방향성 불확실성이 큽니다.
- 핵심 주장: 외국인·기관 동반 순매도와 변동성 지표(VIX)도 위험회피 심리를 시사합니다.

### 수급 담당자
- 한줄 요약: 고환율·금리 부담에 외국인 매도, 개인이 단기 저점매수로 흡수하는 공급우위 국면.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고환율·미국 금리 부담(금리/연준, 환율/달러)과 최근 KOSPI 급락(-21%/20일) 누적에 따른 위험회피가 주된 원인.
- 핵심 주장: KOSPI에서 외국인 매도 집중, USD/KRW 상승과 동반되어 FX-driven 유출 성격이 강함.
- 핵심 주장: 개인 대규모 순매수는 저가 반등 기대의 레버리지 추격매수 성격이 강해 지속성에 의문.

### 섹터 담당자
- 한줄 요약: 시장 전반에 걸쳐 약세와 수급 악화가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고 단기 반등 신호는 없음.
- 핵심 주장: 외국인·기관 동반 순매도, 시장 수급 악화 지속.
- 핵심 주장: 한국 실물지표는 생산·소비·투자 모두 부진, 중기 경기 개선 신호 미약.

### 리스크 담당자
- 한줄 요약: 중기 약세와 수급 악화가 동시에 확인됩니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 -21%로 중기 약세 지속
- 핵심 주장: 외국인·기관 동반 대규모 순매도
- 핵심 주장: 생산·소비·투자 등 실물지표 부진

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 하향 조정이 불가피한 구간입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 약화 신호가 뚜렷함
- 핵심 주장: 외국인·기관 동반 매도세로 이익 추정치 하향 압력
- 핵심 주장: 단기 반등 후 20일 누적 하락세 지속

### 브레드스 담당자
- 한줄 요약: 시장 전반의 하락 확산과 약한 반등 신호가 확인됩니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고, 단기 반등 신호는 약함.
- 핵심 주장: 시장 내 확산도(breadth) 지표가 부진하여 하락세가 광범위함.
- 핵심 주장: 수급도 외국인·기관 동반 매도세로 전환 신호 미약.

### 유동성 담당자
- 한줄 요약: 유동성 및 정책 민감 지표가 위험회피 신호를 강화하고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 외국인 대규모 순매도 지속
- 핵심 주장: 달러/원 강보합, 변동성(VIX)도 중립 이상 유지
- 핵심 주장: 정책·유동성 환경이 위험회피로 기울어 있음

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 5명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 불확실성과 단기 위험회피 신호가 동시에 나타납니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3846억, institution_net=-2298억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.volatility.vix
- [수급 담당자] 저는 수급 담당자 입장에서 '고환율·금리 부담에 외국인 매도, 개인이 단기 저점매수로 흡수하는 공급우위 국면.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.95%, usdkrw=1338.04입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.market_summary.usdkrw, snapshot.news_headlines
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 걸쳐 약세와 수급 악화가 뚜렷합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.flow_summary.note, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '중기 약세와 수급 악화가 동시에 확인됩니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.korea_macro_context
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 하향 조정이 불가피한 구간입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3846억, institution_net=-2298억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.kospi_change_pct
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 하락 확산과 약한 반등 신호가 확인됩니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3846억, institution_net=-2298억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.reversal_signal
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 및 정책 민감 지표가 위험회피 신호를 강화하고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3846억, dxy=101.82입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.macro.structural.fed_funds_rate, snapshot.macro.daily.dxy
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.95%, USD/KRW 1338.04(+0.04%), VIX 17.2, 외국인 -3846억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 위험 국면: 다수=매크로·수급·섹터·이익모멘텀·브레드스·유동성 담당자는 외국인·기관 매도와 20일 누적 하락을 근거로 리스크 오프를 제시했습니다., 소수=리스크 담당자의 태그는 RISK_ON이지만 실제 주장은 중기 약세와 수급 악화를 강조해 내용상 다수 의견과 가깝습니다., 에이전트=[risk]
  - 의미: 소수 태그와 서술이 일치하지 않아 이를 강세 신호로 해석할 수 없으며, 국면 판단의 신뢰도를 일부 낮춥니다.
- AI·반도체 뉴스의 시장 방어력: 다수=당일에는 외국인·기관 순매도와 지수 급락이 AI 관련 호재보다 강한 핵심 신호입니다., 소수=엔비디아의 네이버 투자 보도와 주간 AI·반도체 연구 의제는 중기 산업 수요의 긍정적 가능성을 제시합니다., 에이전트=[해당 없음]
  - 의미: 중기 연구 의제는 현재 수급이나 매매 신호가 아니므로, 관련 뉴스만으로 시장 전체의 추세 전환을 선언해서는 안 됩니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고, 단기 반전 신호는 없습니다.",
    "한국 월별 지표는 생산·소비 부진과 수출·고용 개선이 혼재되어 중기 방향성 불확실성이 큽니다.",
    "외국인·기관 동반 순매도와 변동성 지표(VIX)도 위험회피 심리를 시사합니다."
  ],
  "korean_comment": "중기 불확실성과 단기 위험회피 신호가 동시에 나타납니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre_analysis_KR",
  "core_claims": [
    "외국인 대규모 순매도는 고환율·미국 금리 부담(금리/연준, 환율/달러)과 최근 KOSPI 급락(-21%/20일) 누적에 따른 위험회피가 주된 원인.",
    "KOSPI에서 외국인 매도 집중, USD/KRW 상승과 동반되어 FX-driven 유출 성격이 강함.",
    "개인 대규모 순매수는 저가 반등 기대의 레버리지 추격매수 성격이 강해 지속성에 의문."
  ],
  "korean_comment": "고환율·금리 부담에 외국인 매도, 개인이 단기 저점매수로 흡수하는 공급우위 국면.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.markets.volatility.vix"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고 단기 반등 신호는 없음.",
    "외국인·기관 동반 순매도, 시장 수급 악화 지속.",
    "한국 실물지표는 생산·소비·투자 모두 부진, 중기 경기 개선 신호 미약."
  ],
  "korean_comment": "시장 전반에 걸쳐 약세와 수급 악화가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.flow_summary.note",
    "snapshot.korea_macro_context"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI 20일 누적 -21%로 중기 약세 지속",
    "외국인·기관 동반 대규모 순매도",
    "생산·소비·투자 등 실물지표 부진"
  ],
  "korean_comment": "중기 약세와 수급 악화가 동시에 확인됩니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
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
    "실적 모멘텀 약화 신호가 뚜렷함",
    "외국인·기관 동반 매도세로 이익 추정치 하향 압력",
    "단기 반등 후 20일 누적 하락세 지속"
  ],
  "korean_comment": "실적 추정치 하향 조정이 불가피한 구간입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.kospi_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고, 단기 반등 신호는 약함.",
    "시장 내 확산도(breadth) 지표가 부진하여 하락세가 광범위함.",
    "수급도 외국인·기관 동반 매도세로 전환 신호 미약."
  ],
  "korean_comment": "시장 전반의 하락 확산과 약한 반등 신호가 확인됩니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.reversal_signal"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 20일 누적 급락과 외국인 대규모 순매도 지속",
    "달러/원 강보합, 변동성(VIX)도 중립 이상 유지",
    "정책·유동성 환경이 위험회피로 기울어 있음"
  ],
  "korean_comment": "유동성 및 정책 민감 지표가 위험회피 신호를 강화하고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.macro.structural.fed_funds_rate",
    "snapshot.macro.daily.dxy"
  ],
  "confidence": "HIGH"
}
```