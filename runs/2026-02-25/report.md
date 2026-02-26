# 데일리 AI 투자위원회

날짜: 2026-02-25
생성 시각: 2026-02-25T00:36:52.189701+00:00

## 합의 결과
위원회는 선별적 모니터링 하에 중립적 스탠스를 유지합니다.

## 핵심 포인트
- 다수 국면 태그: NEUTRAL. (출처: macro, sector)

## AI 한줄 의견
- 매크로: 상승세에도 불안 요인이 적지 않습니다.
- 수급: 상승세에도 불안 요인이 커지고 있습니다.
- 섹터: 코스피 강세에도 불안 요인이 커지고 있습니다.
- 리스크: 시장 고점 논란과 외국인 매도세가 주목됩니다.

## AI 핵심 주장
### 매크로
- 코스피가 사상 최고치에 도달했으나 외국인 매도세가 두드러집니다.
- 시장에 하락 베팅과 고점 경계 심리가 확산되고 있습니다.
### 수급
- 코스피가 6000선에 도달했으나 변동성 확대 신호가 감지됨.
- 외국인 대규모 매도와 하락 베팅 증가가 부담 요인임.
- 단기적으로 조정 가능성에 유의해야 함.
### 섹터
- 코스피가 사상 첫 6000선을 돌파하며 강세를 보이고 있다.
- 외국인과 기관의 매도세가 확대되며 고점 신호가 감지된다.
- 하락 베팅 규모가 커져 단기 변동성 확대 가능성이 높다.
### 리스크
- 코스피 6000 돌파, 사상 최고치 기록
- 외국인 대규모 매도세 지속
- 시장 과열 및 하락 베팅 증가

## AI 원문 응답
### 매크로
```
{
  "agent_name": "MACRO pre-analysis agent",
  "core_claims": [
    "코스피가 사상 최고치에 도달했으나 외국인 매도세가 두드러집니다.",
    "시장에 하락 베팅과 고점 경계 심리가 확산되고 있습니다."
  ],
  "korean_comment": "상승세에도 불안 요인이 적지 않습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.usdkrw",
    "snapshot.news_headlines",
    "snapshot.flow_summary.note"
  ],
  "confidence": "MED"
}
```
### 수급
```
{
  "agent_name": "FLOW pre-analysis agent",
  "core_claims": [
    "코스피가 6000선에 도달했으나 변동성 확대 신호가 감지됨.",
    "외국인 대규모 매도와 하락 베팅 증가가 부담 요인임.",
    "단기적으로 조정 가능성에 유의해야 함."
  ],
  "korean_comment": "상승세에도 불안 요인이 커지고 있습니다.",
  "regime_tag": "RISK_OFF",
  "evidence_ids": [
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.note",
    "snapshot.news_headlines",
    "snapshot.flow_summary.note"
  ],
  "confidence": "HIGH"
}
```
### 섹터
```
{
  "agent_name": "SECTOR",
  "core_claims": [
    "코스피가 사상 첫 6000선을 돌파하며 강세를 보이고 있다.",
    "외국인과 기관의 매도세가 확대되며 고점 신호가 감지된다.",
    "하락 베팅 규모가 커져 단기 변동성 확대 가능성이 높다."
  ],
  "korean_comment": "코스피 강세에도 불안 요인이 커지고 있습니다.",
  "regime_tag": "NEUTRAL",
  "evidence_ids": [
    "snapshot.news_headlines",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.market_summary.note"
  ],
  "confidence": "MED"
}
```
### 리스크
```
{"agent_name": "RISK pre-analysis agent", "core_claims": ["코스피 6000 돌파, 사상 최고치 기록", "외국인 대규모 매도세 지속", "시장 과열 및 하락 베팅 증가"], "korean_comment": "시장 고점 논란과 외국인 매도세가 주목됩니다.", "regime_tag": "RISK_ON", "evidence_ids": ["snapshot.market_summary.note", "snapshot.news_headlines"], "confidence": "MED"}
```

국면 투표: NEUTRAL=2, RISK_ON=1, RISK_OFF=1
요약: 현재 국면은 NEUTRAL로 판단됩니다.

## 이견
- 국면 태그: 다수=NEUTRAL, 소수=None, 에이전트=[none]. 다른 국면 태그의 이견은 없습니다.

## 운영 가이드
- [OpsGuidanceLevel.OK/유지] 관심 종목을 좁게 유지하고 과도한 노출을 피합니다.
- [OpsGuidanceLevel.CAUTION/주의] 포지션 규모를 보수적으로 유지합니다.
- [OpsGuidanceLevel.AVOID/회피] 과도한 레버리지는 피합니다.

## 글로벌 시장
국내: KOSPI +0.00%, KOSDAQ +0.00%
미국: S&P500 +0.77%, NASDAQ +1.04%, DOW +0.76%
환율: USD/KRW 1442.40 (+0.00%)

## 시장 지표
- KOSPI 일일 등락: **+0.00%**
- USD/KRW: **1442.40**
- 요약: KOSPI 0.00%, USD/KRW 1442.40. Headlines loaded. Flows unavailable.

## 수급 (억원, 순매수)
- 외국인: **+0** / 기관: **+0** / 개인: **+0**
- 비고: flows_fetch_failed: unavailable (외국인/기관/개인 순매수는 데이터 없음)

## 한국 수급 (KOSPI/KOSDAQ, 억원 순매수)
- 데이터: unavailable (PyKRX 미설치/실패/휴장일 등)

## 매크로 (요약)
- 일간: 미10년 4.03% / 미2년 3.59% / 2-10 0.44%p
        DXY 97.88 / USDKRW 1441.48 / VIX 19.5
- 월간: 실업률 4.30%, CPI YoY 2.83%, Core CPI YoY 2.95%, PCE YoY 2.90%, PMI n/a
          임금 레벨 37.17, 임금 YoY 3.71%
- 분기: 실질 GDP 24111.83, GDP QoQ 연율 1.40%
- 구조: 기준금리 3.64%, 실질금리 1.77%