# Daily AI Investment Committee (MVP v1)

이 프로젝트는 **하루 1회** AI 에이전트들의 사전 분석 결과를 모아 **규칙 기반 합의(Consensus)** 리포트를 만드는 오프라인 파이프라인입니다.  
실시간 알림/장중 분석/챗봇은 없으며, 사용자는 **아침에 생성된 리포트만 읽습니다**.

## 핵심 원칙
- 모든 산출물은 **스키마(Pydantic)** 검증을 통과해야 합니다.
- 에이전트는 **서로 직접 대화하지 않습니다**.
- 합의 규칙은 **코드로 강제**됩니다.
- 서비스가 아닌 **배치 파이프라인**이며, 확장성과 유지보수를 최우선으로 합니다.

---

## 전체 흐름 (매일 1회)

```
Snapshot 생성
  -> Pre-Analysis (에이전트 Stance)
    -> Chair 합의 (CommitteeResult)
      -> Report 생성/저장
```

### 1) Snapshot
하루 회의에서 공유하는 “단일 사실 패킷”입니다.
- 시장 요약/수급 요약/섹터/뉴스/워치리스트 포함
- 실패해도 반드시 반환되며, **note**에 실패 사유 기록

### 2) Stance
각 에이전트의 사전 분석 결과입니다.
- agent_name, 핵심 주장, 국면 태그, 근거 경로, 신뢰도
- 에이전트는 서로 대화하지 않음

### 3) CommitteeResult
Chair가 규칙 기반으로 합의를 도출한 결과입니다.
- consensus: 단일 문장
- key_points: 근거 출처 포함
- disagreements: minority 정보 포함
- ops_guidance: OK/CAUTION/AVOID 3단계

### 4) Report
Snapshot + Stance + CommitteeResult를 묶은 최종 리포트입니다.

---

## 디렉터리 구조

```
committee/
  schemas/      # 스키마 정의 (Snapshot, Stance, CommitteeResult)
  agents/       # Stub 에이전트 (Macro/Flow/Sector/Risk) + Chair
  core/         # 파이프라인/검증/리포트/저장
  tools/        # 데이터 수집 Provider 인터페이스 및 구현
  adapters/     # 외부 연동 (Telegram sender)

scripts/        # 실행 스크립트
runs/           # 날짜별 아카이브 (YYYY-MM-DD)
reports/        # JSON 리포트 (보조 출력)
```

---

## 주요 모듈 설명

### `committee/schemas/`
- **snapshot.py**: Snapshot 구조 (market_summary, flow_summary, headlines 등)
- **stance.py**: Stance 구조 (agent_name, core_claims, regime_tag 등)
- **committee_result.py**: 합의 결과 구조 (consensus, key_points, disagreements, ops_guidance)

### `committee/agents/`
- **macro_stub.py / flow_stub.py / sector_stub.py / risk_stub.py**  
  단순 if/else 규칙으로 Stance 생성
- **chair_stub.py**  
  다수/소수 태그를 계산해 합의 결과 생성

### `committee/core/`
- **snapshot_builder.py**  
  `build_snapshot_real()`로 실데이터 시도 → 실패 시 fallback  
  실패 사유는 note에 기록됨
- **pipeline.py**  
  Snapshot → Stances → CommitteeResult → Report 생성
- **validators.py**  
  스키마/길이 제한/금지 문구/티커 검증 등 안전장치
- **report_renderer.py**  
  JSON + Markdown 리포트 생성
- **storage.py**  
  실행 결과를 `runs/YYYY-MM-DD/`에 아카이브 저장

### `committee/tools/`
- **providers.py**: IDataProvider 인터페이스 정의
- **http_provider.py**: 공개 API로 실데이터 시도 (실패 시 reason 반환)
- **fallback_provider.py**: 항상 기본값 반환

### `committee/adapters/`
- **telegram_sender.py**  
  텔레그램 전송 (토큰 없으면 콘솔 출력).  
  길이 3500자 초과 시 분할 전송.

---

## 실행 방법

### 1) 로컬 실행 (디버그용)
```
python scripts/run_local.py
```

### 2) 야간 실행 (자동화 배치)
```
python scripts/run_nightly.py
```
- 결과 저장 경로: `runs/YYYY-MM-DD/`

### 3) 아침 발송 (텔레그램 또는 콘솔)
```
python scripts/send_morning.py
```
기본은 **브리프(지표 요약)만** 발송합니다. 상세 `report.md`까지 붙이려면 아래 환경 변수를 켜세요.

