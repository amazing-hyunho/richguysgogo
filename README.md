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

---

## 환경 변수 (Telegram)

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

없으면 콘솔 출력으로 대체합니다.

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
