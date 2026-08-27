# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-08-27**
- 생성 시각(UTC): `2026-08-27T00:52:45.256927+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.
- **국면 투표**: NEUTRAL=2, RISK_ON=4, RISK_OFF=1
- **다수 국면**: RISK_ON

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 확인된 모멘텀 주도주 중심으로 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] 변동성 한도를 기준으로 포지션 규모를 조절합니다.
- [OpsGuidanceLevel.AVOID/회피] 과열된 돌파 구간 추격 매수는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +1.32% / KOSDAQ +0.51%
- **미국 지수**: S&P500 -0.02% / NASDAQ -0.08% / DOW -0.21%
- **환율/변동성**: USD/KRW 1384.61 (-0.55%) / VIX 15.2
- **시장 요약 노트**: KOSPI 1.32%, USD/KRW 1384.61. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 +915억 / 기관 +2541억 / 개인 -5395억
- **일간 매크로**: 미10년 4.66% / 미2년 3.69% / 2-10 0.97%p / DXY 99.11
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.54% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.34%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_ON.
  ↳ 출처: `regime_tuner`
- KOSPI는 6,897.82로 1.32% 상승했고 외국인 915억원, 기관 2,541억원 순매수가 지수 상승을 주도했습니다.
  ↳ 출처: `KEY_FIGURES_FOR_REPORT, korean_market_flow_breakdown, agent_opinions(flow)`
- USD/KRW는 1,384.61로 0.55% 하락하고 VIX는 15.21을 기록해 당일 위험 선호를 뒷받침했습니다.
  ↳ 출처: `macro_daily, cumulative_context, agent_opinions(liquidity)`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 급등 이후 추가 상승에는 신중함이 필요합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 코스피는 최근 20일간 강한 상승세를 보였습니다.
- 핵심 주장: 외국인과 기관의 순매수세가 뚜렷하게 나타납니다.
- 핵심 주장: 거시지표와 변동성은 안정적이지만 추가 상승에는 불확실성이 존재합니다.

### 수급 담당자
- 한줄 요약: 외국인 매수세가 KOSPI에 집중되며, 개인은 차익실현에 나선 수급 구도입니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: 외국인 순매수는 KOSPI에 집중되었으며, 고환율 완화와 반도체/AI 기대감이 주요 배경입니다.
- 핵심 주장: 개인은 대규모 차익실현에 나섰으나, 20일 누적 급등(23%↑) 이후 레버리지 추격매수보다는 이익실현 성격이 강합니다.
- 핵심 주장: 국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 변동성만 반영합니다.

### 섹터 담당자
- 한줄 요약: 시장 전반에 강한 상승 모멘텀이 유지되고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 23% 이상 상승하며 강한 상승세를 보이고 있습니다.
- 핵심 주장: 외국인과 기관의 순매수세가 지속되고 있습니다.
- 핵심 주장: 변동성(VIX)도 낮은 수준을 유지하고 있어 위험 선호 분위기가 이어집니다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 뚜렷한 위험 신호는 없습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피 20일 누적 상승세가 강함
- 핵심 주장: 외국인·기관 순매수 지속
- 핵심 주장: 변동성 지표 안정적

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 신호는 아직 미약합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 코스피 20일 누적 상승세는 견조하나, 실적 모멘텀 신호는 제한적입니다.
- 핵심 주장: 외국인·기관 순매수는 긍정적이나, 실적 추정치 상향 조정은 뚜렷하지 않습니다.

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸친 강한 상승 모멘텀이 유지되고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI의 20일 누적 상승폭이 매우 강하다.
- 핵심 주장: 시장 내부 확산도 양호하며 외국인·기관 순매수세가 뚜렷하다.

### 유동성 담당자
- 한줄 요약: 정책 및 유동성 측면에서 위험 선호가 유지되고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: 유동성 환경이 양호하며 외국인 자금 유입이 지속되고 있습니다.
- 핵심 주장: 환율과 변동성 모두 안정적이며, 정책 불확실성은 제한적입니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 급등 이후 추가 상승에는 신중함이 필요합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+1.32%, dxy=99.11입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.macro.daily.vix, snapshot.macro.daily.dxy, snapshot.macro.monthly.cpi_yoy
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매수세가 KOSPI에 집중되며, 개인은 차익실현에 나선 수급 구도입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+1.32%, usdkrw=1384.61입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.market_summary.usdkrw, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 강한 상승 모멘텀이 유지되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+915억, institution_net=+2541억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.vix_5d_avg, snapshot.market_summary.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 뚜렷한 위험 신호는 없습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+915억, institution_net=+2541억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 신호는 아직 미약합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+915억, institution_net=+2541억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.earnings_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸친 강한 상승 모멘텀이 유지되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+915억, institution_net=+2541억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 및 유동성 측면에서 위험 선호가 유지되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+915억, institution_net=+2541억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.fx.usdkrw_pct, snapshot.markets.volatility.vix, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.phase_two_signals.liquidity_signal_score
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 온입니다. 근거는 KOSPI +1.32%, USD/KRW 1384.61(-0.55%), VIX 15.2, 외국인 +915억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 모멘텀이 확인된 구간 위주로 비중을 늘리되 손절 기준은 짧게 가져갑니다.

## 7) 이견 사항
- 현재 시장 국면: 다수=수급·섹터·브레드스·유동성 담당자는 외국인·기관 순매수와 안정된 환율·변동성을 근거로 위험 선호가 유지된다고 판단했습니다., 소수=매크로 담당자는 20일 급등 이후 추가 상승에 신중했고, 리스크 담당자의 내부 국면 태그도 위험 회피로 분류됐습니다., 에이전트=[macro, risk]
  - 의미: 상승 추세 자체보다 현 수준에서 추격 매수의 손익비와 금리 이벤트 이후 변동성 확대 가능성을 결정하는 쟁점입니다.
- 상승세의 펀더멘털 지속성: 다수=섹터·브레드스 담당자는 시장 전반의 강한 상승 모멘텀이 유지된다고 평가했습니다., 소수=이익모멘텀 담당자는 실적 추정치 상향 신호가 아직 미약하다고 지적했습니다., 에이전트=[earnings]
  - 의미: 수급 중심 상승이 실적 개선으로 연결되지 않으면 높은 단기 누적 수익률이 조정 압력으로 전환될 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "코스피는 최근 20일간 강한 상승세를 보였습니다.",
    "외국인과 기관의 순매수세가 뚜렷하게 나타납니다.",
    "거시지표와 변동성은 안정적이지만 추가 상승에는 불확실성이 존재합니다."
  ],
  "korean_comment": "단기 급등 이후 추가 상승에는 신중함이 필요합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.macro.daily.vix",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.monthly.cpi_yoy"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre-analysis_KR",
  "core_claims": [
    "외국인 순매수는 KOSPI에 집중되었으며, 고환율 완화와 반도체/AI 기대감이 주요 배경입니다.",
    "개인은 대규모 차익실현에 나섰으나, 20일 누적 급등(23%↑) 이후 레버리지 추격매수보다는 이익실현 성격이 강합니다.",
    "국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 변동성만 반영합니다."
  ],
  "korean_comment": "외국인 매수세가 KOSPI에 집중되며, 개인은 차익실현에 나선 수급 구도입니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 최근 20일간 23% 이상 상승하며 강한 상승세를 보이고 있습니다.",
    "외국인과 기관의 순매수세가 지속되고 있습니다.",
    "변동성(VIX)도 낮은 수준을 유지하고 있어 위험 선호 분위기가 이어집니다."
  ],
  "korean_comment": "시장 전반에 강한 상승 모멘텀이 유지되고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.market_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "코스피 20일 누적 상승세가 강함",
    "외국인·기관 순매수 지속",
    "변동성 지표 안정적"
  ],
  "korean_comment": "시장 전반에 뚜렷한 위험 신호는 없습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.market_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "코스피 20일 누적 상승세는 견조하나, 실적 모멘텀 신호는 제한적입니다.",
    "외국인·기관 순매수는 긍정적이나, 실적 추정치 상향 조정은 뚜렷하지 않습니다."
  ],
  "korean_comment": "실적 추정치 상향 신호는 아직 미약합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI의 20일 누적 상승폭이 매우 강하다.",
    "시장 내부 확산도 양호하며 외국인·기관 순매수세가 뚜렷하다."
  ],
  "korean_comment": "시장 전반에 걸친 강한 상승 모멘텀이 유지되고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
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
    "유동성 환경이 양호하며 외국인 자금 유입이 지속되고 있습니다.",
    "환율과 변동성 모두 안정적이며, 정책 불확실성은 제한적입니다."
  ],
  "korean_comment": "정책 및 유동성 측면에서 위험 선호가 유지되고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```