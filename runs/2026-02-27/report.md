# 데일리 AI 투자위원회 리포트

- 시장 기준일: **2026-02-27**
- 생성 시각(UTC): `2026-02-27T05:04:53.317371+00:00`

## 1) 한눈에 보기
- **위원회 합의**: 위원회는 선별적 포지셔닝을 전제로 중립적 입장을 유지합니다.
- **국면 투표**: NEUTRAL=5, RISK_ON=0, RISK_OFF=2
- **다수 국면**: NEUTRAL

## 2) 운영 가이드
- [OpsGuidanceLevel.OK/유지] 노출을 균형 있게 유지합니다.
- [OpsGuidanceLevel.CAUTION/주의] 리스크 한도를 엄격히 유지합니다.
- [OpsGuidanceLevel.AVOID/회피] 과도한 레버리지는 피합니다.

## 3) 시장/매크로 스냅샷
- **국내 지수**: KOSPI -0.44% / KOSDAQ +0.46%
- **미국 지수**: S&P500 -0.54% / NASDAQ -1.18% / DOW +0.03%
- **환율/변동성**: USD/KRW 1429.10 (+0.00%) / VIX 18.6
- **시장 요약 노트**: KOSPI -0.44%, USD/KRW 1429.10. Headlines loaded. Flows unavailable.
- **수급 요약**: 외국인 +0억 / 기관 +0억 / 개인 +0억
- **일간 매크로**: 미10년 4.02% / 미2년 3.59% / 2-10 0.43%p / DXY 97.64
- **월간 매크로**: 실업률 4.30% / CPI YoY 2.83% / Core CPI YoY 2.95% / PMI n/a
- **분기/구조**: GDP QoQ 연율 1.40% / 기준금리 3.64% / 실질금리 1.74%

## 4) 위원회 핵심 포인트
- 다수 국면 태그: NEUTRAL.
  ↳ 출처: `macro, flow, risk, earnings, breadth`
- 공통 근거: snapshot.news_headlines.
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
- 한줄 요약: 외국인 매도세와 대외 변수로 시장 불확실성이 커졌습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 코스피가 최근 고점 논란과 외국인 대규모 순매도로 조정 국면에 진입했습니다.
- 핵심 주장: 엔비디아 급락 등 대외 악재가 투자심리 위축에 영향을 주고 있습니다.
- 핵심 주장: 단기적으로 변동성 확대와 조정 위험이 높아진 상황입니다.

### 리스크
- 한줄 요약: 시장에 뚜렷한 위험 신호는 아직 감지되지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 코스피가 소폭 하락했으나 변동성은 제한적입니다.
- 핵심 주장: 외국인 매도세가 있지만 리밸런싱 성격이 강합니다.
- 핵심 주장: 시장 전반에 극단적 위험 신호는 없습니다.

### 이익모멘텀
- 한줄 요약: 실적 추정치 변화는 아직 뚜렷하지 않습니다.
- 국면 태그: NEUTRAL / 신뢰도: MED
- 핵심 주장: 실적 모멘텀 둔화 신호가 뚜렷하지 않음
- 핵심 주장: 외국인 매도세는 일시적 리밸런싱 가능성
- 핵심 주장: 지속적 실적 하향 조정 신호는 부족

### 브레드스
- 한줄 요약: 브레드스 신호가 혼재되어 중립 대응이 합리적입니다.
- 국면 태그: NEUTRAL / 신뢰도: LOW
- 핵심 주장: 추세 확산과 역추세 신호가 공존합니다.
- 핵심 주장: 기술적 우위가 명확하지 않습니다.
- 핵심 주장: 방향 확정 전까지 균형 비중이 적절합니다.

### 유동성
- 한줄 요약: 유동성 및 정책 환경이 위험회피로 기울고 있습니다.
- 국면 태그: RISK_OFF / 신뢰도: HIGH
- 핵심 주장: 달러/원 환율이 고정되어 있으나 외국인 대규모 순매도와 변동성 상승이 확인됨.
- 핵심 주장: VIX가 18 이상으로 상승하며 위험회피 심리가 강화되고 있음.
- 핵심 주장: 정책금리와 실질금리 모두 높아 유동성 환경이 보수적임.

## 6) 이견 사항
- 국면 태그: 다수=NEUTRAL, 소수=RISK_OFF, 에이전트=[sector, liquidity]
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
    "코스피가 최근 고점 논란과 외국인 대규모 순매도로 조정 국면에 진입했습니다.",
    "엔비디아 급락 등 대외 악재가 투자심리 위축에 영향을 주고 있습니다.",
    "단기적으로 변동성 확대와 조정 위험이 높아진 상황입니다."
  ],
  "korean_comment": "외국인 매도세와 대외 변수로 시장 불확실성이 커졌습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.us.nasdaq_pct",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "HIGH"
}
```
### 리스크
```text
{
  "agent_name": "RISK pre-analysis agent",
  "core_claims": [
    "코스피가 소폭 하락했으나 변동성은 제한적입니다.",
    "외국인 매도세가 있지만 리밸런싱 성격이 강합니다.",
    "시장 전반에 극단적 위험 신호는 없습니다."
  ],
  "korean_comment": "시장에 뚜렷한 위험 신호는 아직 감지되지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix"
  ],
  "confidence": "MED"
}
```
### 이익모멘텀
```text
{
  "agent_name": "EARNINGS-REVISION",
  "core_claims": [
    "실적 모멘텀 둔화 신호가 뚜렷하지 않음",
    "외국인 매도세는 일시적 리밸런싱 가능성",
    "지속적 실적 하향 조정 신호는 부족"
  ],
  "korean_comment": "실적 추정치 변화는 아직 뚜렷하지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.news_headlines",
    "snapshot.phase_two_signals.earnings_signal_score",
    "snapshot.market_summary.note"
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
    "달러/원 환율이 고정되어 있으나 외국인 대규모 순매도와 변동성 상승이 확인됨.",
    "VIX가 18 이상으로 상승하며 위험회피 심리가 강화되고 있음.",
    "정책금리와 실질금리 모두 높아 유동성 환경이 보수적임."
  ],
  "korean_comment": "유동성 및 정책 환경이 위험회피로 기울고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.markets.volatility.vix",
    "snapshot.macro.structural.real_rate"
  ],
  "confidence": "HIGH"
}
```