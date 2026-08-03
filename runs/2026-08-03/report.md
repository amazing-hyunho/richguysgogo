# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-08-03**
- 생성 시각(UTC): `2026-08-03T00:52:31.229096+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -3.99% / KOSDAQ +1.93%
- **미국 지수**: S&P500 +0.70% / NASDAQ +1.00% / DOW +0.53%
- **환율/변동성**: USD/KRW 1438.20 (-0.26%) / VIX 16.0
- **시장 요약 노트**: KOSPI -3.99%, USD/KRW 1438.20. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -13528억 / 기관 -5630억 / 개인 +18718억
- **일간 매크로**: 미10년 4.74% / 미2년 3.68% / 2-10 1.06%p / DXY 99.48
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.73% / Core CPI YoY 2.81% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.46%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI가 6332.28p로 -3.99% 급락, 20일 누적 -26.47%로 약세장 심화.
  ↳ 출처: `CORE_SIGNALS, macro_daily`
- 외국인 -13528억, 기관 -5630억 순매도, 개인 +18718억 저가매수 유입에도 수급 불안 지속.
  ↳ 출처: `CORE_SIGNALS, flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 국내 증시는 약세 흐름이 뚜렷하며, 추가 변동성에 유의해야 합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 크게 하락하며 약세장이 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.
- 핵심 주장: 거시환경 불확실성이 높아 보수적 접근이 필요합니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안 지속.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인 대규모 순매도는 고금리/연준, 고환율, 반도체/AI 불확실성 등 복합적 리스크에 따른 포트폴리오 리밸런싱 및 환차손 방어 목적이 주도.
- 핵심 주장: 개인 대규모 순매수는 최근 급락(-26%/20일) 이후 저가매수 성격이나, 펀더멘털보다는 단기 반등 기대 심리가 강해 지속성은 낮음.
- 핵심 주장: 국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 시장 기준으로 해석 한계.

### 섹터 담당자
- 한줄 요약: 시장 전반에 걸쳐 투자심리가 매우 위축된 상황입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI는 최근 20일간 -26% 이상 급락하며 약세장이 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.
- 핵심 주장: 반등 신호 없이 변동성만 높은 위험 회피 국면입니다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 구조적 약세가 뚜렷합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큼
- 핵심 주장: 외국인 대규모 순매도 지속
- 핵심 주장: 단기 반전 신호는 없음

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 하향 압력이 지속되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI의 20일 누적 급락은 실적 모멘텀 약화 신호입니다.
- 핵심 주장: 외국인 대규모 순매도는 실적 전망 하향을 반영합니다.

### 브레드스 담당자
- 한줄 요약: 시장 내부 확산 약화와 누적 하락세가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI의 20일 누적 하락폭이 매우 크고, 시장 확산도 약화가 뚜렷하다.
- 핵심 주장: 외국인과 기관의 대규모 순매도, 시장 내부 확산 신호도 부정적이다.
- 핵심 주장: 단기 반전 신호는 없으며, 시장 전반에 위험회피 심리가 강하다.

### 유동성 담당자
- 한줄 요약: 유동성 및 정책 환경이 위험 회피 국면임을 명확히 보여줍니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 크고 외국인 자금 유출이 심각하다.
- 핵심 주장: 정책 및 환율 환경이 불안정하며, 유동성 신호도 위험 회피를 시사한다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '국내 증시는 약세 흐름이 뚜렷하며, 추가 변동성에 유의해야 합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-13528억, institution_net=-5630억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.news_headlines, snapshot.cumulative_context.note
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안 지속.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-3.99%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.macro.daily.us10y, snapshot.macro.daily.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반에 걸쳐 투자심리가 매우 위축된 상황입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-13528억, institution_net=-5630억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.market_summary.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 구조적 약세가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-13528억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.note, snapshot.cumulative_context.kospi_5d_cum_pct
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 하향 압력이 지속되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-13528억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 내부 확산 약화와 누적 하락세가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-13528억, institution_net=-5630억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 및 정책 환경이 위험 회피 국면임을 명확히 보여줍니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-13528억, usdkrw=1438.20입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.usdkrw, snapshot.macro.daily.dxy, snapshot.phase_two_signals.liquidity_signal_score, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.note
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -3.99%, USD/KRW 1438.20(-0.26%), VIX 16.0, 외국인 -13528억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 구조적 약세 해석: 다수=RISK_OFF: 약세장 지속, 변동성 완화 전까지 방어적 접근 필요, 소수=RISK_ON: 구조적 약세는 맞으나, 일부 단기 반전 가능성도 배제할 수 없음, 에이전트=[risk]
  - 의미: 단기 반전 신호 부재에도 불구하고, 극단적 하락 후 기술적 반등 가능성에 대한 소수 의견 존재

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO",
  "core_claims": [
    "KOSPI가 최근 20일간 크게 하락하며 약세장이 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.",
    "거시환경 불확실성이 높아 보수적 접근이 필요합니다."
  ],
  "korean_comment": "국내 증시는 약세 흐름이 뚜렷하며, 추가 변동성에 유의해야 합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market)",
  "core_claims": [
    "외국인 대규모 순매도는 고금리/연준, 고환율, 반도체/AI 불확실성 등 복합적 리스크에 따른 포트폴리오 리밸런싱 및 환차손 방어 목적이 주도.",
    "개인 대규모 순매수는 최근 급락(-26%/20일) 이후 저가매수 성격이나, 펀더멘털보다는 단기 반등 기대 심리가 강해 지속성은 낮음.",
    "국내 변동성 직접 판단 제한적 (VKOSPI 미제공), VIX는 미국 시장 기준으로 해석 한계."
  ],
  "korean_comment": "외국인 매도 우위, 개인 저가매수 흡수 구간이나 수급 불안 지속.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 최근 20일간 -26% 이상 급락하며 약세장이 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.",
    "반등 신호 없이 변동성만 높은 위험 회피 국면입니다."
  ],
  "korean_comment": "시장 전반에 걸쳐 투자심리가 매우 위축된 상황입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
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
    "KOSPI 20일 누적 하락폭이 매우 큼",
    "외국인 대규모 순매도 지속",
    "단기 반전 신호는 없음"
  ],
  "korean_comment": "시장 전반에 구조적 약세가 뚜렷합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.market_summary.note",
    "snapshot.cumulative_context.kospi_5d_cum_pct"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI의 20일 누적 급락은 실적 모멘텀 약화 신호입니다.",
    "외국인 대규모 순매도는 실적 전망 하향을 반영합니다."
  ],
  "korean_comment": "실적 추정치 하향 압력이 지속되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI의 20일 누적 하락폭이 매우 크고, 시장 확산도 약화가 뚜렷하다.",
    "외국인과 기관의 대규모 순매도, 시장 내부 확산 신호도 부정적이다.",
    "단기 반전 신호는 없으며, 시장 전반에 위험회피 심리가 강하다."
  ],
  "korean_comment": "시장 내부 확산 약화와 누적 하락세가 뚜렷합니다.",
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
    "KOSPI 20일 누적 하락폭이 매우 크고 외국인 자금 유출이 심각하다.",
    "정책 및 환율 환경이 불안정하며, 유동성 신호도 위험 회피를 시사한다."
  ],
  "korean_comment": "유동성 및 정책 환경이 위험 회피 국면임을 명확히 보여줍니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.usdkrw",
    "snapshot.macro.daily.dxy",
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```