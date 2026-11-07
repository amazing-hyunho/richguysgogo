# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-11-03**
- 생성 시각(UTC): `2026-11-03T00:52:21.341576+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.55% / KOSDAQ -3.39%
- **미국 지수**: S&P500 -0.51% / NASDAQ -1.07% / DOW +0.41%
- **환율/변동성**: USD/KRW 1332.76 (-0.23%) / VIX 21.1
- **시장 요약 노트**: KOSPI -3.55%, USD/KRW 1332.76. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -5758억 / 기관 -4519억 / 개인 +9945억
- **일간 매크로**: 미10년 4.89% / 미2년 3.98% / 2-10 0.91%p / DXY 101.73
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 3.40% / 기준금리 3.88% / 실질금리 2.60%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 5,651.31로 3.55%, KOSDAQ은 709.48로 3.39% 하락했고 외국인 -5,758억원, 기관 -4,519억원의 동반 매도가 지수 급락을 주도했다.
  ↳ 출처: `flow_data, market_data`
- KOSPI 20일 누적 수익률은 -21.953%이고 반전 신호는 없으며, VIX 21.15는 5일 평균 18.848을 웃돌아 위험회피가 이어지고 있다.
  ↳ 출처: `cumulative_context, macro_daily`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표는 일부 긍정적이나, 단기 시장 흐름은 위험회피가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고, 단기 반전 신호는 확인되지 않습니다.
- 핵심 주장: 한국 월별 지표는 생산·소비·수출·고용이 긍정적이나, 경기·심리 혼조로 중기 개선 확신은 어렵습니다.
- 핵심 주장: 외국인·기관 대규모 순매도와 변동성(VIX) 상승이 위험회피 심리를 반영합니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저점 추격매수로 수급 불균형 심화 국면.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 반도체/AI 기대 약화와 고금리/연준 불확실성(금리/연준) 영향이 복합적으로 작용.
- 핵심 주장: USD/KRW 하락에도 외국인 매도 지속은 단순 환차익 목적이 아닌, 글로벌 위험회피(RISK_OFF) 및 KOSPI 20일 누적 급락(-21.95%)에 따른 포트폴리오 리밸런싱 가능성.
- 핵심 주장: 개인 대규모 순매수는 저점 인식에 따른 레버리지 추격매수 성격이 강하며, 단기적으로 지속 가능성은 낮음.

### 섹터 담당자
- 한줄 요약: 시장 전반에 위험 회피 분위기가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고 단기 반등 신호는 없습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도, 변동성(VIX) 상승이 위험 회피 심리를 강화합니다.
- 핵심 주장: 한국 중기 경제지표는 생산·소비·수출 개선에도 불구하고 경기·심리 혼조가 지속됩니다.

### 리스크 담당자
- 한줄 요약: 단기 급락과 수급 악화가 뚜렷하게 나타납니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큼
- 핵심 주장: 외국인·기관 대규모 순매도 지속
- 핵심 주장: 중기 한국 경기지표는 혼조이나 생산·소비는 긍정

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀 약화가 단기 반등 없이 이어지고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 지속
- 핵심 주장: 외국인·기관 동반 순매도, 실적 전망 하향 압력 강화
- 핵심 주장: 단기 반등 신호 없이 실적 추세 개선 근거 부족

### 브레드스 담당자
- 한줄 요약: 시장 전반의 하락세와 확산 약화가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고, 단기 반등 신호는 없다.
- 핵심 주장: 수급과 시장 내 확산도 모두 약화된 상태가 지속되고 있다.

### 유동성 담당자
- 한줄 요약: 정책 민감 유동성 환경이 악화되어 위험회피 국면이 지속됩니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 외국인 대규모 순매도 지속
- 핵심 주장: VIX 21 상회, 변동성 확대와 위험회피 심화
- 핵심 주장: 달러/원 환율은 소폭 하락이나 유동성 개선 신호 미약

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표는 일부 긍정적이나, 단기 시장 흐름은 위험회피가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-5758억, institution_net=-4519억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.volatility.vix
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저점 추격매수로 수급 불균형 심화 국면.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.55%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.kr.kospi_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.macro.daily.vix
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 위험 회피 분위기가 강하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-5758억, institution_net=-4519억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.volatility.vix, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 급락과 수급 악화가 뚜렷하게 나타납니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-5758억, institution_net=-4519억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.korea_macro_context, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀 약화가 단기 반등 없이 이어지고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-5758억, institution_net=-4519억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.reversal_signal
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 하락세와 확산 약화가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-5758억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 민감 유동성 환경이 악화되어 위험회피 국면이 지속됩니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-5758억, vix=21.1입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.market_summary.usdkrw
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.55%, USD/KRW 1332.76(-0.23%), VIX 21.1, 외국인 -5758억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 국면 판단: 다수=매크로·수급·섹터·이익·브레드스·유동성 담당자는 외국인 매도, VIX 상승, 반전 신호 부재를 근거로 리스크 오프를 판단했다., 소수=리스크 담당자의 내부 태그는 RISK_ON이지만 실제 논평은 급락과 수급 악화를 강조해 내용상 다수 의견과 가깝다., 에이전트=[risk]
  - 의미: 태그와 논거의 불일치로 확신도를 중간 수준으로 낮추되, 핵심 수급 데이터가 바뀌기 전까지 방어적 결론은 유지해야 한다.
- 중기 펀더멘털과 당일 가격 신호: 다수=당일 급락과 외국인·기관 매도는 단기 위험회피를 가리킨다., 소수=9월 생산·소비·설비투자·수출 및 고용 지표는 중기 경기의 일부 개선 가능성을 보여준다., 에이전트=[macro, sector]
  - 의미: 월간 지표를 당일 반등 신호로 오인해서는 안 되지만, 변동성 완화 시 낙폭 회복의 펀더멘털 기반이 될 수 있다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고, 단기 반전 신호는 확인되지 않습니다.",
    "한국 월별 지표는 생산·소비·수출·고용이 긍정적이나, 경기·심리 혼조로 중기 개선 확신은 어렵습니다.",
    "외국인·기관 대규모 순매도와 변동성(VIX) 상승이 위험회피 심리를 반영합니다."
  ],
  "korean_comment": "중기 지표는 일부 긍정적이나, 단기 시장 흐름은 위험회피가 뚜렷합니다.",
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
  "agent_name": "FLOW_pre-analysis_KR",
  "core_claims": [
    "외국인 대규모 순매도는 반도체/AI 기대 약화와 고금리/연준 불확실성(금리/연준) 영향이 복합적으로 작용.",
    "USD/KRW 하락에도 외국인 매도 지속은 단순 환차익 목적이 아닌, 글로벌 위험회피(RISK_OFF) 및 KOSPI 20일 누적 급락(-21.95%)에 따른 포트폴리오 리밸런싱 가능성.",
    "개인 대규모 순매수는 저점 인식에 따른 레버리지 추격매수 성격이 강하며, 단기적으로 지속 가능성은 낮음."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저점 추격매수로 수급 불균형 심화 국면.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.vix_5d_avg"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고 단기 반등 신호는 없습니다.",
    "외국인과 기관의 대규모 순매도, 변동성(VIX) 상승이 위험 회피 심리를 강화합니다.",
    "한국 중기 경제지표는 생산·소비·수출 개선에도 불구하고 경기·심리 혼조가 지속됩니다."
  ],
  "korean_comment": "시장 전반에 위험 회피 분위기가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.markets.volatility.vix",
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
    "KOSPI 20일 누적 하락폭이 매우 큼",
    "외국인·기관 대규모 순매도 지속",
    "중기 한국 경기지표는 혼조이나 생산·소비는 긍정"
  ],
  "korean_comment": "단기 급락과 수급 악화가 뚜렷하게 나타납니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.korea_macro_context",
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
    "KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 지속",
    "외국인·기관 동반 순매도, 실적 전망 하향 압력 강화",
    "단기 반등 신호 없이 실적 추세 개선 근거 부족"
  ],
  "korean_comment": "실적 모멘텀 약화가 단기 반등 없이 이어지고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.reversal_signal"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 크고, 단기 반등 신호는 없다.",
    "수급과 시장 내 확산도 모두 약화된 상태가 지속되고 있다."
  ],
  "korean_comment": "시장 전반의 하락세와 확산 약화가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
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
    "KOSPI 20일 누적 급락과 외국인 대규모 순매도 지속",
    "VIX 21 상회, 변동성 확대와 위험회피 심화",
    "달러/원 환율은 소폭 하락이나 유동성 개선 신호 미약"
  ],
  "korean_comment": "정책 민감 유동성 환경이 악화되어 위험회피 국면이 지속됩니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.market_summary.usdkrw"
  ],
  "confidence": "HIGH"
}
```