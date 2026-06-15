# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-06-15**
- 생성 시각(UTC): `2026-06-15T00:53:51.024576+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=5, RISK_OFF=1
- **다수 국면**: RISK_ON

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 확인된 모멘텀 주도주 중심으로 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] 변동성 한도를 기준으로 포지션 규모를 조절합니다.
- [OpsGuidanceLevel.AVOID/회피] 과열된 돌파 구간 추격 매수는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +5.67% / KOSDAQ +0.67%
- **미국 지수**: S&P500 +0.50% / NASDAQ +0.31% / DOW +0.70%
- **환율/변동성**: USD/KRW 1516.97 (-0.71%) / VIX 17.7
- **시장 요약 노트**: KOSPI 5.67%, USD/KRW 1516.97. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 +106억 / 기관 +6650억 / 개인 -6575억
- **일간 매크로**: 미10년 4.49% / 미2년 3.62% / 2-10 0.87%p / DXY 99.50
- **월간 매크로**: 실업률 4.30% / CPI YoY 4.27% / Core CPI YoY 2.96% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.60% / 기준금리 3.63% / 실질금리 2.18%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_ON.
  ↳ 출처: `regime_tuner`
- KOSPI가 5.67% 급등(8,587.16p)하며 20일 누적 +15.65%로 강한 랠리 지속, 기관 순매수 +6,650억이 주도.
  ↳ 출처: `CORE_SIGNALS, flow_data, macro_daily`
- 외국인은 소폭 순매수(+106억)로 신중한 태도, 개인은 대규모 차익실현 매도(-6,575억)로 전환.
  ↳ 출처: `CORE_SIGNALS, flow_data`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 최근 강한 상승세와 기관 매수세가 뚜렷하지만, 변동성은 주의가 필요합니다.
- 국면 태그: RISK_ON / 신뢰도: MED
- 핵심 주장: KOSPI가 최근 20일간 강하게 상승하며 위험선호가 뚜렷합니다.
- 핵심 주장: 기관 중심의 매수세가 강하게 유입되고 있습니다.
- 핵심 주장: 변동성은 다소 높지만, 단기적 위험 신호는 제한적입니다.

### 수급 담당자
- 한줄 요약: 기관 주도의 강한 매수세가 시장을 견인하며, 외국인은 신중한 태도를 보임.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: 기관 중심의 강한 매수세가 주도하며, 외국인은 제한적 순매수에 그침.
- 핵심 주장: 외국인 매수는 고환율 안정과 반도체/AI 기대감이 복합적으로 작용.
- 핵심 주장: 개인 대규모 매도는 최근 급등에 따른 차익실현 성격이 강함.

### 섹터 담당자
- 한줄 요약: 강한 상승세와 매수세가 지속되고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 15% 이상 상승하며 강한 랠리를 보이고 있습니다.
- 핵심 주장: 기관과 외국인의 순매수세가 뚜렷하게 나타나고 있습니다.
- 핵심 주장: 변동성(VIX)도 안정적인 수준으로 전환 중입니다.

### 리스크 담당자
- 한줄 요약: 과열 신호는 없으며, 위험 신호도 확인되지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI가 최근 20일간 15% 이상 급등함
- 핵심 주장: 기관 중심의 강한 매수세가 지속됨
- 핵심 주장: 변동성 및 환율도 안정적인 흐름을 보임

### 이익모멘텀 담당자
- 한줄 요약: 실적 추정치 상향 조정이 동반되지 않아 추세 전환 신호는 약합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 코스피 20일 누적 급등은 실적 모멘텀 개선 신호가 부족하다.
- 핵심 주장: 기관 중심 매수세는 일시적 기대감에 불과하며, 실적 추정치 상향은 확인되지 않는다.

### 브레드스 담당자
- 한줄 요약: 시장 전반의 확산과 강한 상승 모멘텀이 확인됩니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 최근 20일간 강한 상승세를 보임.
- 핵심 주장: 시장 전반에 걸친 매수세와 확산이 뚜렷하게 나타남.
- 핵심 주장: 단기 과열 신호는 없으며, 리스크온 환경이 유지됨.

### 유동성 담당자
- 한줄 요약: 정책 및 유동성 측면에서 위험선호가 확연히 강화되었습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: 유동성 환경이 매우 강하게 개선되고 있음.
- 핵심 주장: 환율 하락과 외국인 순매수로 위험선호가 뚜렷함.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 4명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '최근 강한 상승세와 기관 매수세가 뚜렷하지만, 변동성은 주의가 필요합니다.' 의견을 유지합니다. 근거 숫자는 institution_net=+6650억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.institution_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal
- [수급 담당자] 저는 수급 담당자 입장에서 '기관 주도의 강한 매수세가 시장을 견인하며, 외국인은 신중한 태도를 보임.' 의견을 유지합니다. 근거 숫자는 dxy=99.50입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.korean_market_flow, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.markets.fx.usdkrw, snapshot.news_headlines, snapshot.macro.daily.dxy
- [섹터 담당자] 저는 섹터 담당자 입장에서 '강한 상승세와 매수세가 지속되고 있습니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.note, snapshot.cumulative_context.vix_5d_avg
- [리스크 담당자] 저는 리스크 담당자 입장에서 '과열 신호는 없으며, 위험 신호도 확인되지 않습니다.' 의견을 유지합니다. 근거 숫자는 institution_net=+6650억입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.flow_summary.institution_net, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.reversal_signal
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 추정치 상향 조정이 동반되지 않아 추세 전환 신호는 약합니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.phase_two_signals.earnings_signal_score, snapshot.flow_summary.note, snapshot.cumulative_context.note
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반의 확산과 강한 상승 모멘텀이 확인됩니다.' 의견을 유지합니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_abs_move_5d_avg, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.phase_two_signals.breadth_signal_score, snapshot.flow_summary.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 및 유동성 측면에서 위험선호가 확연히 강화되었습니다.' 의견을 유지합니다. 근거 숫자는 foreign_net=+106억, vix=17.7입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.phase_two_signals.liquidity_signal_score, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.flow_summary.foreign_net, snapshot.markets.volatility.vix
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 온입니다. 근거는 KOSPI +5.67%, USD/KRW 1516.97(-0.71%), VIX 17.7, 외국인 +106억이고, 뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다. 따라서 모멘텀이 확인된 구간 위주로 비중을 늘리되 손절 기준은 짧게 가져갑니다.

## 7) 이견 사항
- 시장 과열 및 리스크 신호: 다수=과열 신호 없으며, 리스크온 환경이 유지된다는 의견(매크로, 수급, 섹터, 브레드스, 유동성 담당자), 소수=실적 모멘텀 부족으로 추세 전환 신호는 약하다는 의견(이익모멘텀 담당자), 에이전트=[earnings]
  - 의미: 실적 개선이 동반되지 않으면 랠리의 지속성에 한계가 있을 수 있어, 추후 실적 발표 시즌에 주의 필요.
- 외국인 매수의 지속성: 다수=기관 주도의 매수세가 시장을 견인하며 외국인은 신중하다는 평가(수급, 매크로, 섹터, 브레드스, 유동성 담당자), 소수=외국인 매수가 제한적이어서 랠리의 동력이 약할 수 있다는 시각(이익모멘텀, 리스크 담당자), 에이전트=[earnings, risk]
  - 의미: 외국인 매수세가 본격화되지 않으면 환율·글로벌 변수 변화 시 시장 변동성 확대 가능.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "KOSPI가 최근 20일간 강하게 상승하며 위험선호가 뚜렷합니다.",
    "기관 중심의 매수세가 강하게 유입되고 있습니다.",
    "변동성은 다소 높지만, 단기적 위험 신호는 제한적입니다."
  ],
  "korean_comment": "최근 강한 상승세와 기관 매수세가 뚜렷하지만, 변동성은 주의가 필요합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre_analysis_KR",
  "core_claims": [
    "기관 중심의 강한 매수세가 주도하며, 외국인은 제한적 순매수에 그침.",
    "외국인 매수는 고환율 안정과 반도체/AI 기대감이 복합적으로 작용.",
    "개인 대규모 매도는 최근 급등에 따른 차익실현 성격이 강함."
  ],
  "korean_comment": "기관 주도의 강한 매수세가 시장을 견인하며, 외국인은 신중한 태도를 보임.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.korean_market_flow",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.markets.fx.usdkrw",
    "snapshot.news_headlines",
    "snapshot.macro.daily.dxy"
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
    "기관과 외국인의 순매수세가 뚜렷하게 나타나고 있습니다.",
    "변동성(VIX)도 안정적인 수준으로 전환 중입니다."
  ],
  "korean_comment": "강한 상승세와 매수세가 지속되고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.note",
    "snapshot.cumulative_context.vix_5d_avg"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "KOSPI가 최근 20일간 15% 이상 급등함",
    "기관 중심의 강한 매수세가 지속됨",
    "변동성 및 환율도 안정적인 흐름을 보임"
  ],
  "korean_comment": "과열 신호는 없으며, 위험 신호도 확인되지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.flow_summary.institution_net",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.reversal_signal"
  ],
  "confidence": "HIGH"
}
```
### 이익모멘텀 담당자
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "코스피 20일 누적 급등은 실적 모멘텀 개선 신호가 부족하다.",
    "기관 중심 매수세는 일시적 기대감에 불과하며, 실적 추정치 상향은 확인되지 않는다."
  ],
  "korean_comment": "실적 추정치 상향 조정이 동반되지 않아 추세 전환 신호는 약합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.flow_summary.note",
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
    "KOSPI와 KOSDAQ 모두 최근 20일간 강한 상승세를 보임.",
    "시장 전반에 걸친 매수세와 확산이 뚜렷하게 나타남.",
    "단기 과열 신호는 없으며, 리스크온 환경이 유지됨."
  ],
  "korean_comment": "시장 전반의 확산과 강한 상승 모멘텀이 확인됩니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_abs_move_5d_avg",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.flow_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 유동성 담당자
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "유동성 환경이 매우 강하게 개선되고 있음.",
    "환율 하락과 외국인 순매수로 위험선호가 뚜렷함."
  ],
  "korean_comment": "정책 및 유동성 측면에서 위험선호가 확연히 강화되었습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.phase_two_signals.liquidity_signal_score",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.flow_summary.foreign_net",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "HIGH"
}
```