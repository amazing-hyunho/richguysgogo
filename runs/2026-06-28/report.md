# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-06-28**
- 생성 시각(UTC): `2026-06-28T00:53:20.985480+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -5.81% / KOSDAQ -4.10%
- **미국 지수**: S&P500 -0.05% / NASDAQ -0.24% / DOW -0.09%
- **환율/변동성**: USD/KRW 1536.48 (-0.61%) / VIX 18.4
- **시장 요약 노트**: KOSPI -5.81%, USD/KRW 1536.48. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -39396억 / 기관 -38140억 / 개인 +75231억
- **일간 매크로**: 미10년 4.37% / 미2년 3.66% / 2-10 0.71%p / DXY 101.36
- **월간 매크로**: 실업률 4.30% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.17%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI -5.81%, KOSDAQ -4.10% 급락과 외국인 -3.9조, 기관 -3.8조 순매도 등 수급 불균형이 극심하게 전개됨.
  ↳ 출처: `flow_data, macro_daily`
- USD/KRW 1536.48로 강달러 지속, 변동성(VIX) 18.4로 위험회피 심리 강화.
  ↳ 출처: `macro_daily, news`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ이 최근 5일간 큰 폭으로 하락했습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도가 지속되고 있습니다.
- 핵심 주장: 환율과 변동성 지표도 불안정한 모습을 보이고 있습니다.

### 수급 담당자
- 한줄 요약: 외국인 매도와 개인 추격매수로 수급 불균형이 극심하게 나타난 하루.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 매도는 고환율(USD/KRW), 연준/금리, 반도체/AI 불확실성 등 복합적 요인에 기인.
- 핵심 주장: KOSPI 중심 외국인 매도세는 FX-driven 성격이 강하며, 단기 포트폴리오 리밸런싱과 이익실현도 일부 혼재.
- 핵심 주장: 개인 대규모 순매수는 레버리지 추격매수 성격이 강해 지속성에 의문, 수급 불균형 심화.

### 섹터 담당자
- 한줄 요약: 시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ이 최근 5일간 급락하며 투자심리가 크게 위축됨.
- 핵심 주장: 외국인과 기관의 대규모 순매도, 강달러 및 연준 긴축 전망이 시장에 부담.
- 핵심 주장: 단기 반등 신호는 없으며, 변동성도 높은 상태가 지속됨.

### 리스크 담당자
- 한줄 요약: 시장 전반에 걸쳐 구조적 위험이 뚜렷하게 나타나고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ이 단기간에 큰 폭으로 하락함
- 핵심 주장: 외국인과 기관의 대규모 순매도 지속
- 핵심 주장: 누적 하락폭이 단기 노이즈를 넘어 구조적 위험 신호

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀 약화가 단기적이 아닌 구조적으로 이어질 가능성이 높습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 급락과 외국인 대규모 순매도는 실적 모멘텀 약화 신호.
- 핵심 주장: 실적 추정치 하향 압력 지속, 단기 반등 신호 없음.
- 핵심 주장: 환율 불안과 실적 불확실성으로 가이던스도 보수적 전환.

### 브레드스 담당자
- 한줄 요약: 시장 내부 확산 약화와 하락세가 매우 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 시장 전반에 걸친 급격한 하락과 확산이 뚜렷하다.
- 핵심 주장: 수급과 변동성, 누적 하락폭 모두 위험 신호를 보인다.
- 핵심 주장: 단기 반전 신호는 아직 감지되지 않는다.

### 유동성 담당자
- 한줄 요약: 정책 및 유동성 환경이 위험회피로 전환되었습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 단기 급락과 외국인 대규모 순매도 발생.
- 핵심 주장: 환율은 1536원대 강달러 유지, 정책 불확실성 지속.
- 핵심 주장: 변동성(VIX)도 높고, 유동성 신호는 악화됨.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-5.81%, vix=18.4입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.note, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.markets.fx.usdkrw, snapshot.markets.volatility.vix, snapshot.news_headlines
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도와 개인 추격매수로 수급 불균형이 극심하게 나타난 하루.' 의견을 유지합니다. 근거 숫자는 dxy=101.36입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.note, snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.news_headlines, snapshot.macro.daily.usdkrw, snapshot.macro.daily.dxy, snapshot.macro.daily.us10y, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.note, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 걸쳐 구조적 위험이 뚜렷하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-5.81%, foreign_net=-39396억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.note, snapshot.news_headlines
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀 약화가 단기적이 아닌 구조적으로 이어질 가능성이 높습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-39396억, usdkrw=1536.48입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.news_headlines, snapshot.market_summary.usdkrw, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 내부 확산 약화와 하락세가 매우 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-39396억, institution_net=-38140억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.flow_summary.retail_net
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 및 유동성 환경이 위험회피로 전환되었습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-5.81%, foreign_net=-39396억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.markets.volatility.vix, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -5.81%, USD/KRW 1536.48(-0.61%), VIX 18.4, 외국인 -39396억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 구조적 위험 해석: 다수=단기 급락 및 수급 불균형에 기반한 위험회피(Risk-off) 국면 진단, 소수=구조적 위험 신호가 이미 뚜렷하게 나타나며, 단순 단기 노이즈가 아님, 에이전트=[risk]
  - 의미: 구조적 위험이 현실화될 경우 단기 반등 기대는 무의미해지고, 추가 하락 위험이 커짐

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI와 KOSDAQ이 최근 5일간 큰 폭으로 하락했습니다.",
    "외국인과 기관의 대규모 순매도가 지속되고 있습니다.",
    "환율과 변동성 지표도 불안정한 모습을 보이고 있습니다."
  ],
  "korean_comment": "시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.markets.fx.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW Pre-Analysis Agent (Korean Market)",
  "core_claims": [
    "외국인 대규모 매도는 고환율(USD/KRW), 연준/금리, 반도체/AI 불확실성 등 복합적 요인에 기인.",
    "KOSPI 중심 외국인 매도세는 FX-driven 성격이 강하며, 단기 포트폴리오 리밸런싱과 이익실현도 일부 혼재.",
    "개인 대규모 순매수는 레버리지 추격매수 성격이 강해 지속성에 의문, 수급 불균형 심화."
  ],
  "korean_comment": "외국인 매도와 개인 추격매수로 수급 불균형이 극심하게 나타난 하루.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.note",
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.news_headlines",
    "snapshot.macro.daily.usdkrw",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.daily.us10y",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
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
    "KOSPI와 KOSDAQ이 최근 5일간 급락하며 투자심리가 크게 위축됨.",
    "외국인과 기관의 대규모 순매도, 강달러 및 연준 긴축 전망이 시장에 부담.",
    "단기 반등 신호는 없으며, 변동성도 높은 상태가 지속됨."
  ],
  "korean_comment": "시장 전반에 걸쳐 위험회피 심리가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.note",
    "snapshot.flow_summary.note",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI와 KOSDAQ이 단기간에 큰 폭으로 하락함",
    "외국인과 기관의 대규모 순매도 지속",
    "누적 하락폭이 단기 노이즈를 넘어 구조적 위험 신호"
  ],
  "korean_comment": "시장 전반에 걸쳐 구조적 위험이 뚜렷하게 나타나고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.note",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 5일 누적 급락과 외국인 대규모 순매도는 실적 모멘텀 약화 신호.",
    "실적 추정치 하향 압력 지속, 단기 반등 신호 없음.",
    "환율 불안과 실적 불확실성으로 가이던스도 보수적 전환."
  ],
  "korean_comment": "실적 모멘텀 약화가 단기적이 아닌 구조적으로 이어질 가능성이 높습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines",
    "snapshot.market_summary.usdkrw",
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
    "시장 전반에 걸친 급격한 하락과 확산이 뚜렷하다.",
    "수급과 변동성, 누적 하락폭 모두 위험 신호를 보인다.",
    "단기 반전 신호는 아직 감지되지 않는다."
  ],
  "korean_comment": "시장 내부 확산 약화와 하락세가 매우 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.flow_summary.retail_net",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "KOSPI와 KOSDAQ 모두 단기 급락과 외국인 대규모 순매도 발생.",
    "환율은 1536원대 강달러 유지, 정책 불확실성 지속.",
    "변동성(VIX)도 높고, 유동성 신호는 악화됨."
  ],
  "korean_comment": "정책 및 유동성 환경이 위험회피로 전환되었습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```