# Research-to-Market Radar

논문이 실제 산업·투자 신호로 번지는 과정을 다음 다섯 단계로 추적하는
증거 기반 도구입니다.

1. 연구 검증
2. 인재 이동·창업
3. 자본 형성
4. 인프라 병목
5. 상장사 실적 확인

현재 MVP는 웹을 자동 검색하거나 LLM으로 사실을 생성하지 않습니다. 사람이
검토한 근거 JSON을 입력으로 받아 같은 입력에는 항상 같은 점수와 보고서를
생성합니다. 수집·추출 자동화는 이 결정론적 코어 위에 별도 계층으로 붙이는
것이 안전합니다.

## 빠른 실행

Transformer 예제를 쓰기 없이 확인합니다.

```bash
python scripts/run_research_radar.py
```

JSON과 Markdown을 생성합니다.

```bash
python scripts/run_research_radar.py --execute
```

산출물은 다음 위치에 저장됩니다.

```text
runs/<as-of>/research_radar/<theme-id>.json
runs/<as-of>/research_radar/<theme-id>.md
```

기존 정적 대시보드의 `🔬 연구→시장` 탭에도 표시하려면 레이더 산출 후
대시보드를 다시 생성합니다.

```bash
python scripts/build_dashboard.py
```

과거 시점으로 되감으면 `known_at`이 기준일보다 늦은 근거가 자동 제외됩니다.

```bash
python scripts/run_research_radar.py \
  --input config/research_radar_transformer.json \
  --as-of 2018-12-31
```

## 입력 계약

최상위 스키마 버전은 `research-radar-input-v1`입니다.

```json
{
  "schema_version": "research-radar-input-v1",
  "as_of": "2024-12-20",
  "theme": {
    "theme_id": "example-theme",
    "name": "예제 테마",
    "thesis": "검증할 시장 전달 가설"
  },
  "evidence": [],
  "public_companies": [],
  "limitations": []
}
```

각 근거에는 다음 필드가 필요합니다.

| 필드 | 의미 |
|---|---|
| `evidence_id` | 파일 안에서 유일한 소문자 slug |
| `stage` | 다섯 단계 중 하나 |
| `event_type` | paper, funding, earnings 같은 사건 유형 |
| `title`, `claim` | 출처 제목과 그 출처가 직접 뒷받침하는 주장 |
| `event_date` | 사건이 발생하거나 발표된 날짜 |
| `known_at` | 시스템 또는 당시 관찰자가 이 사실을 알 수 있게 된 날짜 |
| `source_url`, `source_name` | 검증 가능한 원문 링크와 출처명 |
| `source_kind` | 출처 품질 분류 |
| `direction` | `positive`, `neutral`, `negative` |
| `strength` | 해당 단계에 대한 근거 강도, 0~1 |

허용되는 단계 값은 다음과 같습니다.

```text
research_validation
talent_mobility
capital_formation
infrastructure_bottleneck
earnings_confirmation
```

허용되는 출처 유형은 다음과 같습니다.

```text
academic_primary
regulatory_filing
company_filing
company_release
reputable_media
secondary_analysis
other
```

상장사 연결은 반드시 하나 이상의 `evidence_id`를 참조해야 합니다. 연결 유형은
`direct`, `enabler`, `adjacent`, `speculative` 중 하나입니다. 근거 없는 종목명이나
LLM이 추론한 티커를 자동 삽입하지 않습니다.

## 점수 해석

- 단계 점수는 `direction × strength × source_reliability`의 평균입니다.
- 확신도는 독립 출처 도메인 수, 출처 품질, 근거 간 일치도를 따로 반영합니다.
- 단계 통과 기준은 점수 60 이상, 확신도 50 이상입니다.
- 현재 단계는 앞 단계부터 순서대로 통과한 마지막 단계입니다. 뒤 단계의 자료가
  있어도 중간 고리가 비어 있으면 그 단계를 건너뛰지 않습니다.
- 체인 성숙도는 다섯 단계 점수의 고정 가중합입니다.
- 상장사 연결 강도는 근거와 기업의 연결 정도일 뿐 기대수익률이나 밸류에이션
  점수가 아닙니다.

가중치는 코드와 JSON 산출물의 `methodology`에 함께 기록됩니다. 보고서만 보더라도
어떤 규칙으로 계산됐는지 재현할 수 있습니다.

## 운영 원칙

- 시점 오염 방지: `known_at <= as_of`만 사용합니다.
- 근거 우선: URL, 날짜, 직접 주장 없이 점수를 만들지 않습니다.
- 점수와 확신도 분리: 강한 1차 자료 한 건과 여러 독립 출처의 교차검증을 구분합니다.
- 반증 표시: 부정 근거가 전혀 없으면 데이터 공백으로 경고합니다.
- 투자 판단 분리: 가격, 밸류에이션, 시장 기대치가 없으면 매수·매도 결론을 내리지 않습니다.

## 테스트

```bash
python -m unittest tests.test_research_radar tests.test_run_research_radar_cli -v
```

테스트는 스키마 검증, 미래 근거 제외, 반증 충돌, 상장사 근거 참조, Markdown
렌더링, dry-run 무변경, 반복 실행의 바이트 단위 결정성을 확인합니다.
