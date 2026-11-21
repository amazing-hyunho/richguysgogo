# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-11-20**
- 생성 시각(UTC): `2026-11-20T00:52:28.588913+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -4.69% / KOSDAQ -4.52%
- **미국 지수**: S&P500 -2.02% / NASDAQ -2.25% / DOW -2.19%
- **환율/변동성**: USD/KRW 1330.97 (+0.35%) / VIX 28.4
- **시장 요약 노트**: KOSPI -4.69%, USD/KRW 1330.97. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -4848억 / 기관 -3183억 / 개인 +7431억
- **일간 매크로**: 미10년 5.05% / 미2년 4.15% / 2-10 0.90%p / DXY 103.92
- **월간 매크로**: 실업률 4.10% / CPI YoY 4.08% / Core CPI YoY 2.87% / PMI n/a
- **분기/구조**: GDP QoQ 연율 3.40% / 기준금리 3.88% / 실질금리 2.89%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 4,896.90(-4.69%), KOSDAQ은 653.86(-4.52%)로 급락했고 외국인 -4,848억원, 기관 -3,183억원이 하락을 주도했습니다.
  ↳ 출처: `CORE_SIGNALS, korean_market_flow_breakdown`
- VIX 28.44와 미국 10년물 5.052%가 부담이며, 연준 추가 인상 및 AI 과열 관련 뉴스가 성장주 위험회피를 강화했습니다.
  ↳ 출처: `SUPPORTING_SIGNALS, news_digest`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표는 일부 긍정적이나, 단기 시장 충격이 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락폭이 -11%를 넘으며 시장 전반에 위험회피 심리가 강하게 반영되고 있습니다.
- 핵심 주장: 한국 월별 지표(2026년 9~10월)는 생산·소비·고용·수출이 긍정적이나, 경기·심리 혼조로 단기 급락과 상충됩니다.
- 핵심 주장: 글로벌 변동성(VIX 28)과 외국인 대규모 순매도도 단기적으로 위험 신호입니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저가매수 흡수이나 수급 불안 지속.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인은 KOSPI와 KOSDAQ 모두에서 대규모 순매도, 이는 고금리/연준, 글로벌 변동성(VIX), 반도체/AI 이슈가 복합적으로 작용.
- 핵심 주장: USD/KRW 상승과 외국인 매도 동반, FX-driven 유출이 주요 원인.
- 핵심 주장: 개인은 대규모 저가매수에 나섰으나, 최근 5~20일 누적 하락폭과 변동성 감안 시 지속성은 낮음.

### 섹터 담당자
- 한줄 요약: 수급과 변동성, 누적 하락폭 모두 위험 회피 신호가 강합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 -11%로 하락세가 심화되고 있습니다.
- 핵심 주장: 외국인·기관 동반 순매도와 변동성(VIX) 급등이 위험 신호입니다.
- 핵심 주장: 중기 한국 경기지표는 혼조이나, 단기 시장 분위기는 RISK_OFF입니다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 걸친 위험 신호가 명확하게 포착됩니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일간 -11% 이상 급락
- 핵심 주장: 외국인·기관 대규모 순매도 지속
- 핵심 주장: 변동성(VIX) 급등 및 반전 신호 부재

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 하향 압력이 뚜렷하게 강화되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려가 커짐
- 핵심 주장: 외국인·기관 대규모 순매도는 실적 전망 하향 압력 신호
- 핵심 주장: 단기 급락은 일시적 헤드라인 영향이 있으나, 추세적 실적 하향 리스크가 우세

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸친 약세 확산이 지속되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고, 단기 반전 신호도 없음.
- 핵심 주장: 시장 변동성(VIX)과 하락폭 모두 과도하게 확대되어 확산 약세가 뚜렷함.
- 핵심 주장: 수급도 외국인·기관 동반 순매도, 시장 내부 확산 악화.

### 유동성 담당자
- 한줄 요약: 유동성 환경이 급격히 악화되어 위험회피 국면이 강화되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 변동성 급등이 유동성 악화 신호입니다.
- 핵심 주장: 외국인 대규모 순매도와 VIX 28대는 위험회피 심리를 반영합니다.
- 핵심 주장: 달러/원 환율 상승과 미국 금리 고점도 정책 부담을 가중시킵니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표는 일부 긍정적이나, 단기 시장 충격이 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 vix=28.4, foreign_net=-4848억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.korea_macro_context, snapshot.markets.volatility.vix, snapshot.flow_summary.foreign_net, snapshot.market_summary.kospi_change_pct
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저가매수 흡수이나 수급 불안 지속.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-4.69%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.macro.daily.vix, snapshot.news_headlines, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '수급과 변동성, 누적 하락폭 모두 위험 회피 신호가 강합니다.' 의견을 유지합니다. 근거 숫자는 vix=28.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.markets.volatility.vix, snapshot.korea_macro_context, snapshot.news_headlines
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 걸친 위험 신호가 명확하게 포착됩니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4848억, institution_net=-3183억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.kospi_change_pct
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 하향 압력이 뚜렷하게 강화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4848억, institution_net=-3183억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸친 약세 확산이 지속되고 있습니다.' 의견을 유지합니다. 근거 숫자는 vix=28.4, foreign_net=-4848억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct, snapshot.markets.volatility.vix, snapshot.flow_summary.foreign_net
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 환경이 급격히 악화되어 위험회피 국면이 강화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4848억, vix=28.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.vix_5d_avg, snapshot.markets.fx.usdkrw, snapshot.markets.fx.usdkrw_pct, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -4.69%, USD/KRW 1330.97(+0.35%), VIX 28.4, 외국인 -4848억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 단기 위험 국면의 분류: 다수=매크로·수급·섹터·이익·브레드스·유동성 담당자는 누적 하락, 높은 변동성, 외국인 매도를 근거로 리스크 오프를 제시했습니다., 소수=리스크 담당자의 태그는 RISK_ON이지만 실제 주장은 위험 신호 확대와 반전 신호 부재를 강조해 내용상 다수 의견과 가깝습니다., 에이전트=[risk]
  - 의미: 태그와 주장 간 불일치가 있어 명목상 소수 의견을 공격적 위험선호 신호로 해석하면 안 됩니다.
- 국내 경기 배경과 일별 시장 신호: 다수=당일 급락과 외국인·기관 동반 매도, VIX 상승을 우선해 단기 방어적 판단을 유지합니다., 소수=9~10월 생산·소비·고용·수출 지표는 중기 경기의 일부 회복 가능성을 보여줍니다., 에이전트=[macro]
  - 의미: 월별 실물 개선은 중기 완충재지만 오늘의 수급 악화와 동일시할 수 없으며, 반전 확인 없이 저가매수 근거로 쓰기 어렵습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 -11%를 넘으며 시장 전반에 위험회피 심리가 강하게 반영되고 있습니다.",
    "한국 월별 지표(2026년 9~10월)는 생산·소비·고용·수출이 긍정적이나, 경기·심리 혼조로 단기 급락과 상충됩니다.",
    "글로벌 변동성(VIX 28)과 외국인 대규모 순매도도 단기적으로 위험 신호입니다."
  ],
  "korean_comment": "중기 지표는 일부 긍정적이나, 단기 시장 충격이 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.markets.volatility.vix",
    "snapshot.flow_summary.foreign_net",
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
    "외국인은 KOSPI와 KOSDAQ 모두에서 대규모 순매도, 이는 고금리/연준, 글로벌 변동성(VIX), 반도체/AI 이슈가 복합적으로 작용.",
    "USD/KRW 상승과 외국인 매도 동반, FX-driven 유출이 주요 원인.",
    "개인은 대규모 저가매수에 나섰으나, 최근 5~20일 누적 하락폭과 변동성 감안 시 지속성은 낮음."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저가매수 흡수이나 수급 불안 지속.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.macro.daily.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI 20일 누적 -11%로 하락세가 심화되고 있습니다.",
    "외국인·기관 동반 순매도와 변동성(VIX) 급등이 위험 신호입니다.",
    "중기 한국 경기지표는 혼조이나, 단기 시장 분위기는 RISK_OFF입니다."
  ],
  "korean_comment": "수급과 변동성, 누적 하락폭 모두 위험 회피 신호가 강합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.markets.volatility.vix",
    "snapshot.korea_macro_context",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK pre-analysis agent",
  "core_claims": [
    "KOSPI 20일간 -11% 이상 급락",
    "외국인·기관 대규모 순매도 지속",
    "변동성(VIX) 급등 및 반전 신호 부재"
  ],
  "korean_comment": "시장 전반에 걸친 위험 신호가 명확하게 포착됩니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.market_summary.kospi_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려가 커짐",
    "외국인·기관 대규모 순매도는 실적 전망 하향 압력 신호",
    "단기 급락은 일시적 헤드라인 영향이 있으나, 추세적 실적 하향 리스크가 우세"
  ],
  "korean_comment": "실적 추정치 하향 압력이 뚜렷하게 강화되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.earnings_signal_score",
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
    "KOSPI 20일 누적 하락폭이 매우 크고, 단기 반전 신호도 없음.",
    "시장 변동성(VIX)과 하락폭 모두 과도하게 확대되어 확산 약세가 뚜렷함.",
    "수급도 외국인·기관 동반 순매도, 시장 내부 확산 악화."
  ],
  "korean_comment": "시장 전반에 걸친 약세 확산이 지속되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.breadth_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 20일 누적 급락과 변동성 급등이 유동성 악화 신호입니다.",
    "외국인 대규모 순매도와 VIX 28대는 위험회피 심리를 반영합니다.",
    "달러/원 환율 상승과 미국 금리 고점도 정책 부담을 가중시킵니다."
  ],
  "korean_comment": "유동성 환경이 급격히 악화되어 위험회피 국면이 강화되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.markets.fx.usdkrw",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.macro.daily.us10y"
  ],
  "confidence": "HIGH"
}
```