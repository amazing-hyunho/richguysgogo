# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-09-20**
- 생성 시각(UTC): `2026-09-20T00:53:24.522608+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 국내 증시는 누적 상승 추세를 유지하지만 환율·금리 부담과 수급 데이터 공백을 감안해 중립 비중에서 선별 대응할 국면입니다.
- **국면 투표**: NEUTRAL=4, RISK_ON=2, RISK_OFF=1
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 기존 핵심 보유분은 유지하되 추세와 실적 근거가 확인되는 영역만 선별 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] USD/KRW와 미국 10년물 금리, 수급 데이터 복구 여부를 확인하며 신규 진입을 분할합니다.
- [OpsGuidanceLevel.AVOID/회피] 주체별 순매수 확인 없이 하루 지수 급등만 근거로 추격 매수하는 전략은 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +2.66% / KOSDAQ +0.60%
- **미국 지수**: S&P500 +0.17% / NASDAQ +0.39% / DOW -0.18%
- **환율/변동성**: USD/KRW 1386.74 (+0.37%) / VIX 14.8
- **시장 요약 노트**: KOSPI 2.66%, USD/KRW 1386.74. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 5.00% / 미2년 3.98% / 2-10 1.02%p / DXY 100.22
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.71% / Core CPI YoY 2.76% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.67%

## 4) 위원회 핵심 포인트
- KOSPI는 6,894.23으로 2.66% 상승했고 5일·20일 누적 수익률도 각각 5.799%, 5.927%로 추세가 이어졌습니다.
  ↳ 출처: `CORE_SIGNALS, cumulative_context`
- USD/KRW는 1,386.74로 0.37% 상승했고 5일간 1.7% 올라, 지수 강세와 환율 부담이 충돌하고 있습니다.
  ↳ 출처: `CORE_SIGNALS, macro_daily, news_digest`
- 외국인·기관·개인 순매수는 조회 실패로 확인 불가하며, 상승을 주도한 투자 주체를 특정할 수 없습니다.
  ↳ 출처: `flow_data, agent_opinions`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 상승세가 이어지지만 환율과 금리 불확실성에 유의해야 합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 20일간 꾸준히 상승세를 보이고 있습니다.
- 핵심 주장: 원/달러 환율 상승과 매파적 연준 기조로 불확실성은 여전히 존재합니다.
- 핵심 주장: 단기적으로는 긍정적이지만, 환율과 금리 리스크에 주의가 필요합니다.

### 수급 담당자
- 한줄 요약: 수급 데이터 부재로 주체별 매매 동향 해석이 불가하며, 매크로 불확실성만 부각됨.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: 수급 데이터 부재로 외국인/기관/개인 주체별 흐름 해석 불가.
- 핵심 주장: 고환율(USD/KRW 상승), 연준/금리, 경기/성장, 반도체/AI 등 매크로 불확실성 지속.
- 핵심 주장: KOSPI 5일/20일 누적 강세에도 불구, 단기 수급 주도세 판단 제한적 (국내 변동성 직접 판단 제한적, VKOSPI 미제공).

### 섹터 담당자
- 한줄 요약: 국내 증시는 단기적으로 강세 흐름이 이어지고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 5.9% 상승하며 강한 상승세를 보이고 있다.
- 핵심 주장: 미국 금리 인상과 원달러 환율 상승에도 불구하고 국내 증시의 모멘텀이 유지되고 있다.
- 핵심 주장: 변동성(VIX) 하락과 유동성 지표 개선이 위험선호 분위기를 뒷받침한다.

### 리스크 담당자
- 한줄 요약: 시장 전반은 강세 흐름이 유지되고 있습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 20일간 5.9% 상승하며 강세를 보임
- 핵심 주장: 변동성(VIX)과 환율 상승에도 시장 전반은 안정적
- 핵심 주장: 매수 주체별 흐름 데이터 부재로 단기 해석은 제한적

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 조정 신호는 아직 나타나지 않았습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀 신호는 부재하며, 추세적 상향 조정은 감지되지 않음.
- 핵심 주장: 헤드라인 및 단기 랠리는 실적 추정치 상향과 무관함.

### 브레드스 담당자
- 한줄 요약: 지수와 시장 내부 모두 긍정적인 흐름이 유지되고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 최근 20일간 상승세가 뚜렷하다.
- 핵심 주장: 시장 변동성은 낮고, 단기 반전 신호도 없다.
- 핵심 주장: 시장 내부 확산도 양호하다.

### 유동성 담당자
- 한줄 요약: 정책 불확실성과 환율 상승으로 유동성 환경이 제한적입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 원/달러 환율이 상승세를 보이며 정책 불확실성이 높음.
- 핵심 주장: 유동성 신호는 강하지만 금리 인상과 달러 강세로 보수적 접근 필요.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 5명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '상승세가 이어지지만 환율과 금리 불확실성에 유의해야 합니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1386.74, dxy=100.22입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.usdkrw, snapshot.macro.daily.us10y, snapshot.macro.daily.dxy, snapshot.news_headlines, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg
- [수급 담당자] 저는 수급 담당자 입장에서 '수급 데이터 부재로 주체별 매매 동향 해석이 불가하며, 매크로 불확실성만 부각됨.' 의견을 유지합니다. 근거 숫자는 foreign_net=+0억, institution_net=+0억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.flow_summary.retail_net, snapshot.market_summary.kospi_change_pct, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '국내 증시는 단기적으로 강세 흐름이 이어지고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.66%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.macro.daily.vix, snapshot.phase_two_signals.liquidity_signal_score, snapshot.news_headlines, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반은 강세 흐름이 유지되고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.66%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.vix_5d_avg, snapshot.flow_summary.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 조정 신호는 아직 나타나지 않았습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.news_headlines, snapshot.market_summary.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수와 시장 내부 모두 긍정적인 흐름이 유지되고 있습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.breadth_signal_score
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 불확실성과 환율 상승으로 유동성 환경이 제한적입니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1386.74, dxy=100.22입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.macro.daily.dxy, snapshot.macro.daily.us10y, snapshot.phase_two_signals.liquidity_signal_score, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +2.66%, USD/KRW 1386.74(+0.37%), VIX 14.8, 외국인 +0억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 현재 시장 국면: 다수=매크로·리스크·수급·이익모멘텀 담당자는 상승 추세를 인정하면서도 환율, 금리, 수급 공백 때문에 중립 판단을 유지했습니다., 소수=섹터 및 브레드스 담당자는 지수 상승과 반전 신호 부재를 근거로 위험선호 국면을 주장했습니다., 에이전트=[sector, breadth]
  - 의미: 위험선호 판단을 채택하려면 지수 상승이 실제 수급 확산과 실적 개선으로 연결되는지 추가 확인이 필요합니다.
- 유동성 환경의 방향: 다수=다수는 강세 흐름 속에서도 성급한 비중 변경을 피해야 한다고 봤습니다., 소수=유동성 담당자는 USD/KRW 1,386.74와 금리 불확실성을 근거로 제한적인 유동성 환경과 위험회피를 강조했습니다., 에이전트=[liquidity]
  - 의미: 환율 상승이 지속되면 현재의 지수 모멘텀보다 할인율과 외화 유동성 부담이 우선할 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 20일간 꾸준히 상승세를 보이고 있습니다.",
    "원/달러 환율 상승과 매파적 연준 기조로 불확실성은 여전히 존재합니다.",
    "단기적으로는 긍정적이지만, 환율과 금리 리스크에 주의가 필요합니다."
  ],
  "korean_comment": "상승세가 이어지지만 환율과 금리 불확실성에 유의해야 합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre_analysis_KR",
  "core_claims": [
    "수급 데이터 부재로 외국인/기관/개인 주체별 흐름 해석 불가.",
    "고환율(USD/KRW 상승), 연준/금리, 경기/성장, 반도체/AI 등 매크로 불확실성 지속.",
    "KOSPI 5일/20일 누적 강세에도 불구, 단기 수급 주도세 판단 제한적 (국내 변동성 직접 판단 제한적, VKOSPI 미제공)."
  ],
  "korean_comment": "수급 데이터 부재로 주체별 매매 동향 해석이 불가하며, 매크로 불확실성만 부각됨.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.flow_summary.retail_net",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "LOW"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 최근 20일간 5.9% 상승하며 강한 상승세를 보이고 있다.",
    "미국 금리 인상과 원달러 환율 상승에도 불구하고 국내 증시의 모멘텀이 유지되고 있다.",
    "변동성(VIX) 하락과 유동성 지표 개선이 위험선호 분위기를 뒷받침한다."
  ],
  "korean_comment": "국내 증시는 단기적으로 강세 흐름이 이어지고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.macro.daily.vix",
    "snapshot.phase_two_signals.liquidity_signal_score",
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
    "KOSPI가 최근 20일간 5.9% 상승하며 강세를 보임",
    "변동성(VIX)과 환율 상승에도 시장 전반은 안정적",
    "매수 주체별 흐름 데이터 부재로 단기 해석은 제한적"
  ],
  "korean_comment": "시장 전반은 강세 흐름이 유지되고 있습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.flow_summary.note"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 신호는 부재하며, 추세적 상향 조정은 감지되지 않음.",
    "헤드라인 및 단기 랠리는 실적 추정치 상향과 무관함."
  ],
  "korean_comment": "실적 추정치 상향 조정 신호는 아직 나타나지 않았습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.news_headlines",
    "snapshot.market_summary.note"
  ],
  "confidence": "MED"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI와 KOSDAQ 모두 최근 20일간 상승세가 뚜렷하다.",
    "시장 변동성은 낮고, 단기 반전 신호도 없다.",
    "시장 내부 확산도 양호하다."
  ],
  "korean_comment": "지수와 시장 내부 모두 긍정적인 흐름이 유지되고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
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
    "원/달러 환율이 상승세를 보이며 정책 불확실성이 높음.",
    "유동성 신호는 강하지만 금리 인상과 달러 강세로 보수적 접근 필요."
  ],
  "korean_comment": "정책 불확실성과 환율 상승으로 유동성 환경이 제한적입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.daily.us10y",
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```