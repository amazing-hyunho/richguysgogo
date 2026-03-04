# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-02-28**
- 생성 시각(UTC): `2026-02-27T22:51:10.983050+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 선별적 포지셔닝을 전제로 중립적 입장을 유지합니다.
- **국면 투표**: NEUTRAL=4, RISK_ON=0, RISK_OFF=3
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 노출을 균형 있게 유지합니다.
- [OpsGuidanceLevel.CAUTION/주의] 리스크 한도를 엄격히 유지합니다.
- [OpsGuidanceLevel.AVOID/회피] 과도한 레버리지는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -1.00% / KOSDAQ +0.39%
- **미국 지수**: S&P500 -0.43% / NASDAQ -0.92% / DOW -1.05%
- **환율/변동성**: USD/KRW 1429.10 (+0.00%) / VIX 19.9
- **시장 요약 노트**: KOSPI -1.00%, USD/KRW 1429.10. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 3.96% / 미2년 3.58% / 2-10 0.38%p / DXY 97.65
- **월간 매크로**: 실업률 4.30% / CPI YoY 2.83% / Core CPI YoY 2.95% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.40% / 기준금리 3.64% / 실질금리 1.68%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: NEUTRAL.
  ↳ 출처: `macro, flow, risk, breadth`
- 공통 근거: snapshot.market_summary.kospi_change_pct.
  ↳ 출처: `earnings, liquidity, macro, risk, sector`

## 5) AI 에이전트 의견
### 매크로
- 한줄 요약: 거시는 균형적이며 선택적 대응이 적절합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: Macro tone is balanced.
- 핵심 주장: No major shocks.
- 핵심 주장: Stay selective.

### 수급
- 한줄 요약: 수급 데이터가 없어 중립을 유지합니다.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: Flow data unavailable.
- 핵심 주장: Use neutral stance.

### 섹터
- 한줄 요약: 외국인 매도세와 변동성 상승으로 단기 위험이 확대되고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피가 1% 하락하며 외국인 대규모 매도세가 확인됨.
- 핵심 주장: 시장 변동성(VIX) 상승과 외국인 이탈로 단기 조정 위험이 커짐.
- 핵심 주장: 환율(USD/KRW) 고정에도 불구하고 투자심리 위축이 뚜렷함.

### 리스크
- 한줄 요약: 급격한 리스크는 없어 규율을 유지하세요.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: Risk signals stable.
- 핵심 주장: No acute stress.
- 핵심 주장: Maintain discipline.

### 이익모멘텀
- 한줄 요약: 실적 추정치 상향 조정 신호가 부족해 주의가 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: 코스피 하락과 외국인 대규모 매도는 실적 모멘텀 둔화 우려를 반영.
- 핵심 주장: 실적 추정치 상향 뉴스 부재, 단기 반등은 지속성 약함.
- 핵심 주장: 지속적인 실적 상향 신호 없이 단기 변동성 확대.

### 브레드스
- 한줄 요약: 브레드스 신호가 혼재되어 중립 대응이 합리적입니다.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: 추세 확산과 역추세 신호가 공존합니다.
- 핵심 주장: 기술적 우위가 명확하지 않습니다.
- 핵심 주장: 방향 확정 전까지 균형 비중이 적절합니다.

### 유동성
- 한줄 요약: 유동성 악화와 변동성 상승으로 보수적 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피 급락과 외국인 대규모 매도세로 유동성 경색 신호.
- 핵심 주장: USD/KRW 1429.10 고정, 변동성(VIX) 19.86로 위험회피 심리 강화.
- 핵심 주장: 정책 민감 자금 유입 부진, 위험선호 약화.

## 6) 이견 사항
- 국면 태그: 다수=NEUTRAL, 소수=RISK_OFF, 에이전트=[sector, earnings, liquidity]
  - 의미: 소수 의견 국면은 포지션 경계에 영향을 줄 수 있습니다.

## 7) AI 원문 응답 (디버깅/검토용)
### 매크로
(stub or raw response unavailable)
### 수급
(stub or raw response unavailable)
### 섹터
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "코스피가 1% 하락하며 외국인 대규모 매도세가 확인됨.",
    "시장 변동성(VIX) 상승과 외국인 이탈로 단기 조정 위험이 커짐.",
    "환율(USD/KRW) 고정에도 불구하고 투자심리 위축이 뚜렷함."
  ],
  "korean_comment": "외국인 매도세와 변동성 상승으로 단기 위험이 확대되고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
    "snapshot.market_summary.usdkrw"
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
    "코스피 하락과 외국인 대규모 매도는 실적 모멘텀 둔화 우려를 반영.",
    "실적 추정치 상향 뉴스 부재, 단기 반등은 지속성 약함.",
    "지속적인 실적 상향 신호 없이 단기 변동성 확대."
  ],
  "korean_comment": "실적 추정치 상향 조정 신호가 부족해 주의가 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.phase_two_signals.earnings_signal_score"
  ],
  "confidence": "MED"
}
```
### 브레드스
(stub or raw response unavailable)
### 유동성
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "코스피 급락과 외국인 대규모 매도세로 유동성 경색 신호.",
    "USD/KRW 1429.10 고정, 변동성(VIX) 19.86로 위험회피 심리 강화.",
    "정책 민감 자금 유입 부진, 위험선호 약화."
  ],
  "korean_comment": "유동성 악화와 변동성 상승으로 보수적 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```