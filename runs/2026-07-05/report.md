# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-07-05**
- 생성 시각(UTC): `2026-07-05T00:53:33.216858+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.
- **국면 투표**: NEUTRAL=5, RISK_ON=2, RISK_OFF=0
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 확인된 모멘텀 주도주 중심으로 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] 변동성 한도를 기준으로 포지션 규모를 조절합니다.
- [OpsGuidanceLevel.AVOID/회피] 과열된 돌파 구간 추격 매수는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +5.76% / KOSDAQ +0.19%
- **미국 지수**: S&P500 +0.00% / NASDAQ -0.80% / DOW +1.14%
- **환율/변동성**: USD/KRW 1532.63 (-0.51%) / VIX 16.1
- **시장 요약 노트**: KOSPI 5.76%, USD/KRW 1532.63. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -21952억 / 기관 +43042억 / 개인 -21867억
- **일간 매크로**: 미10년 4.48% / 미2년 3.67% / 2-10 0.82%p / DXY 100.86
- **월간 매크로**: 실업률 4.20% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 2.10% / 기준금리 3.63% / 실질금리 2.25%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_ON.
  ↳ 출처: `regime_tuner`
- KOSPI는 8088.34pt(+5.76%)로 급등했으나, 외국인 순매도(-2.2조원)와 기관 순매수(+4.3조원)가 극명하게 엇갈렸습니다.
  ↳ 출처: `flow_data, macro_daily`
- USD/KRW 환율은 1532.63원(-0.51%)로 소폭 하락하며 안정세를 보였고, VIX(16.1)도 낮은 수준을 유지했습니다.
  ↳ 출처: `macro_daily`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 강한 상승세 이후 조정 가능성도 염두에 두어야 합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 20일간 강한 상승세를 보였습니다.
- 핵심 주장: 외국인 순매도와 고환율이 부담 요인으로 남아 있습니다.
- 핵심 주장: 단기적으로 변동성 확대 가능성에 유의해야 합니다.

### 수급 담당자
- 한줄 요약: 차익실현 매물 출회 속 기관이 수급을 주도하며, 외국인 매도는 고점 부담과 리밸런싱 영향이 큼.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: 외국인은 최근 20일간 KOSPI가 15% 이상 급등한 후 대규모 차익실현 매도에 나섰음(반도체/AI, 고환율).
- 핵심 주장: USD/KRW 하락에도 불구하고 외국인 매도는 FX 이슈보다는 포트폴리오 리밸런싱 및 차익실현 성격이 강함.
- 핵심 주장: 개인은 KOSPI에서 대규모 매도, KOSDAQ에서 소규모 매수로 전환하며, 기관이 대규모 매수세로 흡수 중임.

### 섹터 담당자
- 한줄 요약: 기관 매수와 강한 랠리로 위험선호가 뚜렷합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 15% 이상 상승하며 강한 랠리를 보이고 있습니다.
- 핵심 주장: 기관의 대규모 순매수와 외국인 순매도에도 불구하고 시장은 견조합니다.
- 핵심 주장: 환율 하락과 낮은 변동성(VIX)이 위험선호 분위기를 뒷받침합니다.

### 리스크 담당자
- 한줄 요약: 시장 강세가 뚜렷하며 위험 신호는 제한적입니다.
- 국면 태그: NEUTRAL / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 15% 이상 상승
- 핵심 주장: 외국인 순매도에도 시장은 강세 유지
- 핵심 주장: 변동성(VIX)과 환율 안정적

### 이익모멘텀 담당자
- 한줄 요약: 실적 모멘텀은 긍정적이나, 추정치 상향은 제한적입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI의 20일 누적 상승은 실적 모멘텀 기대를 반영함.
- 핵심 주장: 외국인 순매도에도 기관 매수세가 실적 개선 기대를 뒷받침.
- 핵심 주장: 실적 추정치 상향 조정 신호는 아직 뚜렷하지 않음.

### 브레드스 담당자
- 한줄 요약: 시장 전반에 걸친 강한 매수세가 확인됩니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI의 강한 상승세와 20일 누적 상승률이 매우 높음.
- 핵심 주장: 시장 전반의 확산(breadth)과 기관 매수세가 뚜렷함.
- 핵심 주장: 단기 과열 신호는 없으며, 리스크 온 환경 지속.

### 유동성 담당자
- 한줄 요약: 유동성 개선 신호는 제한적이며, 정책 불확실성도 상존합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: KOSPI가 단기적으로 강하게 상승했으나 외국인 자금 유출이 지속되고 있습니다.
- 핵심 주장: 환율은 소폭 하락했지만 여전히 높은 수준을 유지하고 있습니다.
- 핵심 주장: 정책 및 유동성 환경은 보수적으로 해석해야 합니다.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 6명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '강한 상승세 이후 조정 가능성도 염두에 두어야 합니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-21952억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.vix_5d_avg, snapshot.news_headlines
- [수급 담당자] 저는 수급 담당자 입장에서 '차익실현 매물 출회 속 기관이 수급을 주도하며, 외국인 매도는 고점 부담과 리밸런싱 영향이 큼.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+5.76%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines, snapshot.macro.daily.usdkrw
- [섹터 담당자] 저는 섹터 담당자 입장에서 '기관 매수와 강한 랠리로 위험선호가 뚜렷합니다.' 의견을 유지합니다. 근거 숫자는 institution_net=+43042억, foreign_net=-21952억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.institution_net, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw_pct, snapshot.markets.volatility.vix, snapshot.cumulative_context.note
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 강세가 뚜렷하며 위험 신호는 제한적입니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=-21952억, kospi_change_pct=+5.76%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.foreign_net, snapshot.market_summary.kospi_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.markets.fx.usdkrw_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.news_headlines
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 모멘텀은 긍정적이나, 추정치 상향은 제한적입니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.phase_two_signals.earnings_signal_score, snapshot.news_headlines, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반에 걸친 강한 매수세가 확인됩니다.' 의견을 유지합니다. 근거 숫자는 institution_net=+43042억, foreign_net=-21952억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.institution_net, snapshot.flow_summary.foreign_net, snapshot.cumulative_context.reversal_signal, snapshot.cumulative_context.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '유동성 개선 신호는 제한적이며, 정책 불확실성도 상존합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+5.76%, foreign_net=-21952억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.kospi_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.fx.usdkrw, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.news_headlines, snapshot.macro.structural.fed_funds_rate
- 라운드 결론: 의장 정리: 오늘 다수 의견은 중립입니다. 근거는 KOSPI +5.76%, USD/KRW 1532.63(-0.51%), VIX 16.1, 외국인 -21952억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다.

## 7) 이견 사항
- 시장 위험선호(리스크온) 해석: 다수=외국인 매도와 정책 불확실성, 차익실현 등으로 중립적 대응이 필요하다는 의견이 우세, 소수=기관 매수와 시장 전반 확산(breadth)으로 리스크온 환경이 지속된다는 의견(섹터, 브레드스 담당자), 에이전트=[sector, breadth]
  - 의미: 기관 주도의 강한 랠리가 단기 과열로 이어질지, 외국인 매도와 정책 변수로 조정이 나올지 판단이 중요

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 20일간 강한 상승세를 보였습니다.",
    "외국인 순매도와 고환율이 부담 요인으로 남아 있습니다.",
    "단기적으로 변동성 확대 가능성에 유의해야 합니다."
  ],
  "korean_comment": "강한 상승세 이후 조정 가능성도 염두에 두어야 합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.news_headlines"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre_analysis_KR_v2",
  "core_claims": [
    "외국인은 최근 20일간 KOSPI가 15% 이상 급등한 후 대규모 차익실현 매도에 나섰음(반도체/AI, 고환율).",
    "USD/KRW 하락에도 불구하고 외국인 매도는 FX 이슈보다는 포트폴리오 리밸런싱 및 차익실현 성격이 강함.",
    "개인은 KOSPI에서 대규모 매도, KOSDAQ에서 소규모 매수로 전환하며, 기관이 대규모 매수세로 흡수 중임."
  ],
  "korean_comment": "차익실현 매물 출회 속 기관이 수급을 주도하며, 외국인 매도는 고점 부담과 리밸런싱 영향이 큼.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.news_headlines",
    "snapshot.macro.daily.usdkrw",
    "snapshot.macro.daily.dxy",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "HIGH"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "KOSPI가 최근 20일간 15% 이상 상승하며 강한 랠리를 보이고 있습니다.",
    "기관의 대규모 순매수와 외국인 순매도에도 불구하고 시장은 견조합니다.",
    "환율 하락과 낮은 변동성(VIX)이 위험선호 분위기를 뒷받침합니다."
  ],
  "korean_comment": "기관 매수와 강한 랠리로 위험선호가 뚜렷합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.institution_net",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 20일간 15% 이상 상승",
    "외국인 순매도에도 시장은 강세 유지",
    "변동성(VIX)과 환율 안정적"
  ],
  "korean_comment": "시장 강세가 뚜렷하며 위험 신호는 제한적입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
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
    "KOSPI의 20일 누적 상승은 실적 모멘텀 기대를 반영함.",
    "외국인 순매도에도 기관 매수세가 실적 개선 기대를 뒷받침.",
    "실적 추정치 상향 조정 신호는 아직 뚜렷하지 않음."
  ],
  "korean_comment": "실적 모멘텀은 긍정적이나, 추정치 상향은 제한적입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.note"
  ],
  "confidence": "MED"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI의 강한 상승세와 20일 누적 상승률이 매우 높음.",
    "시장 전반의 확산(breadth)과 기관 매수세가 뚜렷함.",
    "단기 과열 신호는 없으며, 리스크 온 환경 지속."
  ],
  "korean_comment": "시장 전반에 걸친 강한 매수세가 확인됩니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.institution_net",
    "snapshot.flow_summary.foreign_net",
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
    "KOSPI가 단기적으로 강하게 상승했으나 외국인 자금 유출이 지속되고 있습니다.",
    "환율은 소폭 하락했지만 여전히 높은 수준을 유지하고 있습니다.",
    "정책 및 유동성 환경은 보수적으로 해석해야 합니다."
  ],
  "korean_comment": "유동성 개선 신호는 제한적이며, 정책 불확실성도 상존합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.fx.usdkrw",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.news_headlines",
    "snapshot.macro.structural.fed_funds_rate"
  ],
  "confidence": "MED"
}
```