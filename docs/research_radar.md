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

## 주간 미래산업 논문 레이더

`config/research_radar_topics.json`에 등록된 미래산업 주제를 대상으로 최근 28일 arXiv 논문을
매주 다시 수집합니다. GPT는 제목·초록 안에서 관련성, 핵심 주장, 반증 방향과 한계를 JSON으로
추출하고 기존 규칙 엔진이 최종 점수와 단계 통과 여부를 계산합니다.

```bash
# 계획만 출력하며 네트워크·GPT 호출·파일 쓰기를 하지 않음
python scripts/run_research_radar_weekly.py

# 실제 수집·GPT 해석·보고서 저장
python scripts/run_research_radar_weekly.py --execute
```

기본 모델은 `gpt-4.1`이며 `RESEARCH_RADAR_LLM_MODEL` 환경변수 또는 `--model`로 바꿀 수
있습니다. `OPENAI_API_KEY`는 기존 프로젝트 설정을 그대로 사용합니다. 주간 예약 진입점인
`scripts/sync_weekly.py`가 대시보드 생성 전에 이 명령을 자동 실행합니다. 일시적으로 제외하려면
`--skip-research-radar`를 사용합니다.

8개 기본 연구영역과 최대 2개의 자유 탐색 슬롯을 운용합니다. 논문 레이더 외에도 주간 산업 뉴스
DB에서 정책·기업 행동을, 산업 사이클 DB에서 시장 확인을 가져옵니다. 당일 정책 뉴스가 부족하면
Google News RSS로 보강하며, 과거 사례는 원문 URL·유사점·차이점·재현 조건을 미리 검증한 목록만
사용합니다. 이 수집기들은 별도의 LLM 호출을 추가하지 않습니다.

산출물은 다음 위치에 저장됩니다.

```text
runs/<as-of>/research_radar/<theme-id>.json
runs/<as-of>/research_radar/<theme-id>.md
```

논문 레이더 결과는 별도 탭을 만들지 않고 `🔭 미래 경제 연구소` 탭에 통합됩니다. 레이더 산출 후
연구 상태와 AI 투자위원회 검토 안건을 갱신하고 대시보드를 다시 생성합니다.

```bash
python scripts/run_future_economy_weekly.py --execute
python scripts/build_dashboard.py
```

과거 시점 재현이나 네트워크 없는 점검에서는 당일 정책 RSS, 정부 원문 API,
DART 공시 수집을 각각 끌 수 있습니다.

```bash
python scripts/run_future_economy_weekly.py --as-of 2026-08-23 \
  --skip-live-policy --skip-official-policy-api --skip-dart-disclosures --execute
```

서로 다른 근거 유형이 2종 이상이면 정식 연구로, 3종 이상이면 AI 투자위원회 검토 안건으로
올라갑니다. 안건은 투자 판단을 위한 참고 자료이며 자동 주문이나 자동매매 지시가 아닙니다.

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
