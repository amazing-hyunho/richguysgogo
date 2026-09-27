# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-09-27**
- 생성 시각(UTC): `2026-09-27T00:53:11.676192+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=5, RISK_OFF=1
- **다수 국면**: RISK_ON

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 확인된 모멘텀 주도주 중심으로 대응합니다.
- [OpsGuidanceLevel.CAUTION/주의] 변동성 한도를 기준으로 포지션 규모를 조절합니다.
- [OpsGuidanceLevel.AVOID/회피] 과열된 돌파 구간 추격 매수는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +0.90% / KOSDAQ +1.21%
- **미국 지수**: S&P500 +0.51% / NASDAQ +0.48% / DOW +0.93%
- **환율/변동성**: USD/KRW 1357.05 (-0.82%) / VIX 14.9
- **시장 요약 노트**: KOSPI 0.90%, USD/KRW 1357.05. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 5.18% / 미2년 4.07% / 2-10 1.11%p / DXY 100.97
- **월간 매크로**: 실업률 4.10% / CPI YoY 3.71% / Core CPI YoY 2.76% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.50% / 기준금리 3.63% / 실질금리 2.84%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_ON.
  ↳ 출처: `regime_tuner`
- KOSPI는 7,080.92로 0.90%, KOSDAQ은 844.48로 1.21% 상승했고 KOSPI 5일·20일 누적 수익률도 각각 2.843%, 5.9%다.
  ↳ 출처: `market_data, cumulative_context`
- USD/KRW는 1,357.05로 당일 0.819% 하락했지만 5일 변화율은 0.495% 상승해 환율 안정 여부를 추가 확인해야 한다.
  ↳ 출처: `macro_daily, cumulative_context`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 최근 상승세가 이어지고 있으나, 금리와 인플레이션 변수는 주의가 필요합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 코스피와 글로벌 증시가 최근 20일간 견조한 상승세를 보이고 있습니다.
- 핵심 주장: 미국 금리와 인플레이션 변수는 여전히 불확실성을 내포하고 있습니다.
- 핵심 주장: 환율 하락과 낮은 변동성은 단기적으로 위험 선호 분위기를 시사합니다.

### 수급 담당자
- 한줄 요약: 수급 데이터 부재로 주체별 해석은 제한적이나, 누적 강세와 매크로 환경은 위험선호 분위기 유지.
- 국면 태그: RISK_ON / 신뢰도: LOW
- 핵심 주장: 핵심 키워드: 환율/달러, 금리/연준, 반도체/AI, 인플레이션.
- 핵심 주장: 외국인/기관/개인 순매수 데이터가 제공되지 않아 흐름 해석에 한계가 있음.
- 핵심 주장: KOSPI 20일 누적 강세와 환율 하락, 반도체 실적 기대감이 시장 상승을 견인.

### 섹터 담당자
- 한줄 요약: 시장 전반적으로 긍정적이지만 환율과 금리 변수에 유의해야 합니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: 코스피와 코스닥이 최근 20일간 강한 상승세를 보이고 있다.
- 핵심 주장: AI 및 반도체 업종 호황이 시장 상승을 견인하고 있다.
- 핵심 주장: 환율 하락과 미국 금리 변수는 주의가 필요하다.

### 리스크 담당자
- 한줄 요약: 시장 전반에 뚜렷한 위험 신호는 보이지 않습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피와 코스닥이 최근 20일간 강한 상승세를 보임
- 핵심 주장: 환율과 변동성(VIX)도 안정적인 흐름 유지
- 핵심 주장: 특별한 리스크 신호나 반전 신호 없음

### 이익모멘텀 담당자
- 한줄 요약: 실적 기대감이 시장에 긍정적으로 반영되고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: AI 메모리 호황과 반도체 업종 실적 기대감이 지속되고 있음
- 핵심 주장: 3분기 실적 전망 상향 조정 분위기이나 환율 하락이 변수로 작용
- 핵심 주장: 20일 누적 코스피 상승은 실적 모멘텀 반영으로 해석 가능

### 브레드스 담당자
- 한줄 요약: 시장 전반적으로 상승 확산세가 유지되고 있습니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 최근 5일, 20일 누적 상승세가 뚜렷하다.
- 핵심 주장: 시장 전반의 확산(breadth)도 양호하며, 단기 변동성도 낮은 편이다.
- 핵심 주장: 외국인·기관 수급 데이터는 부재하나, 기술적 확산은 긍정적이다.

### 유동성 담당자
- 한줄 요약: 정책 및 유동성 환경이 위험선호에 우호적입니다.
- 국면 태그: RISK_ON / 신뢰도: HIGH
- 핵심 주장: 환율 하락과 낮은 변동성으로 유동성 환경이 양호함.
- 핵심 주장: 금리 급등 우려에도 시장은 견조한 흐름을 보임.
- 핵심 주장: 누적 수익률도 긍정적으로 위험선호가 유지됨.

## 6) 에이전트 회의록(1라운드)
- 라운드: 1
- 지표 활용 체크: 7/7명이 수치형 지표 근거를 인용했습니다.
- 진행 메모: 오늘은 7명 중 7명이 숫자 지표를 직접 언급했습니다. 분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다.
- [매크로 담당자] 저는 매크로 담당자 입장에서 '최근 상승세가 이어지고 있으나, 금리와 인플레이션 변수는 주의가 필요합니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1357.05, vix=14.9입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.usdkrw, snapshot.markets.volatility.vix, snapshot.macro.daily.us10y, snapshot.macro.monthly.cpi_yoy, snapshot.news_headlines
- [수급 담당자] 저는 수급 담당자 입장에서 '수급 데이터 부재로 주체별 해석은 제한적이나, 누적 강세와 매크로 환경은 위험선호 분위기 유지.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+0.90%, usdkrw=1357.05입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.flow_summary.note, snapshot.market_summary.kospi_change_pct, snapshot.market_summary.usdkrw, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.usdkrw_5d_change_pct, snapshot.cumulative_context.vix_5d_avg
- [섹터 담당자] 저는 섹터 담당자 입장에서 '시장 전반적으로 긍정적이지만 환율과 금리 변수에 유의해야 합니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+0.90%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.news_headlines, snapshot.market_summary.kospi_change_pct, snapshot.markets.kr.kosdaq_pct, snapshot.macro.daily.us10y, snapshot.macro.daily.usdkrw
- [리스크 담당자] 저는 리스크 담당자 입장에서 '시장 전반에 뚜렷한 위험 신호는 보이지 않습니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1357.05, vix=14.9입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.cumulative_context.reversal_signal, snapshot.market_summary.usdkrw, snapshot.markets.volatility.vix, snapshot.news_headlines
- [이익모멘텀 담당자] 저는 이익모멘텀 담당자 입장에서 '실적 기대감이 시장에 긍정적으로 반영되고 있습니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1357.05입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.news_headlines, snapshot.market_summary.note, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.market_summary.usdkrw
- [브레드스 담당자] 저는 브레드스 담당자 입장에서 '시장 전반적으로 상승 확산세가 유지되고 있습니다.' 의견을 유지합니다. 근거 숫자는 kospi_change_pct=+0.90%입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.phase_two_signals.breadth_signal_score, snapshot.market_summary.kospi_change_pct, snapshot.markets.kr.kosdaq_pct, snapshot.flow_summary.note
- [유동성 담당자] 저는 유동성 담당자 입장에서 '정책 및 유동성 환경이 위험선호에 우호적입니다.' 의견을 유지합니다. 근거 숫자는 usdkrw=1357.05, vix=14.9입니다. 결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.
  - 참조 근거: snapshot.market_summary.usdkrw, snapshot.markets.fx.usdkrw_pct, snapshot.markets.volatility.vix, snapshot.news_headlines, snapshot.cumulative_context.kospi_20d_cum_pct, snapshot.cumulative_context.kospi_5d_cum_pct, snapshot.cumulative_context.vix_5d_avg, snapshot.macro.daily.us10y
- 라운드 결론: 의장 정리: 오늘 다수 의견은 리스크 온입니다. 근거는 KOSPI +0.90%, USD/KRW 1357.05(-0.82%), VIX 14.9, 외국인 +0억이고, 뉴스는 방향성이 엇갈려 단정하기 어렵습니다. 따라서 모멘텀이 확인된 구간 위주로 비중을 늘리되 손절 기준은 짧게 가져갑니다.

## 7) 이견 사항
- 시장 체제 판단: 다수=수급·섹터·이익모멘텀·브레드스·유동성 담당자는 누적 상승과 환율 하락을 근거로 위험선호가 유지된다고 판단했다., 소수=매크로 담당자는 중립, 리스크 담당자는 공식적으로 위험회피 태그를 제시했다., 에이전트=[macro, risk]
  - 의미: 미국 장기금리 상승과 주체별 순매수 데이터 부재 때문에 지수 상승만으로 위험선호의 지속성을 단정하기 어렵다.
- 원화 강세의 영향: 다수=매크로·유동성 담당자는 당일 원화 강세를 국내 위험자산에 우호적인 유동성 신호로 해석했다., 소수=이익모멘텀 담당자는 환율 하락이 반도체 수출기업 실적의 변수가 될 수 있다고 지적했다., 에이전트=[earnings]
  - 의미: 원화 강세는 외국인 투자환경에는 긍정적일 수 있지만 수출기업의 원화 환산 실적에는 상충된 영향을 줄 수 있다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
```text
{
  "agent_name": "MACRO_pre_analysis_agent",
  "core_claims": [
    "코스피와 글로벌 증시가 최근 20일간 견조한 상승세를 보이고 있습니다.",
    "미국 금리와 인플레이션 변수는 여전히 불확실성을 내포하고 있습니다.",
    "환율 하락과 낮은 변동성은 단기적으로 위험 선호 분위기를 시사합니다."
  ],
  "korean_comment": "최근 상승세가 이어지고 있으나, 금리와 인플레이션 변수는 주의가 필요합니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.monthly.cpi_yoy",
    "snapshot.news_headlines"
  ],
  "confidence": "MED"
}
```
### 수급 담당자
```text
{
  "agent_name": "FLOW_pre-analysis_KR",
  "core_claims": [
    "핵심 키워드: 환율/달러, 금리/연준, 반도체/AI, 인플레이션.",
    "외국인/기관/개인 순매수 데이터가 제공되지 않아 흐름 해석에 한계가 있음.",
    "KOSPI 20일 누적 강세와 환율 하락, 반도체 실적 기대감이 시장 상승을 견인."
  ],
  "korean_comment": "수급 데이터 부재로 주체별 해석은 제한적이나, 누적 강세와 매크로 환경은 위험선호 분위기 유지.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.flow_summary.note",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.usdkrw_5d_change_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.macro.daily.us10y"
  ],
  "confidence": "LOW"
}
```
### 섹터 담당자
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "코스피와 코스닥이 최근 20일간 강한 상승세를 보이고 있다.",
    "AI 및 반도체 업종 호황이 시장 상승을 견인하고 있다.",
    "환율 하락과 미국 금리 변수는 주의가 필요하다."
  ],
  "korean_comment": "시장 전반적으로 긍정적이지만 환율과 금리 변수에 유의해야 합니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.news_headlines",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.macro.daily.us10y",
    "snapshot.macro.daily.usdkrw"
  ],
  "confidence": "HIGH"
}
```
### 리스크 담당자
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "코스피와 코스닥이 최근 20일간 강한 상승세를 보임",
    "환율과 변동성(VIX)도 안정적인 흐름 유지",
    "특별한 리스크 신호나 반전 신호 없음"
  ],
  "korean_comment": "시장 전반에 뚜렷한 위험 신호는 보이지 않습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.cumulative_context.reversal_signal",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.volatility.vix",
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
    "AI 메모리 호황과 반도체 업종 실적 기대감이 지속되고 있음",
    "3분기 실적 전망 상향 조정 분위기이나 환율 하락이 변수로 작용",
    "20일 누적 코스피 상승은 실적 모멘텀 반영으로 해석 가능"
  ],
  "korean_comment": "실적 기대감이 시장에 긍정적으로 반영되고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.news_headlines",
    "snapshot.market_summary.note",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.market_summary.usdkrw"
  ],
  "confidence": "HIGH"
}
```
### 브레드스 담당자
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI와 KOSDAQ 모두 최근 5일, 20일 누적 상승세가 뚜렷하다.",
    "시장 전반의 확산(breadth)도 양호하며, 단기 변동성도 낮은 편이다.",
    "외국인·기관 수급 데이터는 부재하나, 기술적 확산은 긍정적이다."
  ],
  "korean_comment": "시장 전반적으로 상승 확산세가 유지되고 있습니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.kr.kosdaq_pct",
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
    "환율 하락과 낮은 변동성으로 유동성 환경이 양호함.",
    "금리 급등 우려에도 시장은 견조한 흐름을 보임.",
    "누적 수익률도 긍정적으로 위험선호가 유지됨."
  ],
  "korean_comment": "정책 및 유동성 환경이 위험선호에 우호적입니다.",
  "regime_tag": "RISK_ON",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.fx.usdkrw_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines",
    "snapshot.cumulative_context.kospi_20d_cum_pct",
    "snapshot.cumulative_context.kospi_5d_cum_pct",
    "snapshot.cumulative_context.vix_5d_avg",
    "snapshot.macro.daily.us10y"
  ],
  "confidence": "HIGH"
}
```