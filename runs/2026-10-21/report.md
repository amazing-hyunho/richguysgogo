# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-10-21**
- 생성 시각(UTC): `2026-10-21T00:52:22.522768+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=4, RISK_ON=0, RISK_OFF=3
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +2.94% / KOSDAQ +1.48%
- **미국 지수**: S&P500 +0.28% / NASDAQ -0.02% / DOW +1.02%
- **환율/변동성**: USD/KRW 1327.17 (-0.15%) / VIX 17.3
- **시장 요약 노트**: KOSPI 2.94%, USD/KRW 1327.17. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 +1286억 / 기관 +973억 / 개인 -4120억
- **일간 매크로**: 미10년 5.12% / 미2년 4.08% / 2-10 1.04%p / DXY 101.78
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.02% / Core CPI YoY 2.79% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.20% / 기준금리 3.75% / 실질금리 2.77%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `regime_tuner`
- KOSPI는 5,716.02로 2.94% 상승했고 외국인과 기관이 각각 1,286억원, 973억원 순매수했다. 다만 20일 누적 수익률은 -21.879%로 반등을 추세 전환으로 단정하기 어렵다.
  ↳ 출처: `flow_data, market_data, cumulative_context`
- USD/KRW는 1,327.17원으로 0.15% 하락해 KOSPI 수급에는 우호적이었으나, KOSDAQ에서는 외국인이 664억원 순매도해 위험선호의 전면적 회복으로 보기는 이르다.
  ↳ 출처: `flow_data, macro_daily`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 월별 지표와 단기 반등 신호가 상충하여 확신은 어렵습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기 급등했으나 20일 누적 하락폭이 매우 커 중기 약세 국면이 지속 중입니다.
- 핵심 주장: 한국 월별 지표는 심리·고용·수출은 긍정이나 생산·소비는 부진하여 경기 방향성에 불확실성이 큽니다.
- 핵심 주장: 외국인 순매수와 환율 안정에도 불구하고, 최근 변동성 및 누적 하락을 감안하면 신중한 접근이 필요합니다.

### 수급 담당자
- 한줄 요약: 외국인 저점 매수와 환율 안정이 KOSPI 중심으로 수급 개선을 이끌었습니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: 외국인 순매수는 KOSPI에 집중되었으며, 고환율 안정(USD/KRW 하락)과 반도체/AI 기대감이 주요 배경입니다.
- 핵심 주장: 최근 20일간 KOSPI 급락(-21.88%) 이후 저점 반발 매수 성격이 강하며, 외국인 유입은 FX 안정과 연준/금리 불확실성 완화에 따른 포지션 조정으로 해석됩니다.
- 핵심 주장: 개인 매수는 KOSDAQ에서만 소폭 유입, KOSPI에서는 대규모 이탈로, 레버리지 추격매수보다는 손실 확정 및 수급 부담 완화 국면입니다.

### 섹터 담당자
- 한줄 요약: 단기 반등에도 중기 약세 신호가 우세합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI는 단기 반등에도 불구하고 20일 누적 하락폭이 매우 큽니다.
- 핵심 주장: 외국인·기관 순매수 유입이 긍정적이나, 중기적 약세 흐름이 뚜렷합니다.
- 핵심 주장: 심리지표는 개선됐으나 생산·소비 지표는 부진합니다.

### 리스크 담당자
- 한줄 요약: 중기 약세 흐름이 지속되나 단기 반등과 수급 개선 신호가 혼재합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI 20일 누적 하락폭이 매우 큼
- 핵심 주장: 생산·소비 지표는 부정적이나 심리·수출·고용은 긍정적
- 핵심 주장: 외국인·기관 순매수와 단기 반등세 확인

### 이익모멘텀 담당자
- 한줄 요약: 실적 추세 개선 신호가 명확하지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 신호는 부재하며, 추세 반전 조짐 없음
- 핵심 주장: 단기 반등에도 중기 실적 전망 하향 압력 지속

### 브레드스 담당자
- 한줄 요약: 지수 반등에도 하락 추세가 뚜렷합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 단기 반등에도 중기 하락세 지속
- 핵심 주장: 수급 개선 불구, 시장 확산력은 제한적
- 핵심 주장: 지수 변동성 높고 확실한 반전 신호 부재

### 유동성 담당자
- 한줄 요약: 유동성 및 정책 민감 지표는 여전히 보수적 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI 20일 누적 급락과 변동성 지속으로 유동성 환경이 매우 위축됨.
- 핵심 주장: 외국인 순매수에도 불구하고 환율과 변동성, 누적 하락폭이 위험회피 신호를 강화함.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '월별 지표와 단기 반등 신호가 상충하여 확신은 어렵습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.94%, foreign_net=+1286억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.korea_macro_context, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.vix_5d_avg
- [수급 담당자] 저는 수급 담당자 입장에서 '외국인 저점 매수와 환율 안정이 KOSPI 중심으로 수급 개선을 이끌었습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.94%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.news_headlines, snapshot.macro.daily.us10y
- [섹터 담당자] 저는 섹터 담당자 입장에서 '단기 반등에도 중기 약세 신호가 우세합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.94%, foreign_net=+1286억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.korea_macro_context
- [리스크 담당자] 저는 리스크 담당자 입장에서 '중기 약세 흐름이 지속되나 단기 반등과 수급 개선 신호가 혼재합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.94%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.korea_macro_context, snapshot.flow_summary.note, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추세 개선 신호가 명확하지 않습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+2.94%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.earnings_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.note, snapshot.market_summary.kospi_change_pct
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '지수 반등에도 하락 추세가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+1286억, institution_net=+973억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.foreign_net, snapshot.flow_summary.institution_net, snapshot.markets.kr.kospi_pct
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 및 정책 민감 지표는 여전히 보수적 접근이 필요합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+1286억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.vix_5d_avg, snapshot.markets.fx.usdkrw, snapshot.flow_summary.foreign_net, snapshot.macro.daily.vix, snapshot.phase_two_signals.liquidity_signal_score
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +2.94%, USD/KRW 1327.17(-0.15%), VIX 17.3, 외국인 +1286억이고, 뉴스는 반등·회복 기대가 섞인 완화 톤입니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 당일 반등의 추세 전환 여부: 다수=매크로·수급·섹터·리스크 담당자는 외국인·기관 순매수와 원화 강세를 반등 확인 신호로 보되, 20일 누적 하락이 커 중립적 확인이 필요하다고 판단했다., 소수=이익모멘텀·브레드스·유동성 담당자는 실적 개선 근거와 추세 반전 신호가 부족하고 누적 하락 및 변동성 부담이 남아 위험회피 관점을 유지했다., 에이전트=[earnings, breadth, liquidity]
  - 의미: 외국인 유입이 KOSPI에 집중된 단기 포지션 조정인지, 폭넓은 위험자산 재유입인지에 따라 반등의 지속성과 업종 선택이 달라진다.
- 한국 경기 배경의 방향성: 다수=심리·고용·수출 개선은 하방 완충 요인으로 평가됐다., 소수=생산·소비·설비투자 약화와 선행지수 하락은 실물경기 확장 판단을 유보하게 한다., 에이전트=[macro, sector, risk]
  - 의미: 월별 지표의 상충이 이어지면 지수 반등에도 내수·경기민감 업종의 실적 가시성은 제한될 수 있다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 단기 급등했으나 20일 누적 하락폭이 매우 커 중기 약세 국면이 지속 중입니다.",
    "한국 월별 지표는 심리·고용·수출은 긍정이나 생산·소비는 부진하여 경기 방향성에 불확실성이 큽니다.",
    "외국인 순매수와 환율 안정에도 불구하고, 최근 변동성 및 누적 하락을 감안하면 신중한 접근이 필요합니다."
  ],
  "korean_comment": "월별 지표와 단기 반등 신호가 상충하여 확신은 어렵습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW pre-analysis agent (Korean market)",
  "core_claims": [
    "외국인 순매수는 KOSPI에 집중되었으며, 고환율 안정(USD/KRW 하락)과 반도체/AI 기대감이 주요 배경입니다.",
    "최근 20일간 KOSPI 급락(-21.88%) 이후 저점 반발 매수 성격이 강하며, 외국인 유입은 FX 안정과 연준/금리 불확실성 완화에 따른 포지션 조정으로 해석됩니다.",
    "개인 매수는 KOSDAQ에서만 소폭 유입, KOSPI에서는 대규모 이탈로, 레버리지 추격매수보다는 손실 확정 및 수급 부담 완화 국면입니다."
  ],
  "korean_comment": "외국인 저점 매수와 환율 안정이 KOSPI 중심으로 수급 개선을 이끌었습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.dxy",
    "snapshot.cumulative_context.usdkrw_5d_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI는 단기 반등에도 불구하고 20일 누적 하락폭이 매우 큽니다.",
    "외국인·기관 순매수 유입이 긍정적이나, 중기적 약세 흐름이 뚜렷합니다.",
    "심리지표는 개선됐으나 생산·소비 지표는 부진합니다."
  ],
  "korean_comment": "단기 반등에도 중기 약세 신호가 우세합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
    "snapshot.korea_macro_context"
  ],
  "confidence": "MED"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI 20일 누적 하락폭이 매우 큼",
    "생산·소비 지표는 부정적이나 심리·수출·고용은 긍정적",
    "외국인·기관 순매수와 단기 반등세 확인"
  ],
  "korean_comment": "중기 약세 흐름이 지속되나 단기 반등과 수급 개선 신호가 혼재합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.korea_macro_context",
    "snapshot.flow_summary.note",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 신호는 부재하며, 추세 반전 조짐 없음",
    "단기 반등에도 중기 실적 전망 하향 압력 지속"
  ],
  "korean_comment": "실적 추세 개선 신호가 명확하지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.note",
    "snapshot.market_summary.kospi_change_pct"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI 단기 반등에도 중기 하락세 지속",
    "수급 개선 불구, 시장 확산력은 제한적",
    "지수 변동성 높고 확실한 반전 신호 부재"
  ],
  "korean_comment": "지수 반등에도 하락 추세가 뚜렷합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.foreign_net",
    "snapshot.flow_summary.institution_net",
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
    "KOSPI 20일 누적 급락과 변동성 지속으로 유동성 환경이 매우 위축됨.",
    "외국인 순매수에도 불구하고 환율과 변동성, 누적 하락폭이 위험회피 신호를 강화함."
  ],
  "korean_comment": "유동성 및 정책 민감 지표는 여전히 보수적 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.markets.fx.usdkrw",
    "snapshot.flow_summary.foreign_net",
    "snapshot.macro.daily.vix",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```