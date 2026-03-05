# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-03-05**
- 생성 시각(UTC): `2026-03-05T01:30:38.439847+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 선별적 포지셔닝을 전제로 중립적 입장을 유지합니다.
- **국면 투표**: NEUTRAL=5, RISK_ON=0, RISK_OFF=2
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 노출을 균형 있게 유지합니다.
- [OpsGuidanceLevel.CAUTION/주의] 리스크 한도를 엄격히 유지합니다.
- [OpsGuidanceLevel.AVOID/회피] 과도한 레버리지는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI +0.00% / KOSDAQ +0.00%
- **미국 지수**: S&P500 +0.78% / NASDAQ +1.29% / DOW +0.49%
- **환율/변동성**: USD/KRW 1464.35 (+0.00%) / VIX 21.1
- **시장 요약 노트**: KOSPI 0.00%, USD/KRW 1464.35. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 4.08% / 미2년 3.60% / 2-10 0.48%p / DXY 98.70
- **월간 매크로**: 실업률 4.30% / CPI YoY 2.83% / Core CPI YoY 2.95% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.40% / 기준금리 3.64% / 실질금리 1.79%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: NEUTRAL.
  ↳ 출처: `macro, flow, sector, risk, earnings`
- 공통 근거: snapshot.market_summary.kospi_change_pct.
  ↳ 출처: `breadth, earnings, macro, risk`

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
- 한줄 요약: 섹터 주도주가 불명확해 균형 유지가 낫습니다.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: Sector moves are mixed.
- 핵심 주장: No clear leader.
- 핵심 주장: Maintain balance.

### 리스크
- 한줄 요약: 급격한 리스크는 없어 규율을 유지하세요.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: Risk signals stable.
- 핵심 주장: No acute stress.
- 핵심 주장: Maintain discipline.

### 이익모멘텀
- 한줄 요약: 실적 추정치 변화가 거의 없는 중립적 구간입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀과 추정치 변화가 뚜렷하지 않음.
- 핵심 주장: 시장 전반에 실적 상향 조정 신호 부재.
- 핵심 주장: 단기 헤드라인 영향 외에 구조적 실적 개선 근거 부족.

### 브레드스
- 한줄 요약: 시장 전반의 확산세가 약해 신중한 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: KOSPI와 KOSDAQ 모두 변동성 없이 횡보 중입니다.
- 핵심 주장: 시장 내부 확산도 약화 신호가 뚜렷합니다.
- 핵심 주장: 미국 지수 상승에도 국내 시장 확산은 부진합니다.

### 유동성
- 한줄 요약: 정책 불확실성과 변동성 상승으로 유동성 환경이 보수적입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 달러/원 환율이 고정되어 있고 변동성(VIX)이 21로 높음.
- 핵심 주장: 연준 금리인하 중단 뉴스와 유동성 신호는 보수적 해석 필요.
- 핵심 주장: 정책 불확실성 및 지정학적 리스크로 위험회피 심리 우세.

## 6) 이견 사항
- 국면 태그: 다수=NEUTRAL, 소수=RISK_OFF, 에이전트=[breadth, liquidity]
  - 의미: 소수 의견 국면은 포지션 경계에 영향을 줄 수 있습니다.

## 7) AI 원문 응답 (디버깅/검토용)
### 매크로
(stub or raw response unavailable)
### 수급
(stub or raw response unavailable)
### 섹터
(stub or raw response unavailable)
### 리스크
(stub or raw response unavailable)
### 이익모멘텀
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀과 추정치 변화가 뚜렷하지 않음.",
    "시장 전반에 실적 상향 조정 신호 부재.",
    "단기 헤드라인 영향 외에 구조적 실적 개선 근거 부족."
  ],
  "korean_comment": "실적 추정치 변화가 거의 없는 중립적 구간입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines"
  ],
  "confidence": "MED"
}
```
### 브레드스
```text
{
  "agent_name": "BREADTH/TECHNICAL",
  "core_claims": [
    "KOSPI와 KOSDAQ 모두 변동성 없이 횡보 중입니다.",
    "시장 내부 확산도 약화 신호가 뚜렷합니다.",
    "미국 지수 상승에도 국내 시장 확산은 부진합니다."
  ],
  "korean_comment": "시장 전반의 확산세가 약해 신중한 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.kr.kosdaq_pct",
    "snapshot.phase_two_signals.breadth_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 유동성
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "달러/원 환율이 고정되어 있고 변동성(VIX)이 21로 높음.",
    "연준 금리인하 중단 뉴스와 유동성 신호는 보수적 해석 필요.",
    "정책 불확실성 및 지정학적 리스크로 위험회피 심리 우세."
  ],
  "korean_comment": "정책 불확실성과 변동성 상승으로 유동성 환경이 보수적입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.markets.volatility.vix",
    "snapshot.news_headlines",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```