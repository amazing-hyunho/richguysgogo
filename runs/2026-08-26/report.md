# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-08-26**
- 생성 시각(UTC): `2026-08-26T00:52:28.210279+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.
- **국면 투표**: NEUTRAL=6, RISK_ON=1, RISK_OFF=0
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 확인된 모멘텀 주도주 중심으로 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] 변동성 한도를 기준으로 포지션 규모를 조절합니다.
- [OpsGuidanceLevel.AVOID/회피] 과열된 돌파 구간 추격 매수는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +0.15% / KOSDAQ -0.77%
- **미국 지수**: S&P500 +0.32% / NASDAQ +0.66% / DOW +0.30%
- **환율/변동성**: USD/KRW 1383.12 (+0.15%) / VIX 15.4
- **시장 요약 노트**: KOSPI 0.15%, USD/KRW 1383.12. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -4275억 / 기관 -894억 / 개인 +3104억
- **일간 매크로**: 미10년 4.64% / 미2년 3.70% / 2-10 0.93%p / DXY 98.92
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.54% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.32%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_ON.
  ↳ 출처: `regime_tuner`
- KOSPI는 6,752.95로 0.15% 상승했으나, 외국인 -4,275억원·기관 -894억원을 개인 +3,104억원이 흡수해 수급의 질은 약화됐다.
  ↳ 출처: `flow_data, macro_daily`
- KOSPI 5일·20일 누적 상승률은 각각 4.481%, 19.936%로 높아 차익실현 압력이 자연스러운 구간이다. 다만 VIX 15.45는 5일 평균 15.482와 유사하다.
  ↳ 출처: `macro_daily, flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기 급등 이후 조정 가능성에 유의해야 합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 20일간 강한 상승세를 보였으나 외국인 순매도와 환율 상승이 부담입니다.
- 핵심 주장: 미국 증시와 글로벌 위험지표는 안정적이지만, 국내 수급은 단기적으로 불안정합니다.

### 수급 담당자
- 한줄 요약: 이익실현성 외국인 매도와 개인의 추격매수 구도, 공급 우위 전환 신호.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 최근 KOSPI 20일간 20% 가까운 급등에 따른 차익실현(이익실현) 성격이 강함.
- 핵심 주장: USD/KRW 환율은 소폭 상승했으나 5일 누적으로는 하락, 환차손 회피 목적의 급격한 외화 유출은 아님.
- 핵심 주장: 개인 매수세는 최근 급등장 이후 레버리지 추격매수 가능성 높아, 지속성에는 의문.

### 섹터 담당자
- 한줄 요약: 강한 상승세가 지속되고 있으나 외국인 매도세는 주의가 필요합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 19% 이상 상승하며 강한 모멘텀을 보이고 있습니다.
- 핵심 주장: 외국인과 기관의 순매도에도 불구하고 시장은 견조한 흐름을 유지하고 있습니다.
- 핵심 주장: 미국 증시와 반도체 업종 강세가 국내 시장에도 긍정적으로 작용하고 있습니다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 뚜렷한 위험 신호는 없습니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 19% 이상 상승하며 강한 흐름을 보임
- 핵심 주장: 외국인 순매도에도 시장 변동성(VIX)과 환율은 안정적
- 핵심 주장: 단기 조정 신호나 리스크 전환 신호는 감지되지 않음

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 모멘텀은 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀 신호는 중립적입니다.
- 핵심 주장: 20일 누적 상승에도 추가 상향 조정 신호는 제한적입니다.

### 브레드스 담당자
- 한줄 요약: 지수는 강하지만 확산세는 둔화되고 있습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI의 20일 누적 상승률이 매우 강하다.
- 핵심 주장: 단기적으로 외국인 매도와 KOSDAQ 약세가 혼재되어 있다.
- 핵심 주장: 시장 전반의 확산도는 다소 약화 조짐이 있다.

### 유동성 담당자
- 한줄 요약: 유동성은 견조하지만 외국인 매도와 환율이 리스크다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 정책 및 유동성 환경은 중립적이다.
- 핵심 주장: 외국인 자금 유출과 환율 상승이 부담 요인이다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 5명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기 급등 이후 조정 가능성에 유의해야 합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4275억, usdkrw=1383.12입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.markets.volatility.vix, snapshot.news_headlines, snapshot.cumulative_context.usdkrw_5d_change_pct
- [수급 담당자] 저는 수급 담당자 입장에서 '이익실현성 외국인 매도와 개인의 추격매수 구도, 공급 우위 전환 신호.' 의견을 유지합니다. 근거 숫자는 usdkrw=1383.12, vix=15.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.markets.volatility.vix
- [섹터 담당자] 저는 섹터 담당자 입장에서 '강한 상승세가 지속되고 있으나 외국인 매도세는 주의가 필요합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.markets.us.sp500_pct, snapshot.markets.us.nasdaq_pct, snapshot.market_summary.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 뚜렷한 위험 신호는 없습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4275억, vix=15.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.note, snapshot.market_summary.usdkrw
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 모멘텀은 뚜렷하지 않습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수는 강하지만 확산세는 둔화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4275억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.markets.kr.kosdaq_pct, snapshot.cumulative_context.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성은 견조하지만 외국인 매도와 환율이 리스크다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4275억, vix=15.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.markets.volatility.vix, snapshot.phase_two_signals.liquidity_signal_score
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +0.15%, USD/KRW 1383.12(+0.15%), VIX 15.4, 외국인 -4275억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 외국인 순매도의 성격과 추세 지속성: 다수=다수는 최근 급등에 따른 이익실현과 단기 수급 불안으로 보며, 중립 비중과 확인 후 대응이 적절하다고 판단했다., 소수=상승 모멘텀이 미국 반도체 강세와 결합해 이어질 수 있다는 의견이다., 에이전트=[sector]
  - 의미: 외국인 매도가 하루성 차익실현에 그치면 추세 훼손은 제한적일 수 있으나, 환율 상승과 함께 이어지면 개인 매수만으로 지수 방어가 어려워질 수 있다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO",
  "core_claims": [
    "KOSPI는 최근 20일간 강한 상승세를 보였으나 외국인 순매도와 환율 상승이 부담입니다.",
    "미국 증시와 글로벌 위험지표는 안정적이지만, 국내 수급은 단기적으로 불안정합니다."
  ],
  "korean_comment": "단기 급등 이후 조정 가능성에 유의해야 합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.usdkrw_5d_change_pct"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market, investor behavior)",
  "core_claims": [
    "외국인 대규모 순매도는 최근 KOSPI 20일간 20% 가까운 급등에 따른 차익실현(이익실현) 성격이 강함.",
    "USD/KRW 환율은 소폭 상승했으나 5일 누적으로는 하락, 환차손 회피 목적의 급격한 외화 유출은 아님.",
    "개인 매수세는 최근 급등장 이후 레버리지 추격매수 가능성 높아, 지속성에는 의문."
  ],
  "korean_comment": "이익실현성 외국인 매도와 개인의 추격매수 구도, 공급 우위 전환 신호.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
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
    "KOSPI는 최근 20일간 19% 이상 상승하며 강한 모멘텀을 보이고 있습니다.",
    "외국인과 기관의 순매도에도 불구하고 시장은 견조한 흐름을 유지하고 있습니다.",
    "미국 증시와 반도체 업종 강세가 국내 시장에도 긍정적으로 작용하고 있습니다."
  ],
  "korean_comment": "강한 상승세가 지속되고 있으나 외국인 매도세는 주의가 필요합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.news_headlines",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.us.nasdaq_pct",
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
    "KOSPI는 최근 20일간 19% 이상 상승하며 강한 흐름을 보임",
    "외국인 순매도에도 시장 변동성(VIX)과 환율은 안정적",
    "단기 조정 신호나 리스크 전환 신호는 감지되지 않음"
  ],
  "korean_comment": "시장 전반에 뚜렷한 위험 신호는 없습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.note",
    "snapshot.market_summary.usdkrw"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 신호는 중립적입니다.",
    "20일 누적 상승에도 추가 상향 조정 신호는 제한적입니다."
  ],
  "korean_comment": "실적 추정치 상향 모멘텀은 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.note",
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
    "KOSPI의 20일 누적 상승률이 매우 강하다.",
    "단기적으로 외국인 매도와 KOSDAQ 약세가 혼재되어 있다.",
    "시장 전반의 확산도는 다소 약화 조짐이 있다."
  ],
  "korean_comment": "지수는 강하지만 확산세는 둔화되고 있습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "정책 및 유동성 환경은 중립적이다.",
    "외국인 자금 유출과 환율 상승이 부담 요인이다."
  ],
  "korean_comment": "유동성은 견조하지만 외국인 매도와 환율이 리스크다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "MED"
}
```