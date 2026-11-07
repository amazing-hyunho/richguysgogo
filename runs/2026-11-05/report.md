# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-11-05**
- 생성 시각(UTC): `2026-11-05T00:52:17.931848+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.10% / KOSDAQ -2.50%
- **미국 지수**: S&P500 +1.58% / NASDAQ +1.44% / DOW +3.03%
- **환율/변동성**: USD/KRW 1343.93 (-0.13%) / VIX 16.6
- **시장 요약 노트**: KOSPI -3.10%, USD/KRW 1343.93. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -8092억 / 기관 +1911억 / 개인 +5908억
- **일간 매크로**: 미10년 4.89% / 미2년 4.03% / 2-10 0.87%p / DXY 101.47
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 3.40% / 기준금리 3.88% / 실질금리 2.63%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 5,507.76(-3.10%), KOSDAQ은 696.88(-2.50%)이며 외국인은 8,092억원 순매도해 단기 수급 불균형이 심화됐다.
  ↳ 출처: `market_data, flow_data`
- KOSPI 5일·20일 누적 수익률은 각각 -7.315%, -19.876%이고 반전 신호도 없어 하루 낙폭만으로 기술적 바닥을 단정하기 어렵다.
  ↳ 출처: `cumulative_context, market_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표는 일부 긍정적이나, 단기 시장 흐름과 수급은 위험 회피가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 약 -20% 급락하며 시장 전반에 뚜렷한 하락 압력이 지속되고 있습니다.
- 핵심 주장: 한국 월별 지표(2026년 9~10월)는 생산·소비·고용·수출이 긍정적이나, 경기·심리 혼조로 중기 개선 신호가 확실하지 않습니다.
- 핵심 주장: 외국인 대규모 순매도와 높은 변동성(5일 평균 VIX 18.94)도 단기 반등 신호 없이 위험 회피 심리를 강화합니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저가매수 유입이나 수급 불균형 지속.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 최근 20일간 누적 하락(-19.9%)과 반도체/AI 불확실성, 정책 리스크(관세) 등 복합 요인에 따른 포트폴리오 리밸런싱 성격이 강함.
- 핵심 주장: USD/KRW는 소폭 하락(-0.13%)해 환율 급등에 따른 강제 매도 압력은 제한적, 외국인 매도는 환차손 회피보다는 한국/반도체 비중 조정이 주된 배경.
- 핵심 주장: 개인 대규모 순매수는 단기 낙폭 과대 구간에서 저가 매수 시도로 보이나, 5일/20일 누적 하락폭이 매우 커 레버리지 추격매수 위험도 내포.

### 섹터 담당자
- 한줄 요약: 단기 약세 추세와 수급 악화가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고 단기 반전 신호는 없습니다.
- 핵심 주장: 외국인 대규모 순매도와 시장 변동성 확대가 지속되고 있습니다.
- 핵심 주장: 중기 한국 경기지표는 생산·소비·수출 개선에도 심리·선행지수 혼조로 방향성 제한적입니다.

### 리스크 담당자
- 한줄 요약: 단기 급락과 외국인 매도세가 위험 신호를 강화합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일간 -19%대 급락
- 핵심 주장: 외국인 대규모 순매도 지속
- 핵심 주장: 중기적 위험 신호 누적

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 하락 압력이 당분간 이어질 전망입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 지속
- 핵심 주장: 외국인 대규모 순매도, 실적 추정치 하향 압력 강화
- 핵심 주장: 단기 반등 신호 없이 실적 추정치 하락 추세 지속 가능성

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸친 약세 확산이 지속되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 20일 누적 하락폭이 매우 크다.
- 핵심 주장: 수급과 시장 내 확산도 모두 약세 신호가 뚜렷하다.
- 핵심 주장: 단기 반전 신호는 아직 감지되지 않는다.

### 유동성 담당자
- 한줄 요약: 유동성 악화와 외국인 이탈로 위험회피 국면이 강화되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 외국인 대규모 순매도 지속.
- 핵심 주장: 환율은 안정적이나 변동성 평균은 여전히 높음.
- 핵심 주장: 정책·유동성 환경이 위험회피로 기울어 있음.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표는 일부 긍정적이나, 단기 시장 흐름과 수급은 위험 회피가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8092억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저가매수 유입이나 수급 불균형 지속.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.10%, usdkrw=1343.93입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.macro.daily.dxy
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 약세 추세와 수급 악화가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8092억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 급락과 외국인 매도세가 위험 신호를 강화합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8092억, kospi_change_pct=-3.10%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.market_summary.kospi_change_pct
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 하락 압력이 당분간 이어질 전망입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8092억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.earnings_signal_score
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸친 약세 확산이 지속되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8092억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.vix_5d_avg
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 악화와 외국인 이탈로 위험회피 국면이 강화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8092억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.usdkrw_5d_change_pct
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.10%, USD/KRW 1343.93(-0.13%), VIX 16.6, 외국인 -8092억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 국내 증시 위험 국면 판단: 다수=매크로·수급·섹터 등 6개 담당자는 외국인 매도와 누적 급락을 근거로 리스크 오프를 제시했다., 소수=리스크 담당자의 내부 태그는 RISK_ON이지만 실제 주장은 급락과 외국인 매도가 위험 신호를 강화한다는 내용이어서 태그와 서술이 충돌한다., 에이전트=[risk]
  - 의미: 소수 태그를 공격적 투자 신호로 해석하기보다 실제 근거와 시장 수치를 우선해야 한다.
