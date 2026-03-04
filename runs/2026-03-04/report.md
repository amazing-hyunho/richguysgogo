# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-03-04**
- 생성 시각(UTC): `2026-03-03T22:51:25.173774+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=2, RISK_ON=0, RISK_OFF=5
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -7.24% / KOSDAQ -4.62%
- **미국 지수**: S&P500 -0.94% / NASDAQ -1.02% / DOW -0.83%
- **환율/변동성**: USD/KRW 1459.33 (+0.00%) / VIX 23.6
- **시장 요약 노트**: KOSPI -7.24%, USD/KRW 1459.33. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 4.06% / 미2년 3.60% / 2-10 0.46%p / DXY 99.06
- **월간 매크로**: 실업률 4.30% / CPI YoY 2.83% / Core CPI YoY 2.95% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.40% / 기준금리 3.64% / 실질금리 1.77%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `flow, sector, earnings, breadth, liquidity`
- 공통 근거: snapshot.market_summary.kospi_change_pct.
  ↳ 출처: `breadth, earnings, flow, liquidity, macro`

## 5) AI 에이전트 의견
### 매크로
- 한줄 요약: 거시는 균형적이며 선택적 대응이 적절합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: Macro tone is balanced.
- 핵심 주장: No major shocks.
- 핵심 주장: Stay selective.

### 수급
- 한줄 요약: 시장 전반에 강한 위험 회피 분위기가 감지됩니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피가 7% 이상 급락하며 극단적 약세를 보이고 있습니다.
- 핵심 주장: 시장 변동성(VIX)도 23 이상으로 높아 위험 회피 심리가 강합니다.
- 핵심 주장: 수급 데이터 부재로 추가 하락 위험을 배제할 수 없습니다.

### 섹터
- 한줄 요약: 한국 증시는 극단적 위험 회피 국면에 진입했습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피가 7% 이상 급락하며 극심한 위험 회피 심리가 나타남.
- 핵심 주장: 유가 상승과 지정학적 리스크로 낙관론이 크게 약화됨.
- 핵심 주장: 시장 변동성(VIX)도 높아져 추가 하락 위험이 큼.

### 리스크
- 한줄 요약: 급격한 리스크는 없어 규율을 유지하세요.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: Risk signals stable.
- 핵심 주장: No acute stress.
- 핵심 주장: Maintain discipline.

### 이익모멘텀
- 한줄 요약: 실적 전망이 빠르게 악화되는 구간입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피 급락은 단기 충격으로, 실적 추정치 하향 압력 커짐.
- 핵심 주장: 지속적 실적 모멘텀 약화 가능성 높음.
- 핵심 주장: 가이던스 하향 조정 우려 확대.

### 브레드스
- 한줄 요약: 시장 전반에 걸친 매도세가 뚜렷하게 나타납니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피와 코스닥 모두 극단적 하락세를 보임.
- 핵심 주장: 시장 전반에 걸친 확산 약화와 기술적 붕괴 신호.
- 핵심 주장: 시장 내부 확산지표가 매우 부정적임.

### 유동성
- 한줄 요약: 유동성 악화와 환율 불안이 위험회피를 자극하고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피 7% 급락과 변동성(VIX) 급등으로 유동성 경색 신호.
- 핵심 주장: USD/KRW 1459로 환율 불안정성 지속.
- 핵심 주장: 정책 민감 자산 전반에 위험회피 심리 강화.

## 6) 이견 사항
- 국면 태그: 다수=RISK_OFF, 소수=NEUTRAL, 에이전트=[macro, risk]
  - 의미: 소수 의견 국면은 포지션 경계에 영향을 줄 수 있습니다.

## 7) AI 원문 응답 (디버깅/검토용)
### 매크로
(stub or raw response unavailable)
### 수급
```text
{
  "agent_name": "FLOW pre-analysis agent",
  "core_claims": [
    "코스피가 7% 이상 급락하며 극단적 약세를 보이고 있습니다.",
    "시장 변동성(VIX)도 23 이상으로 높아 위험 회피 심리가 강합니다.",
    "수급 데이터 부재로 추가 하락 위험을 배제할 수 없습니다."
  ],
  "korean_comment": "시장 전반에 강한 위험 회피 분위기가 감지됩니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
    "snapshot.flow_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 섹터
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "코스피가 7% 이상 급락하며 극심한 위험 회피 심리가 나타남.",
    "유가 상승과 지정학적 리스크로 낙관론이 크게 약화됨.",
    "시장 변동성(VIX)도 높아져 추가 하락 위험이 큼."
  ],
  "korean_comment": "한국 증시는 극단적 위험 회피 국면에 진입했습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.note",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
    "snapshot.phase_two_signals.breadth_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 리스크
(stub or raw response unavailable)
### 이익모멘텀
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "코스피 급락은 단기 충격으로, 실적 추정치 하향 압력 커짐.",
    "지속적 실적 모멘텀 약화 가능성 높음.",
    "가이던스 하향 조정 우려 확대."
  ],
  "korean_comment": "실적 전망이 빠르게 악화되는 구간입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.note",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.phase_two_signals.earnings_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 브레드스
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "코스피와 코스닥 모두 극단적 하락세를 보임.",
    "시장 전반에 걸친 확산 약화와 기술적 붕괴 신호.",
    "시장 내부 확산지표가 매우 부정적임."
  ],
  "korean_comment": "시장 전반에 걸친 매도세가 뚜렷하게 나타납니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.phase_two_signals.breadth_signal_score",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```
### 유동성
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "코스피 7% 급락과 변동성(VIX) 급등으로 유동성 경색 신호.",
    "USD/KRW 1459로 환율 불안정성 지속.",
    "정책 민감 자산 전반에 위험회피 심리 강화."
  ],
  "korean_comment": "유동성 악화와 환율 불안이 위험회피를 자극하고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines"
  ],
  "confidence": "HIGH"
}
```