---

## 에이전트 모델 프로필 (GPT 기본 + 로컬 확장)

각 에이전트별 추천 모델은 `committee/agents/model_profiles.py`에 고정되어 있습니다.
기본은 GPT(OpenAI) 프로필이고, 나중에 비용 절감을 위해 로컬 무료 모델 프로필로 즉시 전환할 수 있습니다.

- 기본(권장): `AGENT_MODEL_BACKEND=openai`
- 로컬 확장: `AGENT_MODEL_BACKEND=local` (또는 `hf`, `ollama`)

현재 권장 매핑:
- macro: `gpt-4.1` → 로컬 대안 `Qwen/Qwen2.5-32B-Instruct`
- flow: `gpt-4.1-mini` → 로컬 대안 `Qwen/Qwen2.5-14B-Instruct`
- sector: `gpt-4.1-mini` → 로컬 대안 `meta-llama/Llama-3.1-8B-Instruct`
- risk: `gpt-4.1` → 로컬 대안 `Qwen/Qwen2.5-32B-Instruct`

### Agent에 LLM 붙이기 (실행)
기본값은 stub 에이전트이며, 아래 환경 변수를 켜면 LLM 기반 pre-analysis를 사용합니다.

```bash
export USE_LLM_AGENTS=1
export AGENT_MODEL_BACKEND=openai
export LLM_TEMPERATURE=0.1
python scripts/run_local.py
```

```powershell
# Windows PowerShell
$env:USE_LLM_AGENTS = "1"
$env:AGENT_MODEL_BACKEND = "openai"
$env:LLM_TEMPERATURE = "0.1"
python scripts/run_local.py
```

야간 배치(`scripts/run_nightly.py`)도 동일한 환경 변수(`USE_LLM_AGENTS`, `AGENT_MODEL_BACKEND`, `LLM_TEMPERATURE`)를 읽어 pre-analysis 단계에 반영합니다.

### 실행 중간 로그 + AI 응답 추적 로그
`run_local.py`/`run_nightly.py` 실행 시 단계별 진행 로그를 출력합니다.

또한 LLM 사용 시(또는 스텁 fallback 발생 시) 에이전트 응답을 JSONL로 누적 저장합니다.
- 기본 경로: `runs/YYYY-MM-DD/llm_traces.jsonl`
- 재지정: `LLM_TRACE_PATH=/custom/path/llm_traces.jsonl`

로그 이벤트 예시:
- `pipeline_stage`: 스냅샷/stance/committee/저장 단계 상태
- `llm_agent_response`: agent/model/system_prompt/user_prompt/raw_response/parsed/fallback 여부

### API Key 등록 방법 (수정 용이)
OpenAI 호환 설정은 환경 변수만 바꾸면 되도록 구성했습니다.

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 기본값
```

```powershell
# Windows PowerShell
setx OPENAI_API_KEY "sk-..."
setx OPENAI_BASE_URL "https://api.openai.com/v1"
```

- 키 로딩: `committee/tools/openai_chat.py`
- 모델 매핑 수정: `committee/agents/model_profiles.py`
- Agent별 system prompt 수정: `committee/agents/system_prompts.py`

`get_system_prompt(agent, snapshot)`가 실행 시점 Snapshot의 지수/환율/VIX/market note/flow note/최대 20개 헤드라인을 system prompt에 포함합니다.

### Agent별 예시 System Prompt
실제 프롬프트 원문은 `committee/agents/system_prompts.py`에 있으며, 예시는 다음과 같습니다.

- Macro: "Be conservative, explicitly acknowledge uncertainty..."
- Flow: "Map numeric flow context to directional interpretation with stable logic..."
- Sector: "Perform keyword/sector signal classification..."
- Risk: "Precision is critical: avoid false alarms and overreaction..."

## 환경 변수 (Telegram)

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...          # 한 명: 하나만. 여러 명/그룹: 쉼표로 구분 (예: 123,-456,789)
```

없으면 콘솔 출력으로 대체합니다. 여러 사람/그룹에 보내려면 `TELEGRAM_CHAT_ID`에 chat ID를 쉼표로 나열하면 됩니다.

### Windows에서 `setx`로 설정하기 (PowerShell/CMD)

```powershell
setx TELEGRAM_BOT_TOKEN "봇토큰"
setx TELEGRAM_CHAT_ID "123456789,-987654321"   # 여러 명/그룹이면 쉼표로
```

