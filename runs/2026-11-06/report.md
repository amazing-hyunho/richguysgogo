# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-11-06**
- 생성 시각(UTC): `2026-11-06T00:52:24.617719+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -7.84% / KOSDAQ -6.66%
- **미국 지수**: S&P500 -4.36% / NASDAQ -5.52% / DOW -3.44%
- **환율/변동성**: USD/KRW 1340.31 (-0.01%) / VIX 28.2
- **시장 요약 노트**: KOSPI -7.84%, USD/KRW 1340.31. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -3234억 / 기관 +2824억 / 개인 -20억
- **일간 매크로**: 미10년 4.84% / 미2년 3.99% / 2-10 0.85%p / DXY 101.49
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 3.40% / 기준금리 3.88% / 실질금리 2.60%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 4961.92로 7.84%, KOSDAQ은 633.24로 6.66% 하락했고 VIX는 28.18로 5일 평균 20.54를 크게 웃돌았습니다.
  ↳ 출처: `CORE_SIGNALS, cumulative_context`
- 외국인은 3234억원 순매도한 반면 기관은 2824억원 순매수해 충격을 흡수했지만, 20일 누적 하락률 -27.276%와 반전 신호 부재가 우세합니다.
  ↳ 출처: `flow_data, CORE_SIGNALS`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표는 일부 긍정적이나 단기 시장 위험이 우세합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고 변동성도 높아 위험회피 심리가 강합니다.
- 핵심 주장: 한국 월별 지표는 생산·소비·고용·수출이 긍정적이나, 경기·심리 혼조로 단기 급락과 괴리가 있습니다.
- 핵심 주장: 외국인 대규모 순매도와 미국 증시 급락, VIX 급등 등 대외 불확실성도 큽니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 변동성·AI 리스크로 수급 불균형 심화.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 미국발 변동성 급등, 반도체/AI 업종 패닉셀, 연준 금리 발언 등 복합 리스크(고변동성, 연준/금리, 반도체/AI) 영향이 지배적임.
- 핵심 주장: KOSPI 20일 누적 -27%로 외국인 매도는 단순 차익실현이 아닌 글로벌 리스크 회피 및 AI/반도체 비중 축소 목적이 강함.
- 핵심 주장: 개인 매수세는 KOSPI에서만 소폭 유입, KOSDAQ은 오히려 순매도 전환되어 레버리지 추격매수보다는 방어적 성격.

### 섹터 담당자
- 한줄 요약: 시장 전반에 걸친 패닉성 매도와 변동성 급등이 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 -27%로 극단적 약세가 지속되고 있습니다.
- 핵심 주장: 외국인 대규모 순매도와 변동성(VIX) 급등이 위험 회피 심리를 강화합니다.
- 핵심 주장: 중기 한국 경기지표는 혼조이나 단기 시장 충격이 우세합니다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 걸친 심각한 위험 신호가 확인됩니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일간 -27% 급락
- 핵심 주장: 변동성(VIX) 급등 및 외국인 대규모 순매도
- 핵심 주장: 미국·한국 증시 동반 급락

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 하향 압력이 지속될 가능성이 높습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 심화
- 핵심 주장: 외국인 대규모 순매도와 변동성 급등은 실적 전망 하향 압력
- 핵심 주장: 단기 반등 신호 없이 실적 추정치 추가 하락 가능성 높음

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸친 약세 확산이 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 시장 하락폭이 매우 크고, 하락이 단기간 누적되어 있다.
- 핵심 주장: 수급과 변동성, 시장 확산도 모두 약세 신호를 보인다.
- 핵심 주장: 단기 반전 신호는 아직 감지되지 않는다.

### 유동성 담당자
- 한줄 요약: 유동성 환경이 급격히 악화되어 위험회피 국면이 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 변동성 급등이 유동성 악화 신호입니다.
- 핵심 주장: 외국인 대규모 순매도와 VIX 28 돌파로 위험회피 심리가 강화되었습니다.
- 핵심 주장: 정책금리 인상 발언과 달러 강보합도 유동성에 부담을 주고 있습니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표는 일부 긍정적이나 단기 시장 위험이 우세합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3234억, vix=28.2입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct, snapshot.markets.us.nasdaq_pct, snapshot.markets.volatility.vix, snapshot.korea_macro_context
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 변동성·AI 리스크로 수급 불균형 심화.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-7.84%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.news_headlines, snapshot.macro.daily.vix, snapshot.cumulative_context.vix_5d_avg
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 걸친 패닉성 매도와 변동성 급등이 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3234억, vix=28.2입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix, snapshot.news_headlines, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 걸친 심각한 위험 신호가 확인됩니다.' 의견을 유지합니다. 근거 숫자는 vix=28.2, foreign_net=-3234억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.markets.kr.kospi_pct, snapshot.markets.us.nasdaq_pct, snapshot.markets.us.sp500_pct, snapshot.markets.volatility.vix, snapshot.flow_summary.foreign_net, snapshot.news_headlines
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 하향 압력이 지속될 가능성이 높습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3234억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.earnings_signal_score
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸친 약세 확산이 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3234억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.breadth_signal_score, snapshot.phase_two_signals.liquidity_signal_score, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 환경이 급격히 악화되어 위험회피 국면이 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 vix=28.2, foreign_net=-3234억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.markets.volatility.vix, snapshot.flow_summary.foreign_net, snapshot.news_headlines, snapshot.macro.daily.dxy, snapshot.macro.structural.fed_funds_rate
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -7.84%, USD/KRW 1340.31(-0.01%), VIX 28.2, 외국인 -3234억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 국면 분류: 다수=매크로·수급·섹터·이익·브레드스·유동성 담당자는 리스크 오프를 제시했습니다., 소수=리스크 담당자는 분류상 리스크 온을 제시했지만, 실제 주장은 심각한 위험 신호와 방어 필요성을 강조했습니다., 에이전트=[리스크 담당자]
  - 의미: 소수의 분류값과 설명이 충돌하므로 이를 강세 의견으로 해석해서는 안 되며, 실질적인 위원회 합의는 방어적 대응입니다.
- 기관 매수의 의미: 다수=외국인 순매도와 높은 변동성, 누적 하락을 근거로 기관 매수만으로 추세 반전을 판단하기 어렵다는 의견입니다., 소수=기관의 2824억원 순매수는 단기 가격 충격을 일부 완충할 수 있습니다., 에이전트=[해당 없음]
  - 의미: 기관 매수가 지속되는지보다 외국인 수급 전환과 VIX 안정이 함께 확인돼야 반등의 질을 평가할 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고 변동성도 높아 위험회피 심리가 강합니다.",
    "한국 월별 지표는 생산·소비·고용·수출이 긍정적이나, 경기·심리 혼조로 단기 급락과 괴리가 있습니다.",
    "외국인 대규모 순매도와 미국 증시 급락, VIX 급등 등 대외 불확실성도 큽니다."
  ],
  "korean_comment": "중기 지표는 일부 긍정적이나 단기 시장 위험이 우세합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.korea_macro_context"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인 대규모 순매도는 미국발 변동성 급등, 반도체/AI 업종 패닉셀, 연준 금리 발언 등 복합 리스크(고변동성, 연준/금리, 반도체/AI) 영향이 지배적임.",
    "KOSPI 20일 누적 -27%로 외국인 매도는 단순 차익실현이 아닌 글로벌 리스크 회피 및 AI/반도체 비중 축소 목적이 강함.",
    "개인 매수세는 KOSPI에서만 소폭 유입, KOSDAQ은 오히려 순매도 전환되어 레버리지 추격매수보다는 방어적 성격."
  ],
  "korean_comment": "외국인 매도 우위, 변동성·AI 리스크로 수급 불균형 심화.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.vix",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.structural.fed_funds_rate"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI 20일 누적 -27%로 극단적 약세가 지속되고 있습니다.",
    "외국인 대규모 순매도와 변동성(VIX) 급등이 위험 회피 심리를 강화합니다.",
    "중기 한국 경기지표는 혼조이나 단기 시장 충격이 우세합니다."
  ],
  "korean_comment": "시장 전반에 걸친 패닉성 매도와 변동성 급등이 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines",
    "snapshot.korea_macro_context"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK pre-analysis agent",
  "core_claims": [
    "KOSPI 20일간 -27% 급락",
    "변동성(VIX) 급등 및 외국인 대규모 순매도",
    "미국·한국 증시 동반 급락"
  ],
  "korean_comment": "시장 전반에 걸친 심각한 위험 신호가 확인됩니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 심화",
    "외국인 대규모 순매도와 변동성 급등은 실적 전망 하향 압력",
    "단기 반등 신호 없이 실적 추정치 추가 하락 가능성 높음"
  ],
  "korean_comment": "실적 추정치 하향 압력이 지속될 가능성이 높습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.earnings_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "시장 하락폭이 매우 크고, 하락이 단기간 누적되어 있다.",
    "수급과 변동성, 시장 확산도 모두 약세 신호를 보인다.",
    "단기 반전 신호는 아직 감지되지 않는다."
  ],
  "korean_comment": "시장 전반에 걸친 약세 확산이 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.markets.volatility.vix"
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
    "외국인 대규모 순매도와 VIX 28 돌파로 위험회피 심리가 강화되었습니다.",
    "정책금리 인상 발언과 달러 강보합도 유동성에 부담을 주고 있습니다."
  ],
  "korean_comment": "유동성 환경이 급격히 악화되어 위험회피 국면이 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.markets.volatility.vix",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.structural.fed_funds_rate",
    "snapshot.macro.daily.us10y"
  ],
  "confidence": "HIGH"
}
```