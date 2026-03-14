# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-03-14**
- 생성 시각(UTC): `2026-03-14T08:10:49.561689+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 선별적 포지셔닝을 전제로 중립적 입장을 유지합니다.
- **국면 투표**: NEUTRAL=1, RISK_ON=0, RISK_OFF=6
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 노출을 균형 있게 유지합니다.
- [OpsGuidanceLevel.CAUTION/주의] 리스크 한도를 엄격히 유지합니다.
- [OpsGuidanceLevel.AVOID/회피] 과도한 레버리지는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -1.72% / KOSDAQ +0.40%
- **미국 지수**: S&P500 -0.61% / NASDAQ -0.93% / DOW -0.26%
- **환율/변동성**: USD/KRW 1496.54 (+0.59%) / VIX 27.2
- **시장 요약 노트**: KOSPI -1.72%, USD/KRW 1496.54. Headlines loaded. Flows loaded.
- **수급 요약**: 외국인 -15331억 / 기관 -7908억 / 개인 +23187억
- **일간 매크로**: 미10년 4.28% / 미2년 3.60% / 2-10 0.68%p / DXY 100.50
- **월간 매크로**: 실업률 4.40% / CPI YoY 2.66% / Core CPI YoY 2.73% / PMI n/a
- **분기/구조**: GDP QoQ 연율 0.70% / 기준금리 3.64% / 실질금리 1.92%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: NEUTRAL.
  ↳ 출처: `macro, flow, risk, earnings, breadth`
- 공통 근거: snapshot.flow_summary.foreign_net.
  ↳ 출처: `breadth, earnings, flow, liquidity, macro`
- Stability guardrail applied from confidence-weighted votes and cumulative context.
  ↳ 출처: `regime_tuner`

## 5) AI 에이전트 의견
### 매크로 담당자
- 한줄 요약: 변동성 경고가 있어 방어적 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: Macro tone is cautious.
- 핵심 주장: Volatility noted.
- 핵심 주장: Flow demand is weak.

### 수급 담당자
- 한줄 요약: 수급 역풍이 커져 방어적 대응이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: 외국인+기관 순매도가 우세합니다.
- 핵심 주장: 수급 역풍이 확대되고 있습니다.
- 핵심 주장: 방어 비중이 유리합니다.

### 섹터 담당자
- 한줄 요약: 섹터 주도주가 불명확해 균형 유지가 낫습니다.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: Sector moves are mixed.
- 핵심 주장: No clear leader.
- 핵심 주장: Maintain balance.

### 리스크 담당자
- 한줄 요약: 리스크 신호가 높아 노출 축소가 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: Risk signals elevated.
- 핵심 주장: Headline risk rising.
- 핵심 주장: Reduce exposure.

### 이익모멘텀 담당자
- 한줄 요약: 이익 모멘텀이 약해져 방어적 접근이 유리합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: 실적/가이던스 하향 신호가 누적됩니다.
- 핵심 주장: 이익 추정치 둔화 가능성이 커졌습니다.
- 핵심 주장: 밸류에이션 리레이팅 압력이 발생할 수 있습니다.

### 브레드스 담당자
- 한줄 요약: 브레드스 약화와 변동성 상승으로 보수적 대응이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: 지수 확산이 약화되어 추세 신뢰도가 낮습니다.
- 핵심 주장: 변동성 레짐이 위험자산에 불리한 구간입니다.
- 핵심 주장: 손절·비중관리 규칙을 강화할 필요가 있습니다.

### 유동성 담당자
- 한줄 요약: 유동성 여건이 긴축적이라 보수적 운용이 유리합니다.
- 국면 태그: RISK_OFF / 신뢰도: MED
- 핵심 주장: 달러·실질금리 환경이 위험자산에 부담으로 작용합니다.
- 핵심 주장: 유동성 여건이 타이트해 밸류에이션 할인 요인이 큽니다.
- 핵심 주장: 정책/금리 민감 자산 비중 축소가 필요합니다.

## 6) 에이전트 회의록(1라운드)
- 비활성화됨 (USE_AGENT_DEBATE=1 설정 시 활성화)

## 7) 이견 사항
- 국면 태그: 다수=RISK_OFF, 소수=NEUTRAL, 에이전트=[sector]
  - 의미: 소수 의견 국면은 포지션 경계에 영향을 줄 수 있습니다.

## 8) AI 원문 응답 (디버깅/검토용)
### 매크로 담당자
(stub or raw response unavailable)
### 수급 담당자
(stub or raw response unavailable)
### 섹터 담당자
(stub or raw response unavailable)
### 리스크 담당자
(stub or raw response unavailable)
### 이익모멘텀 담당자
(stub or raw response unavailable)
### 브레드스 담당자
(stub or raw response unavailable)
### 유동성 담당자
(stub or raw response unavailable)