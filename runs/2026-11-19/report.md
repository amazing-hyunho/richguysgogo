# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-11-19**
- 생성 시각(UTC): `2026-11-19T00:52:22.604928+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=2, RISK_ON=0, RISK_OFF=5
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +1.99% / KOSDAQ +1.96%
- **미국 지수**: S&P500 -0.23% / NASDAQ +0.42% / DOW -1.11%
- **환율/변동성**: USD/KRW 1332.22 (-0.15%) / VIX 24.6
- **시장 요약 노트**: KOSPI 1.99%, USD/KRW 1332.22. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -3902억 / 기관 +6720억 / 개인 -7384억
- **일간 매크로**: 미10년 5.07% / 미2년 4.14% / 2-10 0.92%p / DXY 103.81
- **월간 매크로**: 실업률 4.10% / CPI YoY 4.08% / Core CPI YoY 2.87% / PMI n/a
- **분기/구조**: GDP QoQ 연율 3.40% / 기준금리 3.88% / 실질금리 2.88%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 5,067.44로 1.99% 상승하고 KOSDAQ도 662.81로 1.96% 올랐으나, KOSPI 5일·20일 누적 수익률은 각각 -3.177%, -5.794%로 반등의 추세 전환 확인은 이르다.
  ↳ 출처: `market_data, cumulative_context`
- 11월 18일 수급은 기관 +6,720억원이 지수 반등을 지지했지만 외국인 -3,902억원과 개인 -7,384억원 순매도가 동반됐다. VIX 24.56은 5일 평균 22.18보다 높아 위험 선호 회복을 제한한다.
  ↳ 출처: `flow_data, macro_daily, cumulative_context`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표는 견조하나 단기 시장 흐름과 수급은 불안정합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 반등했으나 20일 누적 하락세가 뚜렷합니다.
- 핵심 주장: 한국 월별 지표는 생산·소비·고용·수출이 긍정적이나 경기·심리는 혼조입니다.
- 핵심 주장: 외국인 순매도와 높은 변동성(VIX)도 위험 신호로 해석됩니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 기관·개인 저가매수 유입이나 수급 안정성은 미흡.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 순매도는 고금리/연준 긴축(금리/연준), 고변동성(VIX), 최근 KOSPI 약세 누적(20일 -5.8%) 영향이 복합적으로 작용.
- 핵심 주장: USD/KRW 하락에도 외국인 매도 지속은 단순 환차익 목적이 아닌, 글로벌 금리/정책 리스크와 포트폴리오 리밸런싱(비중 조정) 가능성.
- 핵심 주장: 개인 매수는 지수 반등 기대감에 따른 저가매수 성격이나, 최근 누적 하락분을 감안할 때 지속성은 제한적.

### 섹터 담당자
- 한줄 요약: 단기 반등에도 누적 하락과 수급 불안이 지속되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI는 단기 반등에도 불구하고 20일 누적 하락세가 뚜렷합니다.
- 핵심 주장: 외국인 순매도와 높은 변동성(VIX)이 위험 신호로 작용합니다.
- 핵심 주장: 한국 경기지표는 생산·소비·수출 개선에도 경기·심리 혼조가 상존합니다.

### 리스크 담당자
- 한줄 요약: 단기 반등에도 누적 약세와 수급 부담이 여전합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락세 지속
- 핵심 주장: 외국인·개인 동반 순매도
- 핵심 주장: 중기 한국 경기지표 혼조

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정 상향 전환 신호는 아직 뚜렷하지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: 실적 모멘텀 신호는 부재하며, 최근 20일간 코스피 약세가 지속됨.
- 핵심 주장: 외국인 순매도와 변동성 지표(VIX) 상승으로 실적 추정 상향 전환 신호는 약함.

### 브레드스 담당자
- 한줄 요약: 지수 반등에도 확산과 수급 모두 불안정합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 단기 반등에도 20일 누적 하락세가 뚜렷함
- 핵심 주장: 수급은 외국인·개인 동반 순매도, 기관만 순매수
- 핵심 주장: 시장 변동성(VIX)과 5일 평균 변동성 모두 높음

### 유동성 담당자
- 한줄 요약: 정책 및 유동성 환경이 위험회피로 기울고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: VIX가 24 이상으로 변동성 위험이 높음
- 핵심 주장: 외국인 대규모 순매도와 최근 20일간 KOSPI 약세 지속
- 핵심 주장: 달러/원 환율은 안정적이나 유동성 개선 신호는 미약

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표는 견조하나 단기 시장 흐름과 수급은 불안정합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3902억, vix=24.6입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 기관·개인 저가매수 유입이나 수급 안정성은 미흡.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+1.99%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.macro.daily.vix, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 반등에도 누적 하락과 수급 불안이 지속되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3902억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 반등에도 누적 약세와 수급 부담이 여전합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3902억, retail_net=-7384억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.retail_net, snapshot.korea_macro_context, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정 상향 전환 신호는 아직 뚜렷하지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3902억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수 반등에도 확산과 수급 모두 불안정합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-3902억, retail_net=-7384억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.flow_summary.foreign_net, snapshot.flow_summary.retail_net, snapshot.flow_summary.institution_net, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 및 유동성 환경이 위험회피로 기울고 있습니다.' 의견을 유지합니다. 근거 숫자는 vix=24.6, foreign_net=-3902억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.markets.volatility.vix, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.phase_two_signals.liquidity_signal_score
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI +1.99%, USD/KRW 1332.22(-0.15%), VIX 24.6, 외국인 -3902억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 당일 반등의 추세 전환 여부: 다수=다수는 최근 20일 누적 하락, 외국인 순매도 및 높은 VIX를 근거로 반등을 방어적으로 해석한다., 소수=중기 실물지표의 견조함을 감안하면 단기 수급과 시장 흐름을 즉시 비관 국면으로 단정하기 어렵다는 견해다., 에이전트=[macro, risk]
  - 의미: 반등이 추세 전환인지 기술적 반발인지에 따라 위험자산 확대 시점과 손절 관리 기준이 달라진다.
- 환율 안정의 수급 해석: 다수=원/달러가 1,332.216798원으로 0.15459198222942241% 하락했는데도 외국인 순매도가 이어져, 환율만으로 외국인 수급 개선을 판단하기 어렵다., 소수=당일 원화 강세와 기관 순매수는 단기 위험선호 회복의 보조 신호로 볼 여지가 있다., 에이전트=[macro]
  - 의미: 환율 안정이 외국인 매도 완화로 연결되는지 여부가 국내 반등의 지속성을 판별할 핵심 확인 변수다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 단기 반등했으나 20일 누적 하락세가 뚜렷합니다.",
    "한국 월별 지표는 생산·소비·고용·수출이 긍정적이나 경기·심리는 혼조입니다.",
    "외국인 순매도와 높은 변동성(VIX)도 위험 신호로 해석됩니다."
  ],
  "korean_comment": "중기 지표는 견조하나 단기 시장 흐름과 수급은 불안정합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.note",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
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
    "외국인 순매도는 고금리/연준 긴축(금리/연준), 고변동성(VIX), 최근 KOSPI 약세 누적(20일 -5.8%) 영향이 복합적으로 작용.",
    "USD/KRW 하락에도 외국인 매도 지속은 단순 환차익 목적이 아닌, 글로벌 금리/정책 리스크와 포트폴리오 리밸런싱(비중 조정) 가능성.",
    "개인 매수는 지수 반등 기대감에 따른 저가매수 성격이나, 최근 누적 하락분을 감안할 때 지속성은 제한적."
  ],
  "korean_comment": "외국인 매도 우위, 기관·개인 저가매수 유입이나 수급 안정성은 미흡.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.macro.daily.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 단기 반등에도 불구하고 20일 누적 하락세가 뚜렷합니다.",
    "외국인 순매도와 높은 변동성(VIX)이 위험 신호로 작용합니다.",
    "한국 경기지표는 생산·소비·수출 개선에도 경기·심리 혼조가 상존합니다."
  ],
  "korean_comment": "단기 반등에도 누적 하락과 수급 불안이 지속되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.vix_5d_avg",
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
    "KOSPI 20일 누적 하락세 지속",
    "외국인·개인 동반 순매도",
    "중기 한국 경기지표 혼조"
  ],
  "korean_comment": "단기 반등에도 누적 약세와 수급 부담이 여전합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.retail_net",
    "snapshot.korea_macro_context",
    "snapshot.market_summary.kospi_change_pct",
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
    "실적 모멘텀 신호는 부재하며, 최근 20일간 코스피 약세가 지속됨.",
    "외국인 순매도와 변동성 지표(VIX) 상승으로 실적 추정 상향 전환 신호는 약함."
  ],
  "korean_comment": "실적 추정 상향 전환 신호는 아직 뚜렷하지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI 단기 반등에도 20일 누적 하락세가 뚜렷함",
    "수급은 외국인·개인 동반 순매도, 기관만 순매수",
    "시장 변동성(VIX)과 5일 평균 변동성 모두 높음"
  ],
  "korean_comment": "지수 반등에도 확산과 수급 모두 불안정합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.retail_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg",
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
    "VIX가 24 이상으로 변동성 위험이 높음",
    "외국인 대규모 순매도와 최근 20일간 KOSPI 약세 지속",
    "달러/원 환율은 안정적이나 유동성 개선 신호는 미약"
  ],
  "korean_comment": "정책 및 유동성 환경이 위험회피로 기울고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.markets.volatility.vix",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```