설정 후 **새 터미널(또는 Cursor 재시작)**부터 적용됩니다.

---

## 환경 변수 (데이터)

### FRED (월간/분기/구조 지표)
FRED 기반 지표를 쓰려면 API 키가 필요합니다.

```powershell
setx FRED_API_KEY "32자리_키"
```

### 아침 발송에 상세 리포트 포함 (옵션)
기본은 브리프만 보내고, 상세 `report.md`는 제외합니다. 상세까지 보내려면 실행 시 옵션을 붙이세요.

```powershell
python scripts/send_morning.py --include-report
```

---

## 데이터 소스 (스냅샷)
- **시장 지표**: KOSPI 등락률(Yahoo Finance), USD/KRW(무료 환율 API) 사용.
- **수급(외국인/기관/개인)**:
  - 스냅샷/리포트 구조는 준비되어 있으며, **데이터 소스만 교체 가능한 구조**입니다.
  - 현재 기본값은 `unavailable`로 처리됩니다(파이프라인 안정성/속도 우선).
  - **KRX(best-effort) 연동은 옵션**입니다. KRX 화면 식별자(`bld`)가 바뀌면 실패할 수 있어 기본 OFF입니다.
    - 켜기: `KOREAN_FLOW_SOURCE=KRX`
    - 끄기(기본): `KOREAN_FLOW_SOURCE=NONE`
  - 향후 **키움 API(OpenAPI 등)** 로 교체해도 `Snapshot`/`report.md`/DB 구조는 그대로 재사용합니다.
- **PMI(제조업)**: FRED의 ISM 시리즈가 제거되어, 현재는 ISM 공개 페이지(`go.weareism.org`)에서 최신 PMI를 best-effort로 추출합니다. 값이 비현실적(대략 30~70 범위 밖)이면 FAIL 처리합니다.

---

## DB (SQLite) — 저장/조회/마이그레이션

### DB 파일 위치
- `data/investment.db`
- 파이프라인 실행 시 자동 생성/업데이트됩니다.

### 자주 나는 에러
- **`unable to open database file`**:
  - 현재 작업 폴더가 프로젝트 루트인지 확인
  - `data/` 폴더가 없으면 생성: `mkdir data`

### sqlite3 CLI가 없을 때(Windows)
- 꼭 설치할 필요는 없고 파이썬으로 조회 가능합니다.
- 그래도 CLI가 필요하면:

```powershell
winget install SQLite.SQLite
```

### 테이블 목록/스키마 보기
sqlite3가 있을 때:

```powershell
sqlite3 .\data\investment.db ".tables"
sqlite3 .\data\investment.db "PRAGMA table_info(daily_macro);"
```

sqlite3가 없을 때(파이썬):

```powershell
python -c "import sqlite3; c=sqlite3.connect(r'.\\data\\investment.db'); print([r[0] for r in c.execute(\"select name from sqlite_master where type='table' order by name\").fetchall()]); c.close()"
```

### 주요 테이블 (요약)
- **`market_daily`**: 글로벌 지수/FX(일간)
- **`market_flow_daily`**: 수급(일간)
- **`daily_macro`**: 일간 매크로(금리/스프레드/VIX/DXY/환율 + 구조 컬럼 포함)
- **`monthly_macro`**: 월간 매크로(실업률, 물가 YoY, PMI, 임금 level/YoY)
- **`quarterly_macro`**: 분기 매크로(실질 GDP, QoQ 연율)

### 조회 예시

```powershell
sqlite3 .\data\investment.db "SELECT date, us10y, us2y, spread_2_10, vix, dxy, usdkrw, fed_funds_rate, real_rate FROM daily_macro ORDER BY date DESC LIMIT 5;"
sqlite3 .\data\investment.db "SELECT date, unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi, wage_level, wage_yoy FROM monthly_macro ORDER BY date DESC LIMIT 5;"
sqlite3 .\data\investment.db "SELECT date, real_gdp, gdp_qoq_annualized FROM quarterly_macro ORDER BY date DESC LIMIT 5;"
```

### 0.0 → NULL 정리(레거시 마이그레이션)
과거 placeholder 0.0이 들어간 경우를 NULL로 정리하는 1회 스크립트:

```powershell
python scripts/migrate_db_nulls.py
```

---

