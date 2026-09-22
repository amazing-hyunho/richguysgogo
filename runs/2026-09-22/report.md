# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-09-22**
- 생성 시각(UTC): `2026-09-22T00:53:45.126145+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 국내외 주가 모멘텀과 낮은 변동성은 위험선호를 지지하지만, 단기 급등과 수급 공백·금리·유가 부담을 고려해 중립에 가까운 선별적 위험선호가 적절합니다.
- **국면 투표**: NEUTRAL=4, RISK_ON=2, RISK_OFF=1
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] AI·반도체 등 강한 주도 테마는 분할 접근하되 가격과 후속 실적 신호를 함께 확인합니다.
- [OpsGuidanceLevel.CAUTION/주의] KOSPI 5일 누적 7.573% 급등 이후이므로 지수 추격보다 환율·VIX·수급 복원을 기다립니다.
- [OpsGuidanceLevel.AVOID/회피] 결측인 주체별 순매수 0억 표기를 실제 매매 신호로 간주하거나 레버리지를 확대하지 않습니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +1.93% / KOSDAQ +0.76%
- **미국 지수**: S&P500 +1.49% / NASDAQ +2.26% / DOW +0.71%
- **환율/변동성**: USD/KRW 1375.64 (-1.06%) / VIX 14.9
- **시장 요약 노트**: KOSPI 1.93%, USD/KRW 1375.64. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 4.96% / 미2년 3.98% / 2-10 0.98%p / DXY 100.38
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.71% / Core CPI YoY 2.76% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.62%

## 4) 위원회 핵심 포인트
- KOSPI는 7,143.04로 1.93% 상승했고 5일 누적 수익률도 7.573%에 달해 상승 모멘텀이 강하지만, 단기 과열 가능성을 함께 점검해야 합니다.
  ↳ 출처: `market_data, cumulative_context`
- USD/KRW는 1,375.64로 1.06% 하락하고 VIX는 14.87로 5일 평균 16.018을 밑돌아 위험선호 환경을 뒷받침했습니다.
  ↳ 출처: `macro_daily, cumulative_context`
- 외국인·기관·개인 순매수는 수집 실패로 확인할 수 없어, 지수 상승을 특정 투자주체의 지속적 매수로 해석하기 어렵습니다.
  ↳ 출처: `flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 최근 증시 강세에도 불확실성은 여전히 남아 있습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI와 글로벌 증시가 최근 강세를 보이고 있습니다.
- 핵심 주장: 변동성 지수(VIX)가 낮고, 환율도 안정적인 흐름을 보입니다.
- 핵심 주장: 다만, 매크로 불확실성과 유가 상승 등 리스크 요인도 존재합니다.

### 수급 담당자
- 한줄 요약: 수급 데이터 부재로 주체별 매매 해석이 제한적입니다.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: 수급 데이터 부재로 외국인/기관/개인 주체별 흐름 해석 불가.
- 핵심 주장: 최근 5일간 KOSPI 7%대 급등, 반도체/AI, 연준/금리, 고환율 이슈가 핵심.
- 핵심 주장: 국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 변동성만 반영.

### 섹터 담당자
- 한줄 요약: 국내외 증시 모두 강세 흐름이 뚜렷합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 7% 이상 상승하며 강한 모멘텀을 보이고 있다.
- 핵심 주장: 미국 증시와 AI/반도체 섹터 강세가 국내 시장에도 긍정적으로 작용 중이다.
- 핵심 주장: 변동성(VIX)도 낮아 위험 선호 심리가 유지되고 있다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 뚜렷한 위험 신호는 보이지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 7% 이상 상승
- 핵심 주장: 변동성(VIX) 낮고 환율 안정적
- 핵심 주장: 누적 지표상 위험 신호 없음

### 이익모멘텀 담당자
- 한줄 요약: 실적 추세 변화 신호는 아직 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀 신호는 부재하며, 추세적 상향 조정은 감지되지 않음.
- 핵심 주장: 최근 주가 상승은 실적 상향 기대보다는 유동성 및 심리 개선 영향.

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸친 상승 확산이 뚜렷합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 최근 5일간 강한 상승세를 보임.
- 핵심 주장: 미국 주요 지수도 동반 상승하며 글로벌 확산 양상.
- 핵심 주장: 시장 변동성(VIX)도 낮아 위험 선호 분위기 유지.

