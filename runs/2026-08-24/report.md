# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-08-24**
- 생성 시각(UTC): `2026-08-24T04:15:26.085902+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 오늘 국내 증시는 외국인 대규모 매도와 단기 변동성 확대에 따라 방어적 대응이 필요한 위험회피(Risk-off) 국면입니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=0, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 방어적 포트폴리오 유지, 현금 비중 확대 및 변동성 완화 확인 전까지 신규 공격적 매수 자제
- [OpsGuidanceLevel.CAUTION/주의] 외국인·기관 매도세 지속 및 단기 변동성 확대 구간에서는 저가매수 시도도 분할 접근 필요
- [OpsGuidanceLevel.AVOID/회피] 대외 금리·정책 불확실성, 글로벌 관세 이슈 등 불확실성 해소 전까지 레버리지·고위험군 비중 확대는 피할 것

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.16% / KOSDAQ +1.30%
- **미국 지수**: S&P500 +0.43% / NASDAQ +0.43% / DOW +0.98%
- **환율/변동성**: USD/KRW 1385.48 (-0.22%) / VIX 15.1
- **시장 요약 노트**: KOSPI -3.16%, USD/KRW 1385.48. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -27678억 / 기관 -8711억 / 개인 +24742억
- **일간 매크로**: 미10년 4.74% / 미2년 3.71% / 2-10 1.03%p / DXY 98.84
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.54% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.40%

## 4) 위원회 핵심 포인트
- KOSPI가 -3.16% 급락(6694.54p), 외국인 -2.8조원 순매도, 개인 저가매수 유입에도 수급 불안정 심화.
  ↳ 출처: `flow_data, macro_daily`
- USD/KRW 환율은 1385.48원(-0.22%)로 하락하며 안정적이나, 변동성(VIX 15.1)과 미국 금리 이슈로 투자심리 위축.
  ↳ 출처: `macro_daily, news`
- 뉴스 이슈는 연준 매파 발언, 미 국채금리 급등, 글로벌 관세 갈등 등 대외 불확실성에 집중.
  ↳ 출처: `news`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 국내 증시는 외국인 이탈과 변동성 증가로 신중한 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: 코스피가 최근 5일간 크게 하락하며 외국인 매도세가 강하게 나타남.
- 핵심 주장: 미국 증시는 견조하나 국내 시장은 변동성 확대와 위험회피 심리가 우세함.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안정 지속.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인은 KOSPI에서 대규모 순매도, 이는 고금리/연준, 반도체/AI, 환율 안정(USD/KRW 하락) 키워드와 연관.
- 핵심 주장: 외국인 매도는 환율 상승이 아닌, 미국 금리 급등 및 글로벌 반도체/AI 관련 차익실현 성격이 강함.
- 핵심 주장: 개인 매수는 KOSPI 급락에 따른 저가매수 시도로 보이나, 최근 5일간 누적 하락세와 변동성 확대를 감안하면 지속성은 낮음.

### 섹터 담당자
- 한줄 요약: 단기적으로 시장에 하방 압력이 강하게 작용하고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 -3.7% 하락하며 단기 약세가 뚜렷하다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 지속되고 있다.
- 핵심 주장: 20일 누적으로는 상승세이나 단기 변동성 확대에 주의 필요하다.

### 리스크 담당자
- 한줄 요약: 단기 충격이 크지만 누적 흐름은 아직 위험 전환 신호 부족합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 코스피 단기 급락이 있었으나 20일 누적 상승세 유지
- 핵심 주장: 외국인 대규모 순매도와 변동성 확대 신호
- 핵심 주장: 환율 안정과 미국 증시 강세로 과도한 공포는 아님

### 이익모멘텀 담당자
- 한줄 요약: 실적 추세가 단기적으로 더 약화될 가능성이 높아 보입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 약화 신호가 뚜렷함
- 핵심 주장: 외국인 대규모 순매도와 코스피 5일 누적 하락이 지속적 부담
- 핵심 주장: 단기 반등 기대감은 있으나 실적 추세 개선 신호는 부재

### 브레드스 담당자
- 한줄 요약: 시장 확산 약화와 매도세가 뚜렷하게 나타난 구간입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락과 시장 내 확산 약화가 뚜렷하다.
- 핵심 주장: 외국인·기관 동반 매도세로 시장 내부 체력이 저하되었다.

### 유동성 담당자
- 한줄 요약: 유동성 경색과 외국인 이탈로 위험회피 국면이 강화되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도와 코스피 급락으로 유동성 악화 신호.
- 핵심 주장: 환율 하락에도 불구하고 변동성 상승과 외국인 이탈이 위험회피 심리 강화.
- 핵심 주장: 정책 및 금리 불확실성으로 보수적 유동성 환경 지속.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '국내 증시는 외국인 이탈과 변동성 증가로 신중한 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.16%, foreign_net=-27678억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note, snapshot.markets.us.sp500_pct, snapshot.markets.volatility.vix
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안정 지속.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.16%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.macro.daily.us10y, snapshot.news_headlines, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기적으로 시장에 하방 압력이 강하게 작용하고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.16%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 충격이 크지만 누적 흐름은 아직 위험 전환 신호 부족합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.16%, foreign_net=-27678억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.markets.us.sp500_pct, snapshot.markets.volatility.vix
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추세가 단기적으로 더 약화될 가능성이 높아 보입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-27678억, kospi_change_pct=-3.16%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.foreign_net, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.kospi_change_pct, snapshot.news_headlines, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 확산 약화와 매도세가 뚜렷하게 나타난 구간입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-27678억, institution_net=-8711억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 경색과 외국인 이탈로 위험회피 국면이 강화되고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.16%, foreign_net=-27678억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.markets.volatility.vix, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.news_headlines
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.16%, USD/KRW 1385.48(-0.22%), VIX 15.1, 외국인 -27678억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 단기 급락 이후 시장 방향성: 다수=단기 변동성 확대와 외국인 매도세로 위험회피 기조 유지 필요, 소수=20일 누적 상승세와 환율 안정, 미국 증시 강세로 과도한 공포는 경계, 에이전트=[risk]
  - 의미: 단기 충격이 누적 하락 전환 신호로 이어질지, 아니면 일시적 조정에 그칠지 판단이 중요

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "코스피가 최근 5일간 크게 하락하며 외국인 매도세가 강하게 나타남.",
    "미국 증시는 견조하나 국내 시장은 변동성 확대와 위험회피 심리가 우세함."
  ],
  "korean_comment": "국내 증시는 외국인 이탈과 변동성 증가로 신중한 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.note",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market)",
  "core_claims": [
    "외국인은 KOSPI에서 대규모 순매도, 이는 고금리/연준, 반도체/AI, 환율 안정(USD/KRW 하락) 키워드와 연관.",
    "외국인 매도는 환율 상승이 아닌, 미국 금리 급등 및 글로벌 반도체/AI 관련 차익실현 성격이 강함.",
    "개인 매수는 KOSPI 급락에 따른 저가매수 시도로 보이나, 최근 5일간 누적 하락세와 변동성 확대를 감안하면 지속성은 낮음."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안정 지속.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.macro.daily.us10y",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.vix_5d_avg"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 최근 5일간 -3.7% 하락하며 단기 약세가 뚜렷하다.",
    "외국인과 기관의 대규모 순매도세가 지속되고 있다.",
    "20일 누적으로는 상승세이나 단기 변동성 확대에 주의 필요하다."
  ],
  "korean_comment": "단기적으로 시장에 하방 압력이 강하게 작용하고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
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
    "코스피 단기 급락이 있었으나 20일 누적 상승세 유지",
    "외국인 대규모 순매도와 변동성 확대 신호",
    "환율 안정과 미국 증시 강세로 과도한 공포는 아님"
  ],
  "korean_comment": "단기 충격이 크지만 누적 흐름은 아직 위험 전환 신호 부족합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.markets.us.sp500_pct",
    "snapshot.markets.volatility.vix",
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
    "실적 모멘텀 약화 신호가 뚜렷함",
    "외국인 대규모 순매도와 코스피 5일 누적 하락이 지속적 부담",
    "단기 반등 기대감은 있으나 실적 추세 개선 신호는 부재"
  ],
  "korean_comment": "실적 추세가 단기적으로 더 약화될 가능성이 높아 보입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI 5일 누적 하락과 시장 내 확산 약화가 뚜렷하다.",
    "외국인·기관 동반 매도세로 시장 내부 체력이 저하되었다."
  ],
  "korean_comment": "시장 확산 약화와 매도세가 뚜렷하게 나타난 구간입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "외국인 대규모 순매도와 코스피 급락으로 유동성 악화 신호.",
    "환율 하락에도 불구하고 변동성 상승과 외국인 이탈이 위험회피 심리 강화.",
    "정책 및 금리 불확실성으로 보수적 유동성 환경 지속."
  ],
  "korean_comment": "유동성 경색과 외국인 이탈로 위험회피 국면이 강화되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y"
  ],
  "confidence": "HIGH"
}
```