- 대외시장과 국내 수급의 방향 차이: 다수=국내 핵심 신호는 KOSPI 급락과 외국인 8,092억원 순매도로 약세다., 소수=미국 3대 지수는 상승했고 VIX 16.61은 5일 평균 18.942보다 낮아 대외 위험선호 회복 가능성을 시사한다., 에이전트=[flow, liquidity]
  - 의미: 미국 강세가 국내 외국인 수급 개선으로 연결되는지 확인되기 전까지 핵심 약세 판단의 신뢰도만 소폭 낮추는 반대 근거다.
- 월간 실물경제와 일간 시장의 괴리: 다수=당일 가격·수급은 위험 회피를 가리킨다., 소수=9월 생산·소비·설비투자와 수출금액지수는 개선 신호를 보였다., 에이전트=[macro, sector]
  - 의미: 월간 지표는 중기 배경일 뿐 오늘의 하락 원인이나 즉각적인 매수 신호로 동일시할 수 없다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 최근 20일간 약 -20% 급락하며 시장 전반에 뚜렷한 하락 압력이 지속되고 있습니다.",
    "한국 월별 지표(2026년 9~10월)는 생산·소비·고용·수출이 긍정적이나, 경기·심리 혼조로 중기 개선 신호가 확실하지 않습니다.",
    "외국인 대규모 순매도와 높은 변동성(5일 평균 VIX 18.94)도 단기 반등 신호 없이 위험 회피 심리를 강화합니다."
  ],
  "korean_comment": "중기 지표는 일부 긍정적이나, 단기 시장 흐름과 수급은 위험 회피가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인 대규모 순매도는 최근 20일간 누적 하락(-19.9%)과 반도체/AI 불확실성, 정책 리스크(관세) 등 복합 요인에 따른 포트폴리오 리밸런싱 성격이 강함.",
    "USD/KRW는 소폭 하락(-0.13%)해 환율 급등에 따른 강제 매도 압력은 제한적, 외국인 매도는 환차손 회피보다는 한국/반도체 비중 조정이 주된 배경.",
    "개인 대규모 순매수는 단기 낙폭 과대 구간에서 저가 매수 시도로 보이나, 5일/20일 누적 하락폭이 매우 커 레버리지 추격매수 위험도 내포."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저가매수 유입이나 수급 불균형 지속.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.daily.us10y",
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
    "KOSPI 20일 누적 하락폭이 매우 크고 단기 반전 신호는 없습니다.",
    "외국인 대규모 순매도와 시장 변동성 확대가 지속되고 있습니다.",
    "중기 한국 경기지표는 생산·소비·수출 개선에도 심리·선행지수 혼조로 방향성 제한적입니다."
  ],
  "korean_comment": "단기 약세 추세와 수급 악화가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
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
    "KOSPI 20일간 -19%대 급락",
    "외국인 대규모 순매도 지속",
    "중기적 위험 신호 누적"
  ],
  "korean_comment": "단기 급락과 외국인 매도세가 위험 신호를 강화합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
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
    "KOSPI 20일 누적 급락으로 실적 모멘텀 약화 우려 지속",
    "외국인 대규모 순매도, 실적 추정치 하향 압력 강화",
    "단기 반등 신호 없이 실적 추정치 하락 추세 지속 가능성"
  ],
  "korean_comment": "실적 추정치 하락 압력이 당분간 이어질 전망입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
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
    "KOSPI와 KOSDAQ 모두 20일 누적 하락폭이 매우 크다.",
    "수급과 시장 내 확산도 모두 약세 신호가 뚜렷하다.",
    "단기 반전 신호는 아직 감지되지 않는다."
  ],
  "korean_comment": "시장 전반에 걸친 약세 확산이 지속되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 20일 누적 급락과 외국인 대규모 순매도 지속.",
    "환율은 안정적이나 변동성 평균은 여전히 높음.",
    "정책·유동성 환경이 위험회피로 기울어 있음."
  ],
  "korean_comment": "유동성 악화와 외국인 이탈로 위험회피 국면이 강화되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.usdkrw_5d_change_pct"
  ],
  "confidence": "HIGH"
}
```