## Snapshot 상태(status) 출력
실행 스크립트가 `snapshot sources status: ...` 형태로 소스 상태를 보여줍니다.
- **OK**: 수집 성공
- **FAIL**: 수집 실패(값은 snapshot에서 fallback일 수 있음, DB에는 NULL 저장)


---

## 저장 산출물 (runs/YYYY-MM-DD/)
- `snapshot.json`
- `stances.json`
- `committee_result.json`
- `report.md`

---

## 설계 의도 요약
- **안정성 우선**: 데이터 수집 실패 시에도 파이프라인 중단 없음
- **명확한 계약**: 스키마로 모든 출력 강제
- **확장 용이성**: Provider/Agent를 쉽게 추가 가능

---

## 다음 확장 지점
- `tools/`에 실제 데이터 소스 추가
- `agents/`에 실제 LLM 기반 에이전트 추가
- `chair_stub.py`의 합의 로직 고도화 (규칙 기반 유지 가능)

---

## 작업 히스토리 (Changelog)

### 2026-02-14 (오늘)
- **수급 출력 구조 추가**: `report.md`에 `## 한국 수급 (KOSPI/KOSDAQ, 억원 순매수)` 섹션 출력(데이터 없으면 unavailable 표시).
- **스냅샷 스키마 확장**: `Snapshot.korean_market_flow`(옵션) 추가로 KOSPI/KOSDAQ × 개인/외국인/기관 순매수 구조 저장 가능.
- **수급 Provider 실험/정리**
  - `PyKRX` 설치 이슈(Python 3.13에서 `numpy<2.0` 제약으로 빌드 실패) 확인.
  - `KRX POST(getJsonData.cmd)` 기반 best-effort 모듈 추가: `committee/tools/krx_market_flow_provider.py`
  - 기본 실행 속도/안정성 위해 **기본 OFF + 환경변수 토글**로 전환: `KOREAN_FLOW_SOURCE=KRX|NONE`
- **검증 안정화**: KRX 내부 토큰(`STK/KSQ/MDC` 등)로 파이프라인이 멈추지 않도록 예외 토큰/메모 문자열 sanitize 적용.

---

## 파일별 상세 설명 (Java/C 개발자 관점)

아래는 **각 Python 파일을 Java/C의 “클래스/모듈”처럼** 이해하도록 정리한 설명입니다.

### `committee/schemas/snapshot.py`
- **역할**: `Snapshot` DTO 정의
- **주요 클래스**
  - `MarketSummary`: 시장 요약 (note, kospi_change_pct, usdkrw)
  - `FlowSummary`: 수급 요약 (note, foreign_net, institution_net, retail_net)
  - `Snapshot`: 최상위 공유 데이터 구조
- **특징**: `extra=forbid`로 스키마 외 필드 금지

### `committee/schemas/stance.py`
- **역할**: `Stance` DTO 정의
- **주요 클래스**
  - `AgentName`, `RegimeTag`, `ConfidenceLevel`: Enum
  - `Stance`: 에이전트 사전 분석 결과
- **핵심 필드**
  - `agent_name`, `core_claims`, `regime_tag`, `evidence_ids`, `confidence`

### `committee/schemas/committee_result.py`
- **역할**: 합의 결과 DTO 정의
- **주요 클래스**
  - `KeyPoint`: key_points 항목
  - `Disagreement`: 이견 구조
  - `OpsGuidance`: OK/CAUTION/AVOID 가이드
  - `CommitteeResult`: 최종 합의 구조

### `committee/agents/base.py`
- **역할**: Pre-Analysis 에이전트 공통 인터페이스
- **개념 (Java/C)**: 추상 클래스/순수 가상 함수
- **메서드**
  - `run(snapshot) -> Stance`

### `committee/agents/macro_stub.py`
- **역할**: 거시(Macro) Stub 에이전트
- **입력**: `Snapshot.market_summary`
- **출력**: `Stance`
- **특징**: 데이터 실패 시 `confidence=LOW` + “data unavailable”

### `committee/agents/flow_stub.py`
- **역할**: 수급(Flow) Stub 에이전트
- **입력**: `Snapshot.flow_summary`
- **출력**: `Stance`
- **특징**: 수급 데이터 실패 시 neutral + low confidence

### `committee/agents/sector_stub.py`
- **역할**: 섹터 이동 Stub 에이전트
- **입력**: `Snapshot.sector_moves`
- **출력**: `Stance`

