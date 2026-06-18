# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-06-18**
- 생성 시각(UTC): `2026-06-18T02:56:49.208238+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.
- **국면 투표**: NEUTRAL=6, RISK_ON=0, RISK_OFF=1
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 확인된 모멘텀 주도주 중심으로 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] 변동성 한도를 기준으로 포지션 규모를 조절합니다.
- [OpsGuidanceLevel.AVOID/회피] 과열된 돌파 구간 추격 매수는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +0.78% / KOSDAQ -2.92%
- **미국 지수**: S&P500 -1.21% / NASDAQ -1.34% / DOW -0.98%
- **환율/변동성**: USD/KRW 1518.88 (-0.25%) / VIX 18.4
- **시장 요약 노트**: KOSPI 0.78%, USD/KRW 1518.88. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -11784억 / 기관 -2230억 / 개인 +14263억
- **일간 매크로**: 미10년 4.46% / 미2년 3.65% / 2-10 0.82%p / DXY 100.25
- **월간 매크로**: 실업률 4.30% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.60% / 기준금리 3.63% / 실질금리 2.20%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_ON.
  ↳ 출처: `regime_tuner`
- KOSPI는 오늘 0.78% 상승(8,937.56p)하며 20일 누적 +15.35%의 강한 랠리를 이어갔으나, 외국인 -11,784억 순매도와 KOSDAQ -2.92% 급락이 동반되었습니다.
  ↳ 출처: `CORE_SIGNALS, flow_data, macro_daily`
- 미국 연준의 추가 금리 인상 시사와 고환율(USD/KRW 1,518.88) 영향으로 외국인 자금 유출이 확대되었으며, 개인이 대규모 매수(+14,263억)로 이를 흡수했습니다.
  ↳ 출처: `CORE_SIGNALS, news, flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 급등 이후 조정 및 변동성 확대에 유의해야 합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 강한 상승세를 보였습니다.
- 핵심 주장: 미국 금리 인상 우려와 외국인 순매도는 부담 요인입니다.
- 핵심 주장: 변동성 확대와 불확실성으로 신중한 접근이 필요합니다.

### 수급 담당자
- 한줄 요약: 외국인 차익실현 매물 출회, 개인이 단기 추격매수로 흡수하는 구도입니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: 외국인 매도는 최근 KOSPI 20일간 15% 이상 급등에 따른 차익실현(이익실현) 성격이 강함.
- 핵심 주장: 고환율(USD/KRW 1518) 및 연준 금리인상 시사(금리/연준)로 외국인 추가 유입 동력 약화, 단기 포트폴리오 리밸런싱도 일부 반영.
- 핵심 주장: 개인 매수세는 최근 급등장 이후 레버리지 추격매수 성격이 짙어 지속성에 의문, 단기 변동성 확대 우려.

### 섹터 담당자
- 한줄 요약: 강한 상승세가 지속되고 있으나 단기 변동성에 유의해야 합니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 15% 이상 상승하며 강한 모멘텀을 보이고 있습니다.
- 핵심 주장: 외국인과 기관의 순매도에도 불구하고 개인 매수세가 시장을 지지하고 있습니다.
- 핵심 주장: 미국 금리 인상 우려와 환율 변동성 확대가 단기 리스크 요인입니다.

### 리스크 담당자
- 한줄 요약: 누적 상승세와 변동성 수준을 고려할 때 위험 신호는 아직 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 15% 이상 상승세를 보임
- 핵심 주장: 외국인 자금 유출이 크지만 시장은 견조함
- 핵심 주장: 단기 변동성은 있으나 추세적 위험 신호는 없음

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정 상향 모멘텀은 아직 확인되지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI의 최근 20일 누적 상승은 견조하나, 실적 모멘텀 신호는 부재함.
- 핵심 주장: 외국인 순매도와 실적 관련 뉴스 부재로 이익 추정 상향 동력 약함.

### 브레드스 담당자
- 한줄 요약: 지수는 강하지만 내부 확산은 둔화되고 있습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 강한 누적 상승세를 보임.
- 핵심 주장: 단기적으로 외국인 매도와 KOSDAQ 약세로 확산력은 제한적.
- 핵심 주장: 시장 내부 확산(breadth)은 다소 약화 조짐.

