# Pipeline Backfill Guide

`scripts/backfill_pipeline_range.py` 사용법 정리 문서입니다.

이 스크립트는 날짜 범위를 돌면서 `DailyPipeline`를 재실행하고, 아래를 함께 채웁니다.

- `runs/YYYY-MM-DD/` 산출물
- `runs/YYYY-MM-DD.json` 통합 파일
- `data/investment.db` 핵심 테이블 데이터
- (기본값) `docs/dashboard.html` 재생성

---

## 1) 기본 개념

### `--mode missing` (기본 추천)
- 누락 날짜만 골라서 실행합니다.
- 판단 기준:
  - runs 산출물 누락 (`snapshot.json`, `stances.json`, `committee_result.json`, `report.md`, `runs/YYYY-MM-DD.json`)
  - 또는 DB 핵심 행 누락 (`market_daily`, `market_flow_daily`, `daily_macro`)

### `--mode all`
- 지정한 범위의 날짜를 전부 재실행합니다.
- “최근 1년 전체 재백필” 같은 작업에 사용합니다.

---

## 2) 가장 자주 쓰는 명령

### A. 누락 날짜만 백필 (1년 범위)
```bash
python scripts/backfill_pipeline_range.py --mode missing
```

### B. 1년치 전체 재백필
```bash
python scripts/backfill_pipeline_range.py --mode all --lookback-days 365
```

### C. 실제 실행 없이 대상 날짜만 확인 (권장 선점검)
```bash
python scripts/backfill_pipeline_range.py --mode missing --dry-run
```

### D. AI 판단 제외(스냅샷+DB만 백필)
```bash
python scripts/backfill_pipeline_range.py --mode missing --exclude-ai
```

### E. (신규) 수급/매크로 날짜별 백필
```bash
# 1) 시장/환율 히스토리
python scripts/backfill_market_daily_history.py --start-date 2025-05-01 --end-date 2026-04-30

# 2) 일간 매크로 기본 컬럼 (불가한 날짜는 NULL)
python scripts/backfill_daily_macro_history.py --start-date 2025-05-01 --end-date 2026-04-30

# 3) 수급 히스토리 (정확한 날짜만 채우고, 불일치/실패는 NULL)
python scripts/backfill_market_flow_history.py --start-date 2025-05-01 --end-date 2026-04-30 --source AUTO

# 4) 일간 매크로 보강 컬럼 (vix3m/credit/fed_bs)
python scripts/backfill_macro_indicators.py

# 5) runs 재구성 + 대시보드
python scripts/rebuild_runs_from_db.py --start-date 2025-05-01 --end-date 2026-04-30
python scripts/build_dashboard.py
```

### F. (신규) 원클릭 백필 + 검증
```bash
python scripts/backfill_all_history.py --start-date 2025-05-01 --end-date 2026-04-30 --flow-source AUTO
```

- 내부적으로 시장/매크로/수급 백필 + runs 재구성 + 검증을 순서대로 실행합니다.
- 검증 실패 시 non-zero exit로 종료합니다.

---

## 3) 기간 지정 예시

### 특정 기간 전체 재실행
```bash
python scripts/backfill_pipeline_range.py --mode all --start-date 2025-05-01 --end-date 2026-04-30
```

### 특정 기간에서 누락분만 채우기
```bash
python scripts/backfill_pipeline_range.py --mode missing --start-date 2026-04-01 --end-date 2026-04-30
```

---

## 4) 운영 옵션

- `--skip-weekends`  
  토/일은 건너뜁니다.

- `--no-rebuild-dashboard`  
  실행 후 대시보드 재생성을 생략합니다.

- `--no-continue-on-error`  
  날짜 하나라도 실패하면 즉시 중단합니다.

- `--agent-ids`  
  실행 에이전트 목록을 직접 지정합니다.  
  예:
  ```bash
  python scripts/backfill_pipeline_range.py --mode all --lookback-days 30 --agent-ids macro,flow,risk
  ```

- `--exclude-ai`  
  `stance/committee/report` 생성을 건너뛰고, 스냅샷 수집 + DB 적재만 수행합니다.  
  이 모드에서는 날짜별로 `runs/YYYY-MM-DD/snapshot.json`과 `runs/YYYY-MM-DD.json`(snapshot only)을 기록합니다.  
  또한 과거 날짜는 가능한 경우 `investment.db` 히스토리로 재구성합니다.

- `--allow-unsafe-live-data`  
  **주의:** `--exclude-ai` + 과거 날짜 실행을 강제로 허용합니다.  
  기본값은 `false`이며, 기본 동작에서는 과거 날짜 실행을 차단합니다(라이브값 혼입 방지).

---

## 5) 추천 실행 순서

1. `--dry-run`으로 대상 날짜 확인  
2. `--mode missing` 먼저 실행해 누락분 복구  
3. 필요 시 `--mode all --lookback-days 365`로 전체 재백필  
4. 완료 후 `docs/dashboard.html`과 최신 `runs`/DB 업데이트 확인

---

## 6) 참고 사항

- 환경 변수(`.env`)는 스크립트에서 자동 로드합니다.
- 장시간 실행될 수 있으니, 먼저 짧은 범위로 테스트 후 1년치를 돌리는 것을 권장합니다.
- 기존 날짜를 `all` 모드로 다시 돌리면 해당 날짜 산출물은 최신 기준으로 재생성됩니다.
- 안전장치: `--exclude-ai`로 과거 날짜를 돌리면 기본적으로 실패합니다.  
  (과거일에 최신 라이브 데이터가 들어가는 문제를 막기 위한 보호 로직)