### `committee/agents/risk_stub.py`
- **역할**: 리스크 Stub 에이전트
- **입력**: `Snapshot.news_headlines`
- **출력**: `Stance`

### `committee/agents/chair_stub.py`
- **역할**: Chair (합의 도출)
- **입력**: 여러 `Stance`
- **출력**: `CommitteeResult`
- **규칙**
  - majority/minority tag 집계
  - minority 존재 시 disagreements 기록

### `committee/core/snapshot_builder.py`
- **역할**: Snapshot 생성 엔진
- **핵심 함수**
  - `build_snapshot_real()`: 실데이터 시도
  - `build_dummy_snapshot()`: 완전 더미
  - `get_last_snapshot_status()`: 소스 상태 로그
- **특징**: 실패 시 note에 reason 기록, 값은 0.0/빈 리스트

### `committee/core/pipeline.py`
- **역할**: 파이프라인 오케스트레이션
- **흐름**
  - Snapshot → Stances → CommitteeResult → Report
- **클래스**
  - `DailyPipeline`: 하루 1회 실행 단위

### `committee/core/validators.py`
- **역할**: 스키마 + 안전장치 검증
- **검증 항목**
  - stances 최소 1개
  - core_claims 최대 3
  - ops_guidance 레벨 제한
  - 금지 문구/알 수 없는 티커 차단

### `committee/core/report_renderer.py`
- **역할**: Report 생성/렌더링
- **출력**
  - JSON report
  - Markdown report (`report.md`)

### `committee/core/storage.py`
- **역할**: 아카이브 저장 유틸
- **출력**
  - `runs/YYYY-MM-DD/` 폴더에 snapshot/stances/committee_result/report 저장

### `committee/tools/providers.py`
- **역할**: 데이터 수집 인터페이스
- **개념 (Java/C)**: 인터페이스/추상 클래스 역할

### `committee/tools/http_provider.py`
- **역할**: 공개 API 기반 실데이터 시도
- **특징**
  - 실패해도 예외 밖으로 던지지 않음
  - `(value, reason)` 형태로 반환

### `committee/tools/fallback_provider.py`
- **역할**: 항상 안전한 기본값 반환
- **용도**: 실데이터 실패 시 fallback

### `committee/adapters/telegram_sender.py`
- **역할**: 텔레그램 전송 어댑터
- **특징**
  - 토큰 없으면 콘솔 출력
  - 3500자 초과 시 분할 전송

### `scripts/run_local.py`
- **역할**: 로컬 테스트용 실행
- **출력**: 콘솔 + JSON report

### `scripts/run_nightly.py`
- **역할**: 야간 배치 실행
- **출력**: `runs/YYYY-MM-DD/` 저장

### `scripts/send_morning.py`
- **역할**: 최신 report.md를 텔레그램 발송
- **실패 처리**: 토큰 없으면 콘솔 출력

---

## 호출 흐름 (더 상세)

```
run_local.py / run_nightly.py
  -> build_snapshot_real()
     -> HttpProvider (실패 시 FallbackProvider)
  -> agents/*.run(snapshot) -> Stance
  -> ChairStub.run(stances) -> CommitteeResult
  -> build_report() -> Report
  -> render_report() / storage.save_run()
```

---

## 입력/출력 예시 (구조 이해용)

### Snapshot (요약)
```
snapshot.market_summary.note: "KOSPI -1.44%, USD/KRW 1465.09. Headlines loaded. Flows unavailable."
snapshot.market_summary.kospi_change_pct: -1.44
snapshot.market_summary.usdkrw: 1465.09
snapshot.flow_summary.note: "flows_fetch_failed: unavailable"
snapshot.flow_summary.foreign_net: 0.0
snapshot.news_headlines: ["..."]
```

### Stance (요약)
```
agent_name: "macro"
core_claims: ["..."]
regime_tag: "NEUTRAL"
evidence_ids: ["snapshot.market_summary.usdkrw", "snapshot.market_summary.kospi_change_pct", "snapshot.news_headlines"]
confidence: "MED"
```

### CommitteeResult (요약)
```
consensus: "Committee maintains a neutral posture with selective positioning."
key_points: [{ point: "...", sources: ["macro","risk"] }]
disagreements: [{ topic: "Regime tags", majority: "NEUTRAL", minority: "None", ... }]
ops_guidance: [{ level: "OK", text: "..." }, { level: "CAUTION", ... }, { level: "AVOID", ... }]
```