### 유동성 담당자
- 한줄 요약: 정책 불확실성과 외국인 자금 이탈로 유동성 환경이 악화되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 연준의 추가 금리 인상 시사로 정책 불확실성 확대.
- 핵심 주장: 외국인 대규모 순매도와 변동성(VIX) 상승으로 유동성 위축 신호.
- 핵심 주장: KOSPI 단기 급등에도 환율과 정책 리스크로 보수적 접근 필요.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 급등 이후 조정 및 변동성 확대에 유의해야 합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-11784억, vix=18.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.news_headlines, snapshot.markets.us.sp500_pct, snapshot.markets.us.nasdaq_pct, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 차익실현 매물 출회, 개인이 단기 추격매수로 흡수하는 구도입니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1518.88입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.macro.daily.vix
- [섹터 담당자] 저는 섹터 담당자 입장에서 '강한 상승세가 지속되고 있으나 단기 변동성에 유의해야 합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '누적 상승세와 변동성 수준을 고려할 때 위험 신호는 아직 뚜렷하지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-11784억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정 상향 모멘텀은 아직 확인되지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-11784억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.earnings_signal_score, snapshot.flow_summary.foreign_net, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수는 강하지만 내부 확산은 둔화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-11784억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kosdaq_pct, snapshot.phase_two_signals.breadth_signal_score
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 불확실성과 외국인 자금 이탈로 유동성 환경이 악화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-11784억, vix=18.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.news_headlines, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.note
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +0.78%, USD/KRW 1518.88(-0.25%), VIX 18.4, 외국인 -11784억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 유동성 환경 해석: 다수=외국인 매도와 변동성 확대에도 시장은 견조하며, 단기 조정 가능성에 대비한 중립적 대응이 적절하다는 의견, 소수=정책 불확실성과 외국인 자금 이탈로 유동성 환경이 악화되어 보수적 접근이 필요하다는 의견, 에이전트=[liquidity]
  - 의미: 유동성 해석에 따라 단기 리스크 관리 및 신규 투자 타이밍 전략이 달라질 수 있음
- 시장 Breadth(확산력): 다수=지수는 강하지만 내부 확산은 둔화되고 있어 단기 변동성 확대에 유의해야 한다는 의견, 소수=아직 추세적 위험 신호는 뚜렷하지 않다는 의견, 에이전트=[risk]
  - 의미: 지수 상승이 소수 종목에 집중될 경우, 조정 시 낙폭이 커질 수 있음

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 최근 20일간 강한 상승세를 보였습니다.",
    "미국 금리 인상 우려와 외국인 순매도는 부담 요인입니다.",
    "변동성 확대와 불확실성으로 신중한 접근이 필요합니다."
  ],
  "korean_comment": "단기 급등 이후 조정 및 변동성 확대에 유의해야 합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.volatility.vix",
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
    "외국인 매도는 최근 KOSPI 20일간 15% 이상 급등에 따른 차익실현(이익실현) 성격이 강함.",
    "고환율(USD/KRW 1518) 및 연준 금리인상 시사(금리/연준)로 외국인 추가 유입 동력 약화, 단기 포트폴리오 리밸런싱도 일부 반영.",
    "개인 매수세는 최근 급등장 이후 레버리지 추격매수 성격이 짙어 지속성에 의문, 단기 변동성 확대 우려."
  ],
  "korean_comment": "외국인 차익실현 매물 출회, 개인이 단기 추격매수로 흡수하는 구도입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.vix",
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
    "KOSPI는 최근 20일간 15% 이상 상승하며 강한 모멘텀을 보이고 있습니다.",
    "외국인과 기관의 순매도에도 불구하고 개인 매수세가 시장을 지지하고 있습니다.",
    "미국 금리 인상 우려와 환율 변동성 확대가 단기 리스크 요인입니다."
  ],
  "korean_comment": "강한 상승세가 지속되고 있으나 단기 변동성에 유의해야 합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
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
    "KOSPI는 최근 20일간 15% 이상 상승세를 보임",
    "외국인 자금 유출이 크지만 시장은 견조함",
    "단기 변동성은 있으나 추세적 위험 신호는 없음"
  ],
  "korean_comment": "누적 상승세와 변동성 수준을 고려할 때 위험 신호는 아직 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
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
    "KOSPI의 최근 20일 누적 상승은 견조하나, 실적 모멘텀 신호는 부재함.",
    "외국인 순매도와 실적 관련 뉴스 부재로 이익 추정 상향 동력 약함."
  ],
  "korean_comment": "실적 추정 상향 모멘텀은 아직 확인되지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines"
  ],
  "confidence": "MED"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI는 최근 20일간 강한 누적 상승세를 보임.",
    "단기적으로 외국인 매도와 KOSDAQ 약세로 확산력은 제한적.",
    "시장 내부 확산(breadth)은 다소 약화 조짐."
  ],
  "korean_comment": "지수는 강하지만 내부 확산은 둔화되고 있습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
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
    "연준의 추가 금리 인상 시사로 정책 불확실성 확대.",
    "외국인 대규모 순매도와 변동성(VIX) 상승으로 유동성 위축 신호.",
    "KOSPI 단기 급등에도 환율과 정책 리스크로 보수적 접근 필요."
  ],
  "korean_comment": "정책 불확실성과 외국인 자금 이탈로 유동성 환경이 악화되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.news_headlines",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```