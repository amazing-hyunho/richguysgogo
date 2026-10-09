# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-09**
- 생성 시각(UTC): `2026-10-09T00:52:30.658701+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=0, RISK_ON=1, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -2.62% / KOSDAQ -0.69%
- **미국 지수**: S&P500 -0.47% / NASDAQ -1.25% / DOW +0.10%
- **환율/변동성**: USD/KRW 1342.34 (+0.16%) / VIX 15.4
- **시장 요약 노트**: KOSPI -2.62%, USD/KRW 1342.34. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -20079억 / 기관 -17864억 / 개인 +30455억
- **일간 매크로**: 미10년 5.23% / 미2년 4.04% / 2-10 1.19%p / DXY 102.11
- **월간 매크로**: 실업률 4.20% / CPI YoY 3.71% / Core CPI YoY 2.76% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.20% / 기준금리 3.75% / 실질금리 2.88%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 6,625.93(-2.62%)로 하락했고 외국인 -20,079억원, 기관 -17,864억원의 동반 순매도가 개인 +30,455억원 매수보다 방향성을 주도했습니다.
  ↳ 출처: `market_data, flow_data`
- KOSPI 5일 -7.651%, 20일 -5.224%이며 반전 신호도 없어 하루 충격보다 누적 약세로 해석해야 합니다.
  ↳ 출처: `cumulative_context, market_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 중기 지표와 단기 시장 신호가 상충하며, 보수적 해석이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: KOSPI는 최근 5~20일간 약세가 지속되며 단기 반등 신호는 확인되지 않습니다.
- 핵심 주장: 한국 월별 지표는 심리·고용·수출은 긍정적이나 생산·소비는 부진하여 경기 방향성은 혼조입니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도 등 수급도 단기적으로 부담 요인입니다.

### 수급 담당자
- 한줄 요약: 외국인 매도 우위, 개인이 하락분을 단기 흡수하는 공급우위 약세장.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 외국인은 KOSPI에서 대규모 순매도, 이는 금리/연준, 반도체/AI, 고유가 등 대외 불확실성(핵심 키워드)과 연동된 위험회피 성향이 주도.
- 핵심 주장: USD/KRW 상승과 외국인 매도 동반, FX-driven 유출이 주요 원인으로 판단.
- 핵심 주장: 개인은 대규모 매수로 하락분을 흡수했으나, 최근 5일간 KOSPI -7.7% 누적 하락을 감안하면 레버리지 추격매수 가능성 높음, 지속성은 낮음.

### 섹터 담당자
- 한줄 요약: 수급과 누적 하락세 모두 시장에 부정적입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 5일간 -7.65% 급락하며 약세가 지속되고 있습니다.
- 핵심 주장: 외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.
- 핵심 주장: 중기적으로도 시장 반전 신호는 아직 감지되지 않습니다.

### 리스크 담당자
- 한줄 요약: 단기 수급 악화와 누적 약세가 확인됩니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락폭이 크고 외국인·기관 대규모 순매도
- 핵심 주장: 중기적으로도 KOSPI 20일 누적 약세 지속
- 핵심 주장: 시장 변동성(VIX)과 환율은 안정적이나, 단기 수급 악화가 뚜렷

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 하향 압력이 시장에 반영되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 하락세로 실적 모멘텀 약화 신호.
- 핵심 주장: 외국인·기관 동반 순매도, 실적 전망 하향 압력 지속.
- 핵심 주장: 단기 급락이 아닌 중기적 실적 우려가 반영되는 구간.

### 브레드스 담당자
- 한줄 요약: 시장 전반의 하락 압력이 지속되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 하락폭이 크고, 20일 누적도 약세다.
- 핵심 주장: 수급은 외국인·기관 동반 매도, 시장 내 확산 약화 신호.
- 핵심 주장: 단기 반전 신호는 아직 감지되지 않는다.

### 유동성 담당자
- 한줄 요약: 유동성 악화와 외국인 이탈로 보수적 대응이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 5일 누적 급락과 외국인 대규모 순매도 지속
- 핵심 주장: 달러/원 환율 상승세, 유동성 위축 신호
- 핵심 주장: 정책 불확실성 및 금리 우려로 위험회피 심화

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '중기 지표와 단기 시장 신호가 상충하며, 보수적 해석이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.reversal_signal, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 매도 우위, 개인이 하락분을 단기 흡수하는 공급우위 약세장.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=-2.62%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.macro.daily.us10y, snapshot.macro.daily.oil_wti, snapshot.news_headlines, snapshot.cumulative_context.kospi_5d_cum_pct
- [섹터 담당자] 저는 섹터 담당자 입장에서 '수급과 누적 하락세 모두 시장에 부정적입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.cumulative_context.reversal_signal
- [리스크 담당자] 저는 리스크 담당자 입장에서 '단기 수급 악화와 누적 약세가 확인됩니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.flow_summary.note, snapshot.markets.kr.kospi_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.vix_5d_avg
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 하향 압력이 시장에 반영되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.earnings_signal_score, snapshot.market_summary.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 하락 압력이 지속되고 있습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, institution_net=-17864억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.phase_two_signals.breadth_signal_score
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 악화와 외국인 이탈로 보수적 대응이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-20079억, kospi_change_pct=-2.62%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.market_summary.kospi_change_pct, snapshot.news_headlines, snapshot.macro.daily.us10y, snapshot.macro.daily.dxy
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 오프입니다. 근거는 KOSPI -2.62%, USD/KRW 1342.34(+0.16%), VIX 15.4, 외국인 -20079억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다.