### 유동성 담당자
- 한줄 요약: 정책 리스크에도 시장 유동성은 견조한 편입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 정책 불확실성에도 변동성은 낮고, 환율도 안정적입니다.
- 핵심 주장: 최근 5일간 KOSPI 상승세와 유동성 신호가 긍정적입니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 5명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '최근 증시 강세에도 불확실성은 여전히 남아 있습니다.' 의견을 유지합니다. 근거 숫자는 vix=14.9, usdkrw=1375.64입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.markets.us.sp500_pct, snapshot.markets.us.nasdaq_pct, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg, snapshot.market_summary.usdkrw, snapshot.news_headlines
- [수급 담당자] 저는 수급 담당자 입장에서 '수급 데이터 부재로 주체별 매매 해석이 제한적입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+0억, institution_net=+0억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.flow_summary.retail_net, snapshot.news_headlines, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.market_summary.kospi_change_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '국내외 증시 모두 강세 흐름이 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 vix=14.9입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.news_headlines, snapshot.markets.us.nasdaq_pct, snapshot.markets.kr.kospi_pct, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 뚜렷한 위험 신호는 보이지 않습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+1.93%, vix=14.9입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.kospi_change_pct, snapshot.markets.volatility.vix, snapshot.market_summary.usdkrw
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추세 변화 신호는 아직 뚜렷하지 않습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.news_headlines, snapshot.market_summary.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸친 상승 확산이 뚜렷합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct, snapshot.markets.us.sp500_pct, snapshot.markets.us.nasdaq_pct, snapshot.markets.us.dow_pct, snapshot.cumulative_context.vix_5d_avg
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 리스크에도 시장 유동성은 견조한 편입니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1375.64, kospi_change_pct=+1.93%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.usdkrw, snapshot.market_summary.kospi_change_pct, snapshot.macro.daily.vix, snapshot.phase_two_signals.liquidity_signal_score, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.news_headlines
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +1.93%, USD/KRW 1375.64(-1.06%), VIX 14.9, 외국인 +0억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 시장 국면 판단: 다수=다수는 강한 주가 흐름을 인정하면서도 수급과 실적 확인 전까지 중립 대응을 선호했습니다., 소수=섹터와 브레드스 담당자는 국내외 지수의 동반 상승과 낮은 VIX를 근거로 위험선호 국면을 더 강하게 평가했습니다., 에이전트=[섹터 담당자, 브레드스 담당자]
  - 의미: KOSPI의 5일 누적 상승률이 7.573%인 만큼 추격 매수와 조정 대기 중 어느 쪽에 무게를 둘지 좌우합니다.
- 상승의 지속 가능성: 다수=가격·환율·변동성 조합은 우호적이지만 금리와 유가, 실적 신호 부재 때문에 추가 확인이 필요하다는 판단입니다., 소수=이익모멘텀 담당자는 실적 상향 신호가 뚜렷하지 않아 최근 상승을 유동성과 심리 개선 중심으로 해석했습니다., 에이전트=[이익모멘텀 담당자]
  - 의미: 실적 확인 없이 밸류에이션과 심리만으로 상승할 경우 금리·물가 뉴스에 대한 민감도가 커질 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI와 글로벌 증시가 최근 강세를 보이고 있습니다.",
    "변동성 지수(VIX)가 낮고, 환율도 안정적인 흐름을 보입니다.",
    "다만, 매크로 불확실성과 유가 상승 등 리스크 요인도 존재합니다."
  ],
  "korean_comment": "최근 증시 강세에도 불확실성은 여전히 남아 있습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.macro.daily.oil_wti"
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
    "최근 5일간 KOSPI 7%대 급등, 반도체/AI, 연준/금리, 고환율 이슈가 핵심.",
    "국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 변동성만 반영."
  ],
  "korean_comment": "수급 데이터 부재로 주체별 매매 해석이 제한적입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.flow_summary.retail_net",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.volatility.vix",
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
    "KOSPI가 최근 5일간 7% 이상 상승하며 강한 모멘텀을 보이고 있다.",
    "미국 증시와 AI/반도체 섹터 강세가 국내 시장에도 긍정적으로 작용 중이다.",
    "변동성(VIX)도 낮아 위험 선호 심리가 유지되고 있다."
  ],
  "korean_comment": "국내외 증시 모두 강세 흐름이 뚜렷합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.news_headlines",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{"agent_name": "RISK_pre_analysis_agent", "core_claims": ["KOSPI가 최근 5일간 7% 이상 상승", "변동성(VIX) 낮고 환율 안정적", "누적 지표상 위험 신호 없음"], "korean_comment": "시장 전반에 뚜렷한 위험 신호는 보이지 않습니다.", "regime_tag": "RISK_OFF", "evidence_ids": ["snapshot.cumulative_context.kospi_5d_cum_pct", "snapshot.cumulative_context.kospi_20d_cum_pct", "snapshot.cumulative_context.vix_5d_avg", "snapshot.cumulative_context.usdkrw_5d_change_pct", "snapshot.cumulative_context.reversal_signal", "snapshot.market_summary.kospi_change_pct", "snapshot.markets.volatility.vix", "snapshot.market_summary.usdkrw", "snapshot.news_headlines"], "confidence": "HIGH"}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 신호는 부재하며, 추세적 상향 조정은 감지되지 않음.",
    "최근 주가 상승은 실적 상향 기대보다는 유동성 및 심리 개선 영향."
  ],
  "korean_comment": "실적 추세 변화 신호는 아직 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
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
    "KOSPI와 KOSDAQ 모두 최근 5일간 강한 상승세를 보임.",
    "미국 주요 지수도 동반 상승하며 글로벌 확산 양상.",
    "시장 변동성(VIX)도 낮아 위험 선호 분위기 유지."
  ],
  "korean_comment": "시장 전반에 걸친 상승 확산이 뚜렷합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.us.dow_pct",
    "snapshot.cumulative_context.vix_5d_avg",
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
    "정책 불확실성에도 변동성은 낮고, 환율도 안정적입니다.",
    "최근 5일간 KOSPI 상승세와 유동성 신호가 긍정적입니다."
  ],
  "korean_comment": "정책 리스크에도 시장 유동성은 견조한 편입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.macro.daily.vix",
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.news_headlines"
  ],
  "confidence": "MED"
}
```