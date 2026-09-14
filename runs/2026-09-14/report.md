# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-09-14**
- 생성 시각(UTC): `2026-09-14T00:52:32.467104+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=0, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -2.87% / KOSDAQ -1.45%
- **미국 지수**: S&P500 +0.86% / NASDAQ +0.96% / DOW +0.98%
- **환율/변동성**: USD/KRW 1342.63 (+0.24%) / VIX 15.8
- **시장 요약 노트**: KOSPI -2.87%, USD/KRW 1342.63. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -14835억 / 기관 -4062억 / 개인 +16524억
- **일간 매크로**: 미10년 4.97% / 미2년 3.91% / 2-10 1.06%p / DXY 99.18
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.71% / Core CPI YoY 2.76% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.61%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 6,712.37로 2.87% 하락했고 KOSDAQ도 808.71로 1.45% 내렸다. 외국인 -1조4,835억원, 기관 -4,062억원 순매도에 개인 +1조6,524억원 순매수가 대응했다.
  ↳ 출처: `flow_data, market_data`
- USD/KRW는 1,342.63으로 0.24% 상승했고 KOSPI 5일 누적 수익률은 -4.07%다. 금리·인플레이션 및 환율 뉴스가 외국인 이탈과 위험회피 해석을 뒷받침한다.
  ↳ 출처: `macro_daily, cumulative_context, news`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 국내 증시는 외국인 이탈과 환율 상승으로 단기 위험 신호가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 5일간 -4% 이상 하락하며 약세가 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도, 원화 약세가 동반되고 있습니다.
- 핵심 주장: 미국 증시 강세와 달리 국내 시장은 단기적으로 불안정한 모습입니다.

### 수급 담당자
- 한줄 요약: 고환율·금리 불확실성에 외국인 매도 집중, 개인이 단기 반등 기대 매수로 흡수 중.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고환율(USD/KRW 상승)과 연준/금리 불확실성, 인플레이션 우려가 복합적으로 작용.
- 핵심 주장: KOSPI 중심의 외국인 매도세는 FX-driven outflow 성격이 강하며, 최근 5일간 누적 하락세와 연동.
- 핵심 주장: 개인 매수세는 레버리지 추격성 성격이 짙어, 지속 가능성에 의문.

### 섹터 담당자
- 한줄 요약: 시장 전반에 걸쳐 위험회피 심리가 강하게 작용하고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 -4% 이상 하락하며 약세가 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.
- 핵심 주장: 환율 상승과 함께 투자심리가 위축된 모습입니다.

### 리스크 담당자
- 한줄 요약: 단기 약세가 뚜렷하지만 시스템적 위험 신호는 아직 부족합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 5일간 -4% 이상 하락
- 핵심 주장: 외국인 대규모 순매도 지속
- 핵심 주장: 환율 상승세와 변동성은 제한적

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 모멘텀은 부재하며, 하락 추세가 이어집니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 약화가 지속되고 있습니다.
- 핵심 주장: 외국인 대규모 순매도와 코스피 누적 하락이 뚜렷합니다.

### 브레드스 담당자
- 한줄 요약: 시장 내부 확산 약화와 외국인 매도세가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 최근 5일간 하락세가 뚜렷하다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 지속되고 있다.
- 핵심 주장: 시장 전반의 확산도(breadth) 약화가 뚜렷하다.

### 유동성 담당자
- 한줄 요약: 정책 및 유동성 환경이 위험회피로 전환되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락과 외국인 대규모 순매도 지속.
- 핵심 주장: USD/KRW 상승세와 변동성 지표 안정에도 불구, 정책 불확실성 부각.
- 핵심 주장: 유동성 신호는 단기적으로 악화.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '국내 증시는 외국인 이탈과 환율 상승으로 단기 위험 신호가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14835억, institution_net=-4062억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.usdkrw, snapshot.markets.fx.usdkrw_pct, snapshot.markets.kr.kospi_pct, snapshot.news_headlines
- [수급 담당자] 저는 수급 담당자 입장에서 '고환율·금리 불확실성에 외국인 매도 집중, 개인이 단기 반등 기대 매수로 흡수 중.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.87%, usdkrw=1342.63입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.market_summary.usdkrw, snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.macro.daily.usdkrw, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 걸쳐 위험회피 심리가 강하게 작용하고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14835억, institution_net=-4062억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 약세가 뚜렷하지만 시스템적 위험 신호는 아직 부족합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14835억, usdkrw=1342.63입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 모멘텀은 부재하며, 하락 추세가 이어집니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14835억, kospi_change_pct=-2.87%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 내부 확산 약화와 외국인 매도세가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14835억, institution_net=-4062억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.breadth_signal_score, snapshot.cumulative_context.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 및 유동성 환경이 위험회피로 전환되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-14835억, usdkrw=1342.63입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.phase_two_signals.liquidity_signal_score, snapshot.news_headlines, snapshot.cumulative_context.note
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -2.87%, USD/KRW 1342.63(+0.24%), VIX 15.8, 외국인 -14835억이고, 뉴스는 반등·회복 기대가 섞인 완화 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 위험회피의 강도와 시스템 리스크 여부: 다수=매크로·수급·섹터·이익모멘텀·브레드스·유동성 담당자는 외국인·기관 동반 매도와 환율 상승을 근거로 단기 리스크 오프가 우세하다고 판단했다., 소수=리스크 담당자는 단기 약세는 인정하지만 VIX가 15.84이고 5일 평균도 16.1인 점을 들어 시스템적 위험 신호는 아직 부족하다고 봤다., 에이전트=[risk]
  - 의미: 해외 증시 반등과 제한된 변동성은 급락 추격 매도의 근거를 약화시키지만, 외국인 순매도와 원화 약세가 이어지면 국내 수급 악화라는 핵심 판단은 유지된다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO_pre_analysis_agent",
  "core_claims": [
    "KOSPI가 최근 5일간 -4% 이상 하락하며 약세가 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도, 원화 약세가 동반되고 있습니다.",
    "미국 증시 강세와 달리 국내 시장은 단기적으로 불안정한 모습입니다."
  ],
  "korean_comment": "국내 증시는 외국인 이탈과 환율 상승으로 단기 위험 신호가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.news_headlines",
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
    "외국인 대규모 순매도는 고환율(USD/KRW 상승)과 연준/금리 불확실성, 인플레이션 우려가 복합적으로 작용.",
    "KOSPI 중심의 외국인 매도세는 FX-driven outflow 성격이 강하며, 최근 5일간 누적 하락세와 연동.",
    "개인 매수세는 레버리지 추격성 성격이 짙어, 지속 가능성에 의문."
  ],
  "korean_comment": "고환율·금리 불확실성에 외국인 매도 집중, 개인이 단기 반등 기대 매수로 흡수 중.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.usdkrw",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
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
    "KOSPI가 최근 5일간 -4% 이상 하락하며 약세가 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.",
    "환율 상승과 함께 투자심리가 위축된 모습입니다."
  ],
  "korean_comment": "시장 전반에 걸쳐 위험회피 심리가 강하게 작용하고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.news_headlines",
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
    "KOSPI가 최근 5일간 -4% 이상 하락",
    "외국인 대규모 순매도 지속",
    "환율 상승세와 변동성은 제한적"
  ],
  "korean_comment": "단기 약세가 뚜렷하지만 시스템적 위험 신호는 아직 부족합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
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
    "실적 모멘텀 약화가 지속되고 있습니다.",
    "외국인 대규모 순매도와 코스피 누적 하락이 뚜렷합니다."
  ],
  "korean_comment": "실적 추정치 상향 모멘텀은 부재하며, 하락 추세가 이어집니다.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.note"
  ]
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI와 KOSDAQ 모두 최근 5일간 하락세가 뚜렷하다.",
    "외국인과 기관의 대규모 순매도세가 지속되고 있다.",
    "시장 전반의 확산도(breadth) 약화가 뚜렷하다."
  ],
  "korean_comment": "시장 내부 확산 약화와 외국인 매도세가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 5일 누적 하락과 외국인 대규모 순매도 지속.",
    "USD/KRW 상승세와 변동성 지표 안정에도 불구, 정책 불확실성 부각.",
    "유동성 신호는 단기적으로 악화."
  ],
  "korean_comment": "정책 및 유동성 환경이 위험회피로 전환되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```