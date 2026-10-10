# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-10**
- 생성 시각(UTC): `2026-10-10T00:52:49.219234+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -2.62% / KOSDAQ -0.69%
- **미국 지수**: S&P500 +0.59% / NASDAQ +0.64% / DOW +0.83%
- **환율/변동성**: USD/KRW 1341.59 (-0.19%) / VIX 14.8
- **시장 요약 노트**: KOSPI -2.62%, USD/KRW 1341.59. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -20079억 / 기관 -17864억 / 개인 +30455억
- **일간 매크로**: 미10년 5.24% / 미2년 4.06% / 2-10 1.19%p / DXY 102.23
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.71% / Core CPI YoY 2.76% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.20% / 기준금리 3.75% / 실질금리 2.91%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 6,625.93으로 2.62% 하락했고, 5일 누적 -10.727%와 반전 신호 부재가 단기 추세 훼손을 보여줍니다.
  ↳ 출처: `market_data, cumulative_context`
- 10월 8일 외국인 -2조79억원, 기관 -1조7,864억원을 개인 +3조455억원이 흡수해 수급의 질이 불안정합니다.
  ↳ 출처: `flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표와 단기 시장 흐름이 모두 보수적 해석을 요구합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 5일간 -10% 이상 급락하며 단기 약세가 뚜렷합니다.
- 핵심 주장: 한국 월별 지표는 심리·고용·수출은 긍정이나 생산·소비는 부진하여 경기 혼조가 지속됩니다.
- 핵심 주장: 외국인·기관 동반 순매도와 누적 하락세로 단기 반전 신호는 아직 확인되지 않습니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저점 추격매수로 수급 불안정 심화.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 최근 KOSPI 5일간 -10% 급락과 연준/금리 불확실성, 반도체/AI 테마 약세가 복합적으로 작용.
- 핵심 주장: USD/KRW는 소폭 하락했으나, 외국인 매도와 동반되지 않아 환율 주도 자금 유출은 아님(포트폴리오 리밸런싱/차익실현 가능성).
- 핵심 주장: 개인 대규모 순매수는 저점 인식에 따른 레버리지 추격 매수 성격이 강해 지속성에 의문.

### 섹터 담당자
- 한줄 요약: 수급과 단기 낙폭 모두 위험 신호가 강합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 -10% 이상 급락하며 약세가 심화되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 지속되고 있습니다.
- 핵심 주장: 중기적으로 국내 경기지표는 혼조이나 단기 시장심리는 매우 부정적입니다.

### 리스크 담당자
- 한줄 요약: 단기·중기 모두 수급과 지수 흐름이 부정적입니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락폭이 매우 큼
- 핵심 주장: 외국인·기관 대규모 순매도 지속
- 핵심 주장: 중기적으로도 코스피 약세 흐름

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀 약화와 수급 악화가 동반되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 -10% 이상 급락, 실적 모멘텀 약화 신호.
- 핵심 주장: 외국인·기관 동반 대규모 순매도, 이익 추정치 하향 압력.
- 핵심 주장: 실적 추정치 상향 전환 신호 부재, 단기 반등 모멘텀 약함.

### 브레드스 담당자
- 한줄 요약: 시장 내부 확산 약화와 단기 낙폭이 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락폭이 매우 크고, 20일도 약세 지속
- 핵심 주장: 수급은 외국인·기관 동반 매도, 시장 내부 확산 약화
- 핵심 주장: 미국지수 강세와 달리 국내 시장만 단기 급락