## 7) 이견 사항
- 시장 국면 분류: 다수=매크로·수급·섹터·이익·브레드스·유동성 담당자는 누적 약세와 동반 순매도를 근거로 리스크 오프를 제시했습니다., 소수=리스크 담당자의 내부 태그는 리스크 온이지만, 실제 주장은 단기 수급 악화와 누적 약세 확인으로 다수 의견과 유사합니다., 에이전트=[risk]
  - 의미: 분류 태그보다 실제 근거를 우선해야 하며, VIX와 환율이 패닉을 확인하지 않는다는 점 때문에 약세 판단의 확신은 낮춰야 합니다.
- 국내 경기와 일일 시장의 방향: 다수=일일 시장에서는 외국인·기관 매도와 KOSPI 급락이 우세해 방어적 대응이 필요하다는 의견입니다., 소수=매크로 담당자는 9월 심리 개선과 8월 고용·수출의 긍정 신호를 들어 중기 지표와 단기 시장 신호가 상충한다고 봤습니다., 에이전트=[macro]
  - 의미: 월별 경제지표를 당일 반등 신호로 오인해서는 안 되지만, 실물 회복이 확인되면 현재의 수급 약세가 장기 추세로 고착될 가능성은 낮아질 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI는 최근 5~20일간 약세가 지속되며 단기 반등 신호는 확인되지 않습니다.",
    "한국 월별 지표는 심리·고용·수출은 긍정적이나 생산·소비는 부진하여 경기 방향성은 혼조입니다.",
    "외국인과 기관의 대규모 순매도 등 수급도 단기적으로 부담 요인입니다."
  ],
  "korean_comment": "중기 지표와 단기 시장 신호가 상충하며, 보수적 해석이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW Pre-Analysis Agent (Korean Market)",
  "core_claims": [
    "외국인은 KOSPI에서 대규모 순매도, 이는 금리/연준, 반도체/AI, 고유가 등 대외 불확실성(핵심 키워드)과 연동된 위험회피 성향이 주도.",
    "USD/KRW 상승과 외국인 매도 동반, FX-driven 유출이 주요 원인으로 판단.",
    "개인은 대규모 매수로 하락분을 흡수했으나, 최근 5일간 KOSPI -7.7% 누적 하락을 감안하면 레버리지 추격매수 가능성 높음, 지속성은 낮음."
  ],
  "korean_comment": "외국인 매도 우위, 개인이 하락분을 단기 흡수하는 공급우위 약세장.",
  "regime_tag": "RISK_OFF",
  "confidence": "HIGH",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.oil_wti",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg"
  ]
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 최근 5일간 -7.65% 급락하며 약세가 지속되고 있습니다.",
    "외국인과 기관의 대규모 순매도세가 뚜렷하게 나타나고 있습니다.",
    "중기적으로도 시장 반전 신호는 아직 감지되지 않습니다."
  ],
  "korean_comment": "수급과 누적 하락세 모두 시장에 부정적입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
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
    "KOSPI 5일 누적 하락폭이 크고 외국인·기관 대규모 순매도",
    "중기적으로도 KOSPI 20일 누적 약세 지속",
    "시장 변동성(VIX)과 환율은 안정적이나, 단기 수급 악화가 뚜렷"
  ],
  "korean_comment": "단기 수급 악화와 누적 약세가 확인됩니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.flow_summary.note",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "KOSPI 20일 누적 하락세로 실적 모멘텀 약화 신호.",
    "외국인·기관 동반 순매도, 실적 전망 하향 압력 지속.",
    "단기 급락이 아닌 중기적 실적 우려가 반영되는 구간."
  ],
  "korean_comment": "실적 추정치 하향 압력이 시장에 반영되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.phase_two_signals.earnings_signal_score",
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
    "KOSPI 5일 누적 하락폭이 크고, 20일 누적도 약세다.",
    "수급은 외국인·기관 동반 매도, 시장 내 확산 약화 신호.",
    "단기 반전 신호는 아직 감지되지 않는다."
  ],
  "korean_comment": "시장 전반의 하락 압력이 지속되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
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
    "KOSPI 5일 누적 급락과 외국인 대규모 순매도 지속",
    "달러/원 환율 상승세, 유동성 위축 신호",
    "정책 불확실성 및 금리 우려로 위험회피 심화"
  ],
  "korean_comment": "유동성 악화와 외국인 이탈로 보수적 대응이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy"
  ],
  "confidence": "HIGH"
}
```