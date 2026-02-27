# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-02-27**
- 생성 시각(UTC): `2026-02-27T06:42:09.022944+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.
- **국면 투표**: NEUTRAL=3, RISK_ON=0, RISK_OFF=4
- **다수 국면**: RISK_OFF

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] Keep exposure focused on resilience.
- [OpsGuidanceLevel.CAUTION/주의] Favor defensive positioning.
- [OpsGuidanceLevel.AVOID/회피] Avoid high-beta risk assets.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -0.65% / KOSDAQ +0.31%
- **미국 지수**: S&P500 -0.54% / NASDAQ -1.18% / DOW +0.03%
- **환율/변동성**: USD/KRW 1429.10 (+0.00%) / VIX 18.6
- **시장 요약 노트**: KOSPI -0.65%, USD/KRW 1429.10. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 4.02% / 미2년 3.59% / 2-10 0.43%p / DXY 97.73
- **월간 매크로**: 실업률 4.30% / CPI YoY 2.83% / Core CPI YoY 2.95% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.40% / 기준금리 3.64% / 실질금리 1.74%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: RISK_OFF.
  ↳ 출처: `flow, sector, earnings, liquidity`
- 공통 근거: snapshot.news_headlines.
  ↳ 출처: `earnings, flow, liquidity, macro, risk`

## 5) AI 에이전트 의견
### 매크로
- 한줄 요약: 거시는 균형적이며 선택적 대응이 적절합니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: Macro tone is balanced.
- 핵심 주장: No major shocks.
- 핵심 주장: Stay selective.

### 수급
- 한줄 요약: 외국인 매도와 변동성 확대가 단기 조정 신호입니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피가 하락 전환하며 외국인 매도세가 부각되고 있습니다.
- 핵심 주장: 시장 변동성(VIX)이 상승하며 투자심리가 위축되고 있습니다.
- 핵심 주장: 유동성 신호는 양호하나, 단기적으로 조정 국면입니다.

### 섹터
- 한줄 요약: 외국인 매도와 시장 불안이 뚜렷하게 나타납니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피가 최근 고점 논란과 외국인 대규모 순매도로 조정 국면에 진입했습니다.
- 핵심 주장: 시장에는 극단적 공포 심리가 확산되고 있습니다.
- 핵심 주장: 단기적으로 위험회피 심리가 우세합니다.

### 리스크
- 한줄 요약: 단기적으로 경계감이 높아진 상황입니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 코스피가 0.65% 하락하며 단기 조정세를 보임
- 핵심 주장: 외국인 대규모 순매도와 고점 경계감이 부각됨

### 이익모멘텀
- 한줄 요약: 실적 추정치 하향 조정이 본격화될 수 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 실적 모멘텀 둔화 신호가 뚜렷하다.
- 핵심 주장: 외국인 매도세와 고점 인식이 실적 전망 하향 압력으로 작용.
- 핵심 주장: 단기 반등보다는 실적 추정치 하향 조정이 우세할 전망.

### 브레드스
- 한줄 요약: 브레드스 신호가 혼재되어 중립 대응이 합리적입니다.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: 추세 확산과 역추세 신호가 공존합니다.
- 핵심 주장: 기술적 우위가 명확하지 않습니다.
- 핵심 주장: 방향 확정 전까지 균형 비중이 적절합니다.

### 유동성
- 한줄 요약: 정책 민감 유동성 환경이 악화되어 보수적 접근이 필요합니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 달러/원 환율이 1429원으로 고정되어 유동성 경계감이 높음.
- 핵심 주장: 외국인 대규모 순매도와 변동성(VIX 18.6) 상승으로 정책 민감 리스크 확대.
- 핵심 주장: 코스피 하락(-0.65%)과 유동성 신호 약화로 위험회피 심리 우세.

## 6) 이견 사항
- 국면 태그: 다수=RISK_OFF, 소수=NEUTRAL, 에이전트=[macro, risk, breadth]
  - 의미: 소수 의견 국면은 포지션 경계에 영향을 줄 수 있습니다.

## 7) AI 원문 응답 (디버깅/검토용)
### 매크로
(stub or raw response unavailable)
### 수급
```text
{
  "agent_name": "FLOW pre-analysis agent",
  "core_claims": [
    "코스피가 하락 전환하며 외국인 매도세가 부각되고 있습니다.",
    "시장 변동성(VIX)이 상승하며 투자심리가 위축되고 있습니다.",
    "유동성 신호는 양호하나, 단기적으로 조정 국면입니다."
  ],
  "korean_comment": "외국인 매도와 변동성 확대가 단기 조정 신호입니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 섹터
```text
{
  "agent_name": "SECTOR",
  "core_claims": [
    "코스피가 최근 고점 논란과 외국인 대규모 순매도로 조정 국면에 진입했습니다.",
    "시장에는 극단적 공포 심리가 확산되고 있습니다.",
    "단기적으로 위험회피 심리가 우세합니다."
  ],
  "korean_comment": "외국인 매도와 시장 불안이 뚜렷하게 나타납니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.kr.kospi_pct"
  ],
  "confidence": "HIGH"
}
```
### 리스크
```text
{
  "agent_name": "RISK_pre_analysis_agent",
  "core_claims": [
    "코스피가 0.65% 하락하며 단기 조정세를 보임",
    "외국인 대규모 순매도와 고점 경계감이 부각됨"
  ],
  "korean_comment": "단기적으로 경계감이 높아진 상황입니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.kr.kospi_pct"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 둔화 신호가 뚜렷하다.",
    "외국인 매도세와 고점 인식이 실적 전망 하향 압력으로 작용.",
    "단기 반등보다는 실적 추정치 하향 조정이 우세할 전망."
  ],
  "korean_comment": "실적 추정치 하향 조정이 본격화될 수 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.phase_two_signals.earnings_signal_score"
  ],
  "confidence": "HIGH"
}
```
### 브레드스
(stub or raw response unavailable)
### 유동성
```text
{
  "agent_name": "LIQUIDITY/POLICY",
  "core_claims": [
    "달러/원 환율이 1429원으로 고정되어 유동성 경계감이 높음.",
    "외국인 대규모 순매도와 변동성(VIX 18.6) 상승으로 정책 민감 리스크 확대.",
    "코스피 하락(-0.65%)과 유동성 신호 약화로 위험회피 심리 우세."
  ],
  "korean_comment": "정책 민감 유동성 환경이 악화되어 보수적 접근이 필요합니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.markets.kr.kospi_pct",
    "snapshot.markets.volatility.vix",
    "snapshot.phase_two_signals.liquidity_signal_score"
  ],
  "confidence": "HIGH"
}
```