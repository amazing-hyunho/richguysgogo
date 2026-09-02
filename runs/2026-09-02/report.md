# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-09-02**
- 생성 시각(UTC): `2026-09-02T03:17:43.634499+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=0, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -2.45% / KOSDAQ -0.39%
- **미국 지수**: S&P500 -0.71% / NASDAQ -1.03% / DOW -0.79%
- **환율/변동성**: USD/KRW 1373.78 (-0.27%) / VIX 16.3
- **시장 요약 노트**: KOSPI -2.45%, USD/KRW 1373.78. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -4081억 / 기관 -6071억 / 개인 +7837억
- **일간 매크로**: 미10년 4.80% / 미2년 3.77% / 2-10 1.02%p / DXY 99.70
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.54% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.45%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 6,657.68로 2.45% 하락했고, 외국인 -4,081억원·기관 -6,071억원 순매도에 개인 +7,837억원이 대응한 공급 우위 장세였습니다.
  ↳ 출처: `flow_data, macro_daily`
- 미국 10년물 금리 4.796%, WTI 91.65, VIX 16.34과 중동·매파 연준 뉴스가 위험자산 할인율 및 반도체 투자심리를 동시에 압박했습니다.
  ↳ 출처: `macro_daily, news`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 단기적으로 위험회피 심리가 우세해 보입니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 5일간 크게 하락하며 투자심리가 위축되었습니다.
- 핵심 주장: 글로벌 금리 상승과 외국인·기관의 순매도세가 부담으로 작용하고 있습니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인이 방어적 매수로 흡수하는 공급 우위 장세.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인은 KOSPI에서 대규모 순매도로 위험회피 성향이 뚜렷하며, 이는 금리/연준, 고유가, 반도체/AI 약세 등 글로벌 리스크 요인과 연동됨.
- 핵심 주장: USD/KRW는 소폭 하락했으나, 외국인 매도와 동반되지 않아 환율 주도 자금 유출이 아니라 글로벌 금리/AI 테마 약세에 따른 리밸런싱 성격이 강함.
- 핵심 주장: 개인은 대규모 매수로 외국인·기관 매물을 흡수했으나, 최근 5일간 KOSPI가 -3.8% 하락한 점을 감안하면 추격성·방어적 매수로 보이며 지속성은 제한적.

### 섹터 담당자
- 한줄 요약: 시장 전반에 위험회피 심리가 강하게 작용하고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 -3.8% 하락하며 약세가 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.
- 핵심 주장: 글로벌 금리 급등과 AI/반도체주 약세가 시장 전반에 부담을 주고 있습니다.

### 리스크 담당자
- 한줄 요약: 단기 약세지만 중장기 위험 신호는 아직 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI 5일간 약세 지속
- 핵심 주장: 외국인·기관 동반 순매도
- 핵심 주장: 20일 누적 변동성은 제한적

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 모멘텀은 부재하며, 단기 반등 신호도 없다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 약화 신호가 뚜렷하다.
- 핵심 주장: 외국인·기관 매도세와 5일 누적 하락이 지속적이다.

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸쳐 하락 압력이 확산되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락폭이 크고, 시장 내 확산 약화가 뚜렷하다.
- 핵심 주장: 외국인·기관 동반 순매도, 시장 내부 확산도 저조하다.
- 핵심 주장: 20일 누적은 보합이나 단기적으로 리스크 확산이 우세하다.

### 유동성 담당자
- 한줄 요약: 유동성 악화와 금리 상승으로 보수적 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일간 -3.8% 하락, 외국인·기관 대규모 순매도.
- 핵심 주장: 미국 금리 급등, 변동성(VIX) 상승세.
- 핵심 주장: 정책·유동성 환경이 위험회피로 전환 중.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 5명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '단기적으로 위험회피 심리가 우세해 보입니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.45%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note, snapshot.cumulative_context.vix_5d_avg
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인이 방어적 매수로 흡수하는 공급 우위 장세.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.45%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.macro.daily.oil_wti, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 위험회피 심리가 강하게 작용하고 있습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.market_summary.note, snapshot.markets.kr.kospi_pct
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 약세지만 중장기 위험 신호는 아직 뚜렷하지 않습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4081억, institution_net=-6071억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.note
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 모멘텀은 부재하며, 단기 반등 신호도 없다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4081억, institution_net=-6071억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.reversal_signal, snapshot.news_headlines
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸쳐 하락 압력이 확산되고 있습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.note, snapshot.markets.kr.kospi_pct, snapshot.markets.kr.kosdaq_pct, snapshot.markets.us.sp500_pct, snapshot.markets.us.nasdaq_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 악화와 금리 상승으로 보수적 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-4081억, institution_net=-6071억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.macro.daily.us10y, snapshot.markets.volatility.vix, snapshot.news_headlines, snapshot.cumulative_context.vix_5d_avg
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -2.45%, USD/KRW 1373.78(-0.27%), VIX 16.3, 외국인 -4081억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 단기 하락의 중기 추세 훼손 여부: 다수=매크로·수급·섹터·이익모멘텀·브레드스·유동성 담당자는 동반 매도와 금리 부담을 근거로 위험회피 국면 지속을 판단했습니다., 소수=리스크 담당자는 단기 약세는 인정하되 20일 누적 KOSPI가 +0.003%이고 VIX가 16.34인 점에서 중장기 위험 신호는 아직 뚜렷하지 않다고 봤습니다., 에이전트=[risk]
  - 의미: 5일 조정이 중기 하락 추세로 확대되는지, 또는 단기 변동성으로 마무리되는지에 따라 개인의 매수 흡수력을 해석하는 방식이 달라집니다.
- 환율의 수급 설명력: 다수=수급 담당자는 USD/KRW가 1,373.777338로 0.269% 하락했음에도 외국인 순매도가 나타난 만큼 환율보다는 금리·유가 및 AI·반도체 약세에 따른 리밸런싱 성격이 강하다고 판단했습니다., 소수=뉴스에서는 중동 긴장에 따른 달러 강세와 1,370원대 환율 재진입 가능성을 강조해, 향후 환율 변동이 외국인 수급을 악화시킬 위험을 제기했습니다., 에이전트=[해당 없음]
  - 의미: 원화가 당일 강세였다는 실제 수치와 달러 강세 뉴스 흐름의 괴리가 지속될 경우, 외국인 매도의 원인과 지속성 판단에 오류가 생길 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 5일간 크게 하락하며 투자심리가 위축되었습니다.",
    "글로벌 금리 상승과 외국인·기관의 순매도세가 부담으로 작용하고 있습니다."
  ],
  "korean_comment": "단기적으로 위험회피 심리가 우세해 보입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.note",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market investor behavior)",
  "core_claims": [
    "외국인은 KOSPI에서 대규모 순매도로 위험회피 성향이 뚜렷하며, 이는 금리/연준, 고유가, 반도체/AI 약세 등 글로벌 리스크 요인과 연동됨.",
    "USD/KRW는 소폭 하락했으나, 외국인 매도와 동반되지 않아 환율 주도 자금 유출이 아니라 글로벌 금리/AI 테마 약세에 따른 리밸런싱 성격이 강함.",
    "개인은 대규모 매수로 외국인·기관 매물을 흡수했으나, 최근 5일간 KOSPI가 -3.8% 하락한 점을 감안하면 추격성·방어적 매수로 보이며 지속성은 제한적."
  ],
  "korean_comment": "외국인 매도 우위, 개인이 방어적 매수로 흡수하는 공급 우위 장세.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.oil_wti",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
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
    "KOSPI가 최근 5일간 -3.8% 하락하며 약세가 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.",
    "글로벌 금리 급등과 AI/반도체주 약세가 시장 전반에 부담을 주고 있습니다."
  ],
  "korean_comment": "시장 전반에 위험회피 심리가 강하게 작용하고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.news_headlines",
    "snapshot.market_summary.note",
    "snapshot.markets.kr.kospi_pct"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI 5일간 약세 지속",
    "외국인·기관 동반 순매도",
    "20일 누적 변동성은 제한적"
  ],
  "korean_comment": "단기 약세지만 중장기 위험 신호는 아직 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
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
    "외국인·기관 매도세와 5일 누적 하락이 지속적이다."
  ],
  "korean_comment": "실적 추정치 상향 모멘텀은 부재하며, 단기 반등 신호도 없다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.reversal_signal",
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
    "KOSPI 5일 누적 하락폭이 크고, 시장 내 확산 약화가 뚜렷하다.",
    "외국인·기관 동반 순매도, 시장 내부 확산도 저조하다.",
    "20일 누적은 보합이나 단기적으로 리스크 확산이 우세하다."
  ],
  "korean_comment": "시장 전반에 걸쳐 하락 압력이 확산되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.note",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.us.nasdaq_pct"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI 5일간 -3.8% 하락, 외국인·기관 대규모 순매도.",
    "미국 금리 급등, 변동성(VIX) 상승세.",
    "정책·유동성 환경이 위험회피로 전환 중."
  ],
  "korean_comment": "유동성 악화와 금리 상승으로 보수적 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.macro.daily.us10y",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```