### 유동성 담당자
- 한줄 요약: 유동성 악화와 외국인 이탈로 보수적 대응이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 급락과 외국인 대규모 순매도 지속.
- 핵심 주장: 환율 변동성은 제한적이나, 유동성 위축 신호 뚜렷.
- 핵심 주장: 정책 불확실성 및 금리 부담이 위험회피 심리 강화.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표와 단기 시장 흐름이 모두 보수적 해석을 요구합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.korea_macro_context
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저점 추격매수로 수급 불안정 심화.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.62%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines, snapshot.macro.daily.us10y
- [섹터 담당자] 저는 섹터 담당자 입장에서 '수급과 단기 낙폭 모두 위험 신호가 강합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.note, snapshot.market_summary.note, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기·중기 모두 수급과 지수 흐름이 부정적입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀 약화와 수급 악화가 동반되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.kospi_change_pct
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 내부 확산 약화와 단기 낙폭이 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.kr.kospi_pct, snapshot.markets.us.sp500_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 악화와 외국인 이탈로 보수적 대응이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.macro.daily.vix, snapshot.phase_two_signals.liquidity_signal_score, snapshot.news_headlines
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -2.62%, USD/KRW 1341.59(-0.19%), VIX 14.8, 외국인 -20079억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 국내 위험회피와 대외 안정 신호의 충돌: 다수=매크로·수급·섹터·이익·브레드스·유동성 담당자는 국내 지수 급락과 외국인·기관 매도를 근거로 리스크 오프를 주장했습니다., 소수=미국 3대 지수 상승, USD/KRW 0.19% 하락, VIX 14.84는 전면적 글로벌 위험회피와는 다른 신호입니다., 에이전트=[해당 없음]
  - 의미: 국내 약세의 원인이 글로벌 충격보다 포트폴리오 조정에 가깝다면 반등 가능성은 남지만, 현재 반전 신호는 확인되지 않았습니다.
- 리스크 담당자의 체제 태그 불일치: 다수=7명 중 6명은 명시적으로 RISK_OFF 태그를 제시했고 전원 보수적 대응에 동의했습니다., 소수=리스크 담당자는 RISK_ON 태그를 달았지만 실제 주장은 수급·지수 흐름이 부정적이라는 내용이었습니다., 에이전트=[risk]
  - 의미: 태그보다 실제 근거와 결론을 우선해야 하며, 공격적 위험선호 의견으로 해석하면 안 됩니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 최근 5일간 -10% 이상 급락하며 단기 약세가 뚜렷합니다.",
    "한국 월별 지표는 심리·고용·수출은 긍정이나 생산·소비는 부진하여 경기 혼조가 지속됩니다.",
    "외국인·기관 동반 순매도와 누적 하락세로 단기 반전 신호는 아직 확인되지 않습니다."
  ],
  "korean_comment": "중기 지표와 단기 시장 흐름이 모두 보수적 해석을 요구합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.korea_macro_context"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre_analysis_KR",
  "core_claims": [
    "외국인 대규모 순매도는 최근 KOSPI 5일간 -10% 급락과 연준/금리 불확실성, 반도체/AI 테마 약세가 복합적으로 작용.",
    "USD/KRW는 소폭 하락했으나, 외국인 매도와 동반되지 않아 환율 주도 자금 유출은 아님(포트폴리오 리밸런싱/차익실현 가능성).",
    "개인 대규모 순매수는 저점 인식에 따른 레버리지 추격 매수 성격이 강해 지속성에 의문."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저점 추격매수로 수급 불안정 심화.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.markets.volatility.vix"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 최근 5일간 -10% 이상 급락하며 약세가 심화되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 지속되고 있습니다.",
    "중기적으로 국내 경기지표는 혼조이나 단기 시장심리는 매우 부정적입니다."
  ],
  "korean_comment": "수급과 단기 낙폭 모두 위험 신호가 강합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.market_summary.note",
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
    "KOSPI 5일 누적 하락폭이 매우 큼",
    "외국인·기관 대규모 순매도 지속",
    "중기적으로도 코스피 약세 흐름"
  ],
  "korean_comment": "단기·중기 모두 수급과 지수 흐름이 부정적입니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
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
    "KOSPI 5일 누적 -10% 이상 급락, 실적 모멘텀 약화 신호.",
    "외국인·기관 동반 대규모 순매도, 이익 추정치 하향 압력.",
    "실적 추정치 상향 전환 신호 부재, 단기 반등 모멘텀 약함."
  ],
  "korean_comment": "실적 모멘텀 약화와 수급 악화가 동반되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
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
    "KOSPI 5일 누적 하락폭이 매우 크고, 20일도 약세 지속",
    "수급은 외국인·기관 동반 매도, 시장 내부 확산 약화",
    "미국지수 강세와 달리 국내 시장만 단기 급락"
  ],
  "korean_comment": "시장 내부 확산 약화와 단기 낙폭이 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.us.sp500_pct"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 5일 누적 급락과 외국인 대규모 순매도 지속.",
    "환율 변동성은 제한적이나, 유동성 위축 신호 뚜렷.",
    "정책 불확실성 및 금리 부담이 위험회피 심리 강화."
  ],
  "korean_comment": "유동성 악화와 외국인 이탈로 보수적 대응이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.vix",
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```