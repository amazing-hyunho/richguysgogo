# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-08-23**
- 생성 시각(UTC): `2026-08-23T00:53:01.236803+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=4, RISK_ON=1, RISK_OFF=2
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +0.88% / KOSDAQ -4.63%
- **미국 지수**: S&P500 +0.43% / NASDAQ +0.43% / DOW +0.98%
- **환율/변동성**: USD/KRW 1384.51 (-0.71%) / VIX 15.1
- **시장 요약 노트**: KOSPI 0.88%, USD/KRW 1384.51. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -4597억 / 기관 -981억 / 개인 -5416억
- **일간 매크로**: 미10년 4.74% / 미2년 3.71% / 2-10 1.03%p / DXY 98.80
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.54% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.40%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 6912.95(+0.88%)로 마감하며 20일 누적 +6.29%의 강세를 이어갔으나, KOSDAQ은 -4.63% 급락하며 시장 내부 확산 약화가 뚜렷합니다.
  ↳ 출처: `macro_daily, flow_data, cumulative_context`
- 외국인 -4597억, 기관 -981억 순매도세가 지속되며, 특히 KOSDAQ에서 외국인(-2837억)과 기관(-3462억) 동반 매도가 두드러졌습니다.
  ↳ 출처: `flow_data, korean_market_flow`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 변동성 확대와 외국인 매도세에 유의해야 합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 강한 상승세를 보였으나, 단기적으로 변동성이 확대되고 있습니다.
- 핵심 주장: 외국인과 기관의 순매도세가 지속되고 있어 추가 상승에는 불확실성이 존재합니다.
- 핵심 주장: 미국 금리와 환율, 글로벌 정책 불확실성 등 대외 변수에 주의가 필요합니다.

### 수급 담당자
- 한줄 요약: 외국인 매도세가 KOSDAQ에 집중되며, 개인이 이를 단기적으로 흡수하는 불안정한 수급 구도.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 순매도는 KOSDAQ에서 집중적으로 발생, 고금리/연준 및 반도체/AI 관련 불확실성(핵심 키워드) 영향.
- 핵심 주장: USD/KRW 하락에도 외국인 매도 지속, 이는 단순 환차익 실현보다는 글로벌 정책/금리 및 AI/반도체 테마 변동성에 따른 리밸런싱 가능성.
- 핵심 주장: 개인 매수는 KOSDAQ에서 레버리지 추종 성격이 강해 보이며, 최근 5일간 KOSDAQ 급락과 연동된 저가매수 시도이나 지속성은 낮음.

### 섹터 담당자
- 한줄 요약: 중기적으로 코스피는 긍정적 모멘텀을 유지하고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 6% 이상 상승하며 강한 흐름을 보이고 있습니다.
- 핵심 주장: 외국인과 기관의 순매도에도 불구하고 시장은 견조합니다.
- 핵심 주장: 변동성(VIX)과 환율도 안정적인 모습을 보입니다.

### 리스크 담당자
- 한줄 요약: 단기 조정에도 불구하고 중기적으로 위험 신호는 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 6% 이상 상승세를 보임
- 핵심 주장: 외국인과 기관의 순매도세가 지속되고 있음
- 핵심 주장: 시장 변동성(VIX)은 낮은 수준을 유지

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 조정 신호가 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀과 추정치 상향 신호는 부재하다.
- 핵심 주장: 20일 누적 코스피 강세에도 이익 추정치 상향은 확인되지 않는다.
- 핵심 주장: 단기 반등은 유동성 및 외부 요인 영향이 크다.

### 브레드스 담당자
- 한줄 요약: 지수는 견조하지만 내부 확산 약화가 뚜렷합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 견조한 상승세를 보임.
- 핵심 주장: KOSDAQ의 급락과 외국인 순매도는 시장 확산 약화를 시사.
- 핵심 주장: 시장 내부 확산도는 약화되어 단기적으로 중립적 국면.

### 유동성 담당자
- 한줄 요약: 유동성 환경이 불안정하여 신중한 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 정책 불확실성과 외국인 자금 이탈로 유동성 경계 필요.
- 핵심 주장: 환율 하락에도 변동성 상승과 외국인 매도세가 위험 신호.
- 핵심 주장: 5일 누적 코스피 상승에도 유동성 환경은 보수적.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 변동성 확대와 외국인 매도세에 유의해야 합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4597억, institution_net=-981억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.macro.daily.us10y, snapshot.macro.daily.dxy, snapshot.news_headlines, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도세가 KOSDAQ에 집중되며, 개인이 이를 단기적으로 흡수하는 불안정한 수급 구도.' 의견을 유지합니다. 근거 숫자는 dxy=98.80입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.macro.daily.dxy, snapshot.macro.daily.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '중기적으로 코스피는 긍정적 모멘텀을 유지하고 있습니다.' 의견을 유지합니다. 근거 숫자는 vix=15.1입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.markets.volatility.vix, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 조정에도 불구하고 중기적으로 위험 신호는 뚜렷하지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4597억, institution_net=-981억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.vix_5d_avg, snapshot.market_summary.note, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 조정 신호가 뚜렷하지 않습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수는 견조하지만 내부 확산 약화가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4597억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kosdaq_pct, snapshot.phase_two_signals.breadth_signal_score
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 환경이 불안정하여 신중한 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4597억, vix=15.1입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.foreign_net, snapshot.flow_summary.note, snapshot.markets.fx.usdkrw_pct, snapshot.markets.volatility.vix, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +0.88%, USD/KRW 1384.51(-0.71%), VIX 15.1, 외국인 -4597억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 중기 모멘텀 vs 단기 변동성: 다수=중립(NEUTRAL) — 단기 변동성 확대에도 중기적 코스피 강세 모멘텀은 유지, 소수=RISK_OFF — 유동성·수급 불안정으로 보수적 접근 필요, 에이전트=[flow, liquidity]
  - 의미: 단기 변동성 확대가 중기 모멘텀을 훼손할 경우, 시장 방향성 전환 신호로 작용할 수 있음
- 실적 모멘텀: 다수=실적 추정치 상향 신호 부재, 소수=섹터 담당자 — 중기 긍정 모멘텀 강조, 에이전트=[sector]
  - 의미: 실적 개선이 동반되지 않으면 단기 반등의 지속성에 한계가 있음

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 최근 20일간 강한 상승세를 보였으나, 단기적으로 변동성이 확대되고 있습니다.",
    "외국인과 기관의 순매도세가 지속되고 있어 추가 상승에는 불확실성이 존재합니다.",
    "미국 금리와 환율, 글로벌 정책 불확실성 등 대외 변수에 주의가 필요합니다."
  ],
  "korean_comment": "단기 변동성 확대와 외국인 매도세에 유의해야 합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.news_headlines",
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
    "외국인 순매도는 KOSDAQ에서 집중적으로 발생, 고금리/연준 및 반도체/AI 관련 불확실성(핵심 키워드) 영향.",
    "USD/KRW 하락에도 외국인 매도 지속, 이는 단순 환차익 실현보다는 글로벌 정책/금리 및 AI/반도체 테마 변동성에 따른 리밸런싱 가능성.",
    "개인 매수는 KOSDAQ에서 레버리지 추종 성격이 강해 보이며, 최근 5일간 KOSDAQ 급락과 연동된 저가매수 시도이나 지속성은 낮음."
  ],
  "korean_comment": "외국인 매도세가 KOSDAQ에 집중되며, 개인이 이를 단기적으로 흡수하는 불안정한 수급 구도.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.daily.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kosdaq_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 최근 20일간 6% 이상 상승하며 강한 흐름을 보이고 있습니다.",
    "외국인과 기관의 순매도에도 불구하고 시장은 견조합니다.",
    "변동성(VIX)과 환율도 안정적인 모습을 보입니다."
  ],
  "korean_comment": "중기적으로 코스피는 긍정적 모멘텀을 유지하고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
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
    "KOSPI는 최근 20일간 6% 이상 상승세를 보임",
    "외국인과 기관의 순매도세가 지속되고 있음",
    "시장 변동성(VIX)은 낮은 수준을 유지"
  ],
  "korean_comment": "단기 조정에도 불구하고 중기적으로 위험 신호는 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.market_summary.note",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀과 추정치 상향 신호는 부재하다.",
    "20일 누적 코스피 강세에도 이익 추정치 상향은 확인되지 않는다.",
    "단기 반등은 유동성 및 외부 요인 영향이 크다."
  ],
  "korean_comment": "실적 추정치 상향 조정 신호가 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "confidence": "MED",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.note",
    "snapshot.news_headlines"
  ]
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI는 최근 20일간 견조한 상승세를 보임.",
    "KOSDAQ의 급락과 외국인 순매도는 시장 확산 약화를 시사.",
    "시장 내부 확산도는 약화되어 단기적으로 중립적 국면."
  ],
  "korean_comment": "지수는 견조하지만 내부 확산 약화가 뚜렷합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kosdaq_pct",
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
    "정책 불확실성과 외국인 자금 이탈로 유동성 경계 필요.",
    "환율 하락에도 변동성 상승과 외국인 매도세가 위험 신호.",
    "5일 누적 코스피 상승에도 유동성 환경은 보수적."
  ],
  "korean_comment": "유동성 환경이 불안정하여 신중한 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.note",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.news_headlines",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```