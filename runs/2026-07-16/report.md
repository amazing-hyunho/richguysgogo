# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-16**
- 생성 시각(UTC): `2026-07-16T00:52:37.476002+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -6.14% / KOSDAQ -3.83%
- **미국 지수**: S&P500 +0.38% / NASDAQ +0.62% / DOW +0.29%
- **환율/변동성**: USD/KRW 1490.48 (-0.02%) / VIX 15.7
- **시장 요약 노트**: KOSPI -6.14%, USD/KRW 1490.48. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -8359억 / 기관 -4401억 / 개인 +12511억
- **일간 매크로**: 미10년 4.55% / 미2년 3.69% / 2-10 0.86%p / DXY 100.47
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.73% / Core CPI YoY 2.81% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.32%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 -6.14% 급락(6823.34p), KOSDAQ도 -3.83% 하락(798.2p)하며 20일 누적 -25.65%로 구조적 약세가 지속되고 있습니다.
  ↳ 출처: `macro_daily, flow_data`
- 외국인 -8359억, 기관 -4401억 순매도, 개인 +12511억 순매수로 수급은 위험회피 성격이 뚜렷합니다.
  ↳ 출처: `flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 시장 전반에 위험회피 심리가 강하게 나타나고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI의 최근 20일 누적 하락폭이 매우 큽니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 지속되고 있습니다.
- 핵심 주장: 금리 인상 등 긴축 기조가 시장에 부담을 주고 있습니다.

### 수급 담당자
- 한줄 요약: 외국인 환율·금리 리스크 회피 매도, 개인 저가매수 흡수 구간.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고금리/긴축(금리/연준), 고환율(환율/달러), 인플레이션 우려가 복합적으로 작용한 결과입니다.
- 핵심 주장: KOSPI 20일 누적 -25%대 급락과 동반된 외국인 매도는 FX-driven outflow(고환율 연동) 성격이 강하며, 단순 차익실현이나 리밸런싱보다 환율·정책 리스크가 주도적입니다.
- 핵심 주장: 개인 매수세는 대형주 중심 저가매수 시도로 보이나, 최근 변동성 확대와 누적 하락폭을 감안할 때 지속성은 제한적입니다. 국내 변동성 직접 판단 제한적 (VKOSPI 미제공).

### 섹터 담당자
- 한줄 요약: 시장 전반에 뚜렷한 위험 회피 심리가 감지됩니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 -25% 이상 급락하며 약세가 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.
- 핵심 주장: 금리 인상과 고물가 우려가 시장 전반에 부정적 영향을 주고 있습니다.

### 리스크 담당자
- 한줄 요약: 국내 증시의 구조적 하락세가 뚜렷합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 -25% 이상 급락
- 핵심 주장: 외국인·기관 대규모 순매도 지속
- 핵심 주장: 단기 반등 신호 부재

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀 약화가 단기 이슈를 넘어 지속될 수 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI의 20일 누적 급락은 실적 모멘텀 약화 신호.
- 핵심 주장: 외국인 대규모 순매도는 실적 전망 하향 압력.
- 핵심 주장: 실적 추정치 및 가이던스 하향 가능성 높음.

### 브레드스 담당자
- 한줄 요약: 시장 전반의 하락세와 확산 약화가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피 20일 누적 하락폭이 매우 크고, 시장 내부 확산도 약화됨.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 지속되고 있음.
- 핵심 주장: 단기 반등 신호는 없으며, 시장 전반에 위험회피 심리가 강함.

### 유동성 담당자
- 한줄 요약: 유동성 악화와 정책 긴축으로 위험회피 심리가 강합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 외국인 대규모 순매도는 유동성 악화 신호입니다.
- 핵심 주장: 기준금리 인상과 긴축 기조가 정책 리스크를 높이고 있습니다.
- 핵심 주장: 환율은 안정적이나, 변동성은 여전히 경계가 필요합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '시장 전반에 위험회피 심리가 강하게 나타나고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8359억, institution_net=-4401억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.news_headlines, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 환율·금리 리스크 회피 매도, 개인 저가매수 흡수 구간.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-6.14%, usdkrw=1490.48입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 뚜렷한 위험 회피 심리가 감지됩니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.news_headlines, snapshot.market_summary.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '국내 증시의 구조적 하락세가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8359억, institution_net=-4401억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.note, snapshot.news_headlines
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀 약화가 단기 이슈를 넘어 지속될 수 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8359억, kospi_change_pct=-6.14%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.news_headlines, snapshot.phase_two_signals.earnings_signal_score
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 하락세와 확산 약화가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8359억, institution_net=-4401억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 악화와 정책 긴축으로 위험회피 심리가 강합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-8359억, usdkrw=1490.48입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.news_headlines, snapshot.macro.structural.fed_funds_rate, snapshot.market_summary.usdkrw, snapshot.cumulative_context.vix_5d_avg
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -6.14%, USD/KRW 1490.48(-0.02%), VIX 15.7, 외국인 -8359억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 구조적 하락 vs. 단기 반등 가능성: 다수=구조적 하락세 지속, 단기 반등 신호 부재(Risk-off), 소수=일부(리스크 담당자)는 구조적 하락임을 인정하나, 내부 태그는 Risk-on으로 표기, 에이전트=[risk]
  - 의미: 단기 반등 신호가 없다는 점은 대다수 의견과 일치하나, 리스크 담당자의 태그 표기는 해석상 혼선을 줄 수 있음

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI의 최근 20일 누적 하락폭이 매우 큽니다.",
    "외국인과 기관의 대규모 순매도세가 지속되고 있습니다.",
    "금리 인상 등 긴축 기조가 시장에 부담을 주고 있습니다."
  ],
  "korean_comment": "시장 전반에 위험회피 심리가 강하게 나타나고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.news_headlines",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW Pre-Analysis Agent (Korean Market)",
  "core_claims": [
    "외국인 대규모 순매도는 고금리/긴축(금리/연준), 고환율(환율/달러), 인플레이션 우려가 복합적으로 작용한 결과입니다.",
    "KOSPI 20일 누적 -25%대 급락과 동반된 외국인 매도는 FX-driven outflow(고환율 연동) 성격이 강하며, 단순 차익실현이나 리밸런싱보다 환율·정책 리스크가 주도적입니다.",
    "개인 매수세는 대형주 중심 저가매수 시도로 보이나, 최근 변동성 확대와 누적 하락폭을 감안할 때 지속성은 제한적입니다. 국내 변동성 직접 판단 제한적 (VKOSPI 미제공)."
  ],
  "korean_comment": "외국인 환율·금리 리스크 회피 매도, 개인 저가매수 흡수 구간.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.macro.daily.dxy",
    "snapshot.macro.structural.fed_funds_rate"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 최근 20일간 -25% 이상 급락하며 약세가 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.",
    "금리 인상과 고물가 우려가 시장 전반에 부정적 영향을 주고 있습니다."
  ],
  "korean_comment": "시장 전반에 뚜렷한 위험 회피 심리가 감지됩니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.news_headlines",
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
    "KOSPI 20일 누적 -25% 이상 급락",
    "외국인·기관 대규모 순매도 지속",
    "단기 반등 신호 부재"
  ],
  "korean_comment": "국내 증시의 구조적 하락세가 뚜렷합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.market_summary.note",
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
    "KOSPI의 20일 누적 급락은 실적 모멘텀 약화 신호.",
    "외국인 대규모 순매도는 실적 전망 하향 압력.",
    "실적 추정치 및 가이던스 하향 가능성 높음."
  ],
  "korean_comment": "실적 모멘텀 약화가 단기 이슈를 넘어 지속될 수 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.news_headlines",
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
    "코스피 20일 누적 하락폭이 매우 크고, 시장 내부 확산도 약화됨.",
    "외국인과 기관의 대규모 순매도세가 지속되고 있음.",
    "단기 반등 신호는 없으며, 시장 전반에 위험회피 심리가 강함."
  ],
  "korean_comment": "시장 전반의 하락세와 확산 약화가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
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
    "KOSPI 20일 누적 급락과 외국인 대규모 순매도는 유동성 악화 신호입니다.",
    "기준금리 인상과 긴축 기조가 정책 리스크를 높이고 있습니다.",
    "환율은 안정적이나, 변동성은 여전히 경계가 필요합니다."
  ],
  "korean_comment": "유동성 악화와 정책 긴축으로 위험회피 심리가 강합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.news_headlines",
    "snapshot.macro.structural.fed_funds_rate",
    "snapshot.market_summary.usdkrw",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```