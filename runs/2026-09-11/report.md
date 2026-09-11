# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-09-11**
- 생성 시각(UTC): `2026-09-11T00:52:53.057644+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=0, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -2.66% / KOSDAQ -2.06%
- **미국 지수**: S&P500 -0.58% / NASDAQ -0.65% / DOW -0.60%
- **환율/변동성**: USD/KRW 1345.06 (-0.19%) / VIX 17.8
- **시장 요약 노트**: KOSPI -2.66%, USD/KRW 1345.06. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -8975억 / 기관 -7505억 / 개인 +13897억
- **일간 매크로**: 미10년 4.94% / 미2년 3.85% / 2-10 1.10%p / DXY 99.07
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.54% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.54%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 6,835.34로 2.66% 하락했고 KOSDAQ도 819.64로 2.06% 내렸다. 외국인 -8,975억원과 기관 -7,505억원 매도가 개인 +1조3,897억원 매수를 압도했다.
  ↳ 출처: `flow_data, market_data`
- VIX는 17.84로 5일 평균 16.384를 상회했다. 고유가·고금리 및 FOMC 경계 뉴스가 위험자산 회피의 배경으로 작용했으나, 원/달러는 1,345.06원으로 0.19% 하락해 환율 주도 이탈로 단정하기는 어렵다.
  ↳ 출처: `macro_daily, cumulative_context, news`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 시장 전반에 불확실성과 위험회피 심리가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI가 단기적으로 크게 하락하며 외국인과 기관의 매도세가 강하다.
- 핵심 주장: 고유가, 고금리, 지정학적 리스크 등으로 위험회피 심리가 확대되고 있다.
- 핵심 주장: 20일 누적 수익률도 부진해 전반적으로 보수적 접근이 필요하다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안정 지속.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고금리/연준, 고유가, 반도체/AI 급락 등 대외 불확실성(금리/연준, 에너지/원자재, 반도체/AI) 영향이 복합적으로 작용.
- 핵심 주장: USD/KRW는 소폭 하락했으나, 외국인 매도와 동반되지 않아 환율 주도 자금 유출은 아님.
- 핵심 주장: 개인 매수세는 단기 낙폭 확대에 따른 저가매수 성격이나, 최근 5일간 KOSPI 누적상승(+2.5%) 이후 급락이므로 추격매수/레버리지성 위험 존재.

### 섹터 담당자
- 한줄 요약: 시장 전반에 위험회피 심리가 강하게 작용하고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 단기 급락하며 외국인과 기관의 대규모 순매도가 확인됨.
- 핵심 주장: 고유가·고금리·중동 리스크 등 대외 불확실성으로 투자심리 위축.
- 핵심 주장: 20일 누적 기준 KOSPI는 약세 흐름을 보이고 있음.

### 리스크 담당자
- 한줄 요약: 단기 급락에도 누적 흐름은 과도한 위험 신호를 보이지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 급락했으나 최근 5일 누적은 플러스
- 핵심 주장: 외국인·기관 대규모 순매도, 개인 매수세 유입
- 핵심 주장: 20일 누적 하락폭은 제한적이며 반전 신호 없음

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 전환 신호가 아직 나타나지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 약화 신호가 뚜렷하다.
- 핵심 주장: 외국인 대규모 순매도와 변동성 확대가 지속된다.
- 핵심 주장: 단기 반등에도 불구하고 실적 추정치 상향 모멘텀 부재.

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸쳐 확산 약화와 위험회피가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 시장 하락폭이 크고, 수급과 확산 모두 부진하다.
- 핵심 주장: 20일 누적 수익률도 마이너스이며, 반전 신호는 없다.

### 유동성 담당자
- 한줄 요약: 정책 불확실성과 외국인 자금 이탈로 유동성 경색 신호가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 금리 인상 우려와 외국인 대규모 순매도, 변동성 확대가 뚜렷하다.
- 핵심 주장: 환율은 안정적이나, 유동성 및 정책 불확실성으로 위험회피 심리가 강하다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '시장 전반에 불확실성과 위험회피 심리가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.66%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.macro.daily.oil_wti, snapshot.macro.daily.us10y, snapshot.macro.daily.vix, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안정 지속.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.66%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.macro.daily.oil_wti
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 위험회피 심리가 강하게 작용하고 있습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.note, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 급락에도 누적 흐름은 과도한 위험 신호를 보이지 않습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.66%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 전환 신호가 아직 나타나지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8975억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.market_summary.note, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸쳐 확산 약화와 위험회피가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.66%, foreign_net=-8975억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.breadth_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 불확실성과 외국인 자금 이탈로 유동성 경색 신호가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.66%, foreign_net=-8975억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.phase_two_signals.liquidity_signal_score
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -2.66%, USD/KRW 1345.06(-0.19%), VIX 17.8, 외국인 -8975억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 단기 급락의 추세적 위험 전환 여부: 다수=매크로·수급·섹터·이익모멘텀·브레드스·유동성 담당자는 외국인·기관 동반 매도와 변동성 확대를 근거로 리스크오프 지속을 판단했다., 소수=단기 하락은 컸지만 5일 누적 상승과 제한적인 20일 누적 하락을 고려하면 과도한 위험 신호로 단정하기 어렵다는 중립 의견이다., 에이전트=[risk]
  - 의미: 낙폭과대 반등 가능성은 남아 있으나 반전 신호가 없으므로, 반등 시 추격 확대보다 외국인·기관 수급의 지속적 개선 확인이 필요하다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 단기적으로 크게 하락하며 외국인과 기관의 매도세가 강하다.",
    "고유가, 고금리, 지정학적 리스크 등으로 위험회피 심리가 확대되고 있다.",
    "20일 누적 수익률도 부진해 전반적으로 보수적 접근이 필요하다."
  ],
  "korean_comment": "시장 전반에 불확실성과 위험회피 심리가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.news_headlines",
    "snapshot.macro.daily.oil_wti",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.vix",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인 대규모 순매도는 고금리/연준, 고유가, 반도체/AI 급락 등 대외 불확실성(금리/연준, 에너지/원자재, 반도체/AI) 영향이 복합적으로 작용.",
    "USD/KRW는 소폭 하락했으나, 외국인 매도와 동반되지 않아 환율 주도 자금 유출은 아님.",
    "개인 매수세는 단기 낙폭 확대에 따른 저가매수 성격이나, 최근 5일간 KOSPI 누적상승(+2.5%) 이후 급락이므로 추격매수/레버리지성 위험 존재."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안정 지속.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.oil_wti",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 단기 급락하며 외국인과 기관의 대규모 순매도가 확인됨.",
    "고유가·고금리·중동 리스크 등 대외 불확실성으로 투자심리 위축.",
    "20일 누적 기준 KOSPI는 약세 흐름을 보이고 있음."
  ],
  "korean_comment": "시장 전반에 위험회피 심리가 강하게 작용하고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.note",
    "snapshot.flow_summary.note",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
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
    "KOSPI가 단기 급락했으나 최근 5일 누적은 플러스",
    "외국인·기관 대규모 순매도, 개인 매수세 유입",
    "20일 누적 하락폭은 제한적이며 반전 신호 없음"
  ],
  "korean_comment": "단기 급락에도 누적 흐름은 과도한 위험 신호를 보이지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
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
    "실적 모멘텀 약화 신호가 뚜렷하다.",
    "외국인 대규모 순매도와 변동성 확대가 지속된다.",
    "단기 반등에도 불구하고 실적 추정치 상향 모멘텀 부재."
  ],
  "korean_comment": "실적 추정치 상향 전환 신호가 아직 나타나지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.market_summary.note",
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
    "시장 하락폭이 크고, 수급과 확산 모두 부진하다.",
    "20일 누적 수익률도 마이너스이며, 반전 신호는 없다."
  ],
  "korean_comment": "시장 전반에 걸쳐 확산 약화와 위험회피가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
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
    "금리 인상 우려와 외국인 대규모 순매도, 변동성 확대가 뚜렷하다.",
    "환율은 안정적이나, 유동성 및 정책 불확실성으로 위험회피 심리가 강하다."
  ],
  "korean_comment": "정책 불확실성과 외국인 자금 이탈로 유동성 경색 신호가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```