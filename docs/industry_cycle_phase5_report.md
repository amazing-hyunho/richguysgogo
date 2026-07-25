# Phase 5 리포트 — 가격전용 워크포워드 백테스트 + 임계값 민감도 + 무료데이터 병목

**범위 (사용자 승인)**: "지금 가능한 범위만 진행: 가격전용(Phase 1-B) 신호로 워크포워드
백테스트 + 임계값 민감도 분석 + 무료데이터 병목 리포트 작성. 전체 모델 검증은 데이터가
쌓인 뒤로 보류."

전체 `industry_cycle_signal` (펀더멘털+실적+수급+매크로 결합) 모델은 실제 주간 관측치가
1주뿐이라 워크포워드 검증이 통계적으로 의미가 없다. 반면 Phase 1-B 가격전용 신호는
2023-01 ~ 2026-07-24까지 약 3.5년의 실제 일별 가격 데이터가 이미 백필되어 있어, 실제
데이터만으로 검증 가능하다. 이 문서는 그 결과만 다룬다.

---

## 1. 워크포워드 백테스트 결과 (실행 완료, 실데이터)

- 실행 명령: `python scripts/run_industry_price_walkforward.py --start 2023-01-06 --end 2026-07-24 --execute`
- 대상: `config/industry_price_universe.json`의 17개 자산 (반도체/소프트웨어·클라우드/자동차·부품/철강·비철금속/하드웨어·전자부품/은행, KR+US), 186주(금요일 기준, 매주)
- 방식: 매 과거 주 `as_of`마다 실제 운영 코드(`price_factor_runner.run_factor_batch`)를 그대로 재실행 → `industry_factor_weekly`/`industry_price_state_weekly`에 실제 이력 저장 → 각 액션 신호 시점부터 `price_backtest.compute_forward_returns`로 실제 이후 가격을 이용해 1/3/6/12개월 수익률 계산 → `industry_price_signal_performance`에 저장
- 결과: 186주 × 17개 자산 = 3,162건의 주간 계산 성공(실패 0), 액션 신호(RECOVERY_CONFIRMED / OVERHEAT_WARNING / DETERIORATION_CONFIRMED) 총 2,564건 평가

| 신호 상태 | 기간 | n | 적중률(초과수익>0) | 평균 초과수익 | 중간값 초과수익 |
|---|---|---|---|---|---|
| overheat_warning | 1m | 486 | 51.9% | +1.19% | +0.33% |
| overheat_warning | 3m | 427 | 59.5% | +6.27% | +3.70% |
| overheat_warning | 6m | 346 | 62.7% | +16.24% | +7.67% |
| overheat_warning | 12m | 229 | 56.8% | +16.92% | +6.38% |
| recovery_confirmed | 1m | 108 | 64.8% | +2.61% | +2.71% |
| recovery_confirmed | 3m | 104 | 57.7% | +4.10% | +2.70% |
| recovery_confirmed | 6m | 104 | 53.8% | +5.54% | +1.75% |
| recovery_confirmed | 12m | 83 | 49.4% | +20.98% | -0.40% |
| deterioration_confirmed | 1m | 24 | 8.3% | -7.11% | -7.36% |
| deterioration_confirmed | 3m | 24 | 29.2% | -12.60% | -21.75% |
| deterioration_confirmed | 6m | 24 | 25.0% | -17.01% | -23.23% |
| deterioration_confirmed | 12m | 24 | 37.5% | -10.73% | -40.71% |

### 해석 (주의: "적중률" 정의에 관한 주의사항 포함)

- `price_backtest.summarize_performance`의 "적중률(win_rate)"은 언제나 "초과수익 > 0"의
  비율로 정의된다. `recovery_confirmed`/`overheat_warning`처럼 "매수/보유 유지" 신호에서는
  높은 적중률이 좋은 결과지만, `deterioration_confirmed`(하락 확정 → 청산 신호)에서는
  **낮은 적중률(8~38%)이 오히려 신호가 잘 작동했다는 뜻**이다: 하락 확정 신호가 뜬 이후
  대부분(62~92%) 실제로 벤치마크 대비 underperform했다는 것이므로, 이 신호대로 청산했다면
  손실을 피했을 것이라는 의미다. 평균/중간값 초과수익이 전부 음수(-7%~-41%)인 것도 같은
  결론을 뒷받침한다. 이 표를 그대로 대시보드나 리포트에 노출할 경우, `deterioration_confirmed`
  행에는 "낮을수록 신호가 유효함"이라는 주석을 반드시 병기해야 한다 (다음 단계 권고사항 3번).
- `recovery_confirmed`의 12개월 지표는 평균(+20.98%)과 중간값(-0.40%)이 크게 갈린다 — 표본
  83건 중 일부 극단치(2023년 AI/반도체 급등 구간에 진입한 신호)가 평균을 강하게 끌어올린
  것으로 보인다. 평균만 보고 "12개월 보유 시 +21% 기대"라고 결론 내리면 과대해석이며,
  중간값이 더 대표적인 전형적 결과에 가깝다.
- `overheat_warning`은 특이하게도 6/12개월 후 초과수익이 양수(+16%대)로, "과열 경고" 신호
  발생 후에도 계속 올랐다. 이는 표본 기간(2023~2026)이 반도체/AI 랠리가 여러 차례 재차
  과열을 뚫고 상승한 특수한 구간이었음을 반영할 가능성이 높다 — "과열 = 매도"로 단순
  해석하면 이 표본 기간 동안은 손실이었을 것이다. 표본이 특정 강세장에 편중되어 있다는
  점은 2번 섹션(병목)에서도 다룬다.
- 표본이 17개 자산·6개 산업(전체 22개 산업 중)에 한정되어 있어, 결과를 산업 전반에
  일반화하기는 어렵다.

---

## 2. 임계값 민감도 분석 (실행 완료, 실데이터)

- 실행 명령: `python scripts/run_industry_price_threshold_sensitivity.py --start 2023-01-06 --end 2026-07-24 --execute`
- 방식: 동일한 186주 윈도우에 대해 기준(`price_only_v1`) 외 3개 변형(`price_only_v1__sensitivity_<name>`)을
  독립된 `model_version`으로 실행 (기준 실행 결과를 절대 덮어쓰지 않음)

| 변형 | 오버라이드 | recovery_confirmed n (1m) | 1m 적중률 | 1m 평균초과수익 |
|---|---|---|---|---|
| 기준값 (price_only_v1) | `recovery_relative_strength_min=35` | 108 | 64.8% | +2.61% |
| tighter_recovery_rs | `recovery_relative_strength_min=55` | 33 | **72.7%** | +3.32% |
| looser_recovery_rs | `recovery_relative_strength_min=35` | 108 | 64.8% (동일) | +2.61% (동일) |
| tighter_overheat | `overheat_score_min=75` | 118 | 63.6% | +2.39% |

| 변형 | overheat_warning n (6m) | 6m 적중률 | 6m 평균초과수익 |
|---|---|---|---|
| 기준값 | 346 | 62.7% | +16.24% |
| tighter_overheat (min=75) | 260 | 63.5% | +17.49% |

### 해석

- **`recovery_relative_strength_min`을 35→55로 높이면(더 엄격한 회복 조건)**: 신호 개수가
  108→33건으로 3분의 1로 줄지만, 1개월/3개월 적중률이 64.8%→72.7%, 57.7%→62.5%로
  개선된다. 다만 6/12개월 적중률은 오히려 소폭 하락(53.8%→50.0%, 49.4%→48.0%)한다.
  → **단기 정밀도와 장기 성과 사이에 트레이드오프**가 있으며, "더 엄격 = 항상 더 좋음"은
  아니다.
- **`looser_recovery_rs`(35로 설정) 결과가 기준값과 완전히 동일**하다 — 이는 의도한
  "완화" 실험이 아니라, 기준 설정값(35)과 우연히 같은 값을 넣은 스크립트 기본 예시의
  실수였음이 실행 후 확인됐다. 코드는 이미 수정했으나(`_BUILTIN_VARIANTS`를
  `recovery_relative_strength_min=15`로 교체), 재실행에는 변형당 약 7~8분 × 4개 =
  30분 이상이 소요되어 이번 라운드에는 재실행하지 않았다. **다음 라운드에서 재실행
  권장** (아래 "다음 단계" 4번).
- **`overheat_score_min`을 70→75로 높이면(더 엄격한 과열 판정)**: `overheat_warning` 신호가
  486→383건(1개월 기준)으로 줄고 적중률/평균초과수익이 소폭 개선(51.9%→53.5%,
  +1.19%→+1.38%)된다. 부수 효과로 `recovery_confirmed` 신호가 108→118건으로 오히려
  늘었는데(과열로 분류되던 일부 주가 과열 기준 상향으로 재분류되어 회복 후보 쪽으로
  넘어간 것으로 추정), 상태 분류가 상호배타적이라는 점에서 한 임계값 변경이 다른
  상태의 신호 빈도에도 연쇄적으로 영향을 준다는 것을 확인했다 — 임계값 튜닝 시 개별
  상태만 보지 말고 전체 상태 분포를 함께 봐야 한다.
- 결론: 현재 기본값(`config/industry_cycle_price_model.json`)이 명백히 최적이라거나
  명백히 부적합하다는 증거는 없다. `recovery_relative_strength_min`을 소폭 올리는 쪽
  (신호 빈도를 줄이고 단기 정밀도를 높이는 방향)이 이번 표본에서는 근소하게 유리해
  보이나, 표본이 특정 강세장 구간에 편중되어 있어 (섹션 3 참고) 이 결론을 기본값
  변경의 근거로 쓰기엔 이르다.

전체 JSON 결과(기준값 + 3개 변형 × 4개 기간)는 `python scripts/run_industry_price_threshold_sensitivity.py --execute`의
표준출력에 출력되며, DB의 `industry_price_signal_performance` 테이블에
`model_version IN ('price_only_v1', 'price_only_v1__sensitivity_tighter_recovery_rs', 'price_only_v1__sensitivity_looser_recovery_rs', 'price_only_v1__sensitivity_tighter_overheat')`로
조회하면 재현 가능하다.

---

## 3. 무료 데이터 병목 리포트

Phase 0~4 진행 중 실제로 부딛힌 데이터 병목을 원인별로 분류했다. "완전히 막힘"과
"연결만 안 되어 있음(구현하면 바로 풀림)"을 구분하는 것이 핵심이다.

### 3.1 완전히 막힘 (무료 소스 자체가 없음 / 구조적 한계)

| 항목 | 상태 | 상세 |
|---|---|---|
| `flow_score` (수급) | 미구현 스텁 (`cycle_scoring._flow_score_stub` → 항상 `None`) | 설계상 "산업별 거래대금/기관·외국인 누적 수급/ETF 자금 흐름"이 필요하지만, 현재 DB에 있는 유일한 수급 시계열(`market_flow_daily`)은 시장 전체(코스피) 단위라 산업별 구분이 불가능. 이 시계열을 쓰면 모든 KR 산업에 동일한 값을 부여하게 되어 "데이터 없음"보다 더 나쁜 결과(허위 차별화)를 만든다. |
| `macro_fit_score` (매크로 민감도) | 미구현 스텁 (`_macro_fit_score_stub` → 항상 `None`) | "금리/달러/유가/신용스프레드 등에 대한 산업별 과거 민감도"를 계산하려면 산업 ETF 수익률 vs 매크로 시계열의 롤링 회귀 모델이 필요한데 아직 구축되지 않음. 무료 매크로 시계열(FRED) 자체는 구할 수 있으나, "회귀 기반 산업별 민감도 스코어"라는 모델 자체가 없는 것이 병목. |
| US ISM 제조업 PMI (`us_ism_manufacturing_pmi`, FRED series `NAPM`) | 소스 자체가 무료로 없음 | 2026-07-25 기준 실측 확인: ISM PMI는 FRED/ALFRED에 vintage 추적 시계열로 존재하지 않음(ISM 자체 라이선스 데이터, FRED는 과거 한때만 게재). `committee/tools/fred_monthly_provider.py`에 스크레이프 폴백이 있지만 프로덕션에서 확인된 성공 사례 없음. `semiconductors`/`machinery_industrials` 펀더멘털 매핑의 34~40% 비중이 이 지표에 걸려 있어, 이 지표가 비면 나머지 지표로 가중치가 재정규화된다(0으로 조작하지 않음). |
| KOSIS 반도체 생산지수 series_id | `TBD` (미확정) | `config/industry_indicators.json`의 `kr_semiconductor_production_index`는 series_id가 `orgId:tblId:itmId` 형식으로 KOSIS 통계표 카탈로그에서 직접 확인해야 하는데, `KOSIS_API_KEY`가 없어 카탈로그 조회 자체가 불가능 (`committee/tools/kosis_industry_provider.py` 참고). |

### 3.2 연결만 안 되어 있음 (실행하면 바로 풀리는 것) — 가장 큰 기회

| 항목 | 실제 상태 | 조치 |
|---|---|---|
| **펀더멘털 지표 원자료 미적재** | `FRED_API_KEY`는 **설정되어 있음**(환경변수 확인됨). `indicator_catalog`(5건)/`industry_indicator_map`(6건) 등 카탈로그·매핑 테이블은 이미 동기화되어 있으나, `indicator_observation` 테이블은 **0행**. `scripts/run_industry_fundamentals_factors.py`는 카탈로그/매핑만 동기화하고 실제 FRED 값을 가져오는 `committee.industry_cycle.fundamentals_ingest.ingest_catalog(...)` 호출은 아직 CLI에 연결되어 있지 않다. 이것이 "펀더멘털 스코어가 22개 산업 전부 `None`, `data_completeness=0.00`"인 실제 원인이다 — 무료 소스가 없는 게 아니라, 있는 것을 아직 안 당겨온 것. | Phase 2 후속 작업으로 `ingest_catalog`를 실제로 실행(또는 CLI에 연결)하고 `--execute`로 한 번 적재하면, `us_industrial_production_index`/`us_manufacturers_new_orders`/`us_manufacturers_inventories` 3개 지표(전부 FRED, PMI 문제 없음)는 즉시 채워질 것으로 예상됨. |
| **가격 유니버스가 22개 산업 중 6개만 커버** | `config/industry_price_universe.json`은 반도체/소프트웨어·클라우드/자동차·부품/철강·비철금속/하드웨어·전자부품/은행 6개 산업, 17개 자산만 포함. 나머지 16개 산업(조선/기계·산업재/항공·방산/운송·물류/화학/건설·건자재/전력·유틸리티/에너지/보험/증권/부동산/헬스케어·바이오/필수소비재/경기소비재/미디어·엔터·통신서비스)은 `industry_asset_map`에 매핑이 전혀 없어 `coverage_status=INSUFFICIENT`로 남아 있음. | 소스는 무료(Yahoo Finance chart API, 이미 쓰고 있음)이고 코드도 이미 있음(`scripts/backfill_industry_prices.py`) — 남은 산업별로 대표 ETF/종목 티커를 골라 `config/industry_price_universe.json` + `config/industry_etfs.json`에 추가하고 백필만 실행하면 확장 가능. 순수히 "설정 확장" 작업. |
| **종목 레벨 재무/컨센서스 데이터는 이미 훨씬 넓게 존재** | 이번 조사에서 확인: `financial_metric` 테이블에 실제로 **2,788개** 종목, `stock_consensus` 테이블에 **3,934개** 종목이 이미 적재되어 있음 (다른 committee 모듈이 이미 채워둔 것으로 보임). 반면 industry_cycle이 실제로 쓰는 `asset_price_daily`(가격)에는 19개 자산(17개 자산+2개 벤치마크)만 있다. | 재무/컨센서스 데이터는 이미 폭넓게 존재하므로, 가격 백필 대상 티커를 이 2,788/3,934개 풀에서 골라 `industry_price_universe.json`에 추가하면 **새 API 키나 새 데이터 소스 없이** Phase 3(실적/시장폭/종목 후보)와 펀더멘털 커버리지를 크게 넓힐 수 있음 — 지금까지 조사한 병목 중 가장 저비용·고효율 확장 지점. |

### 3.3 KOSIS_API_KEY 관련

- `KOSIS_API_KEY` 환경변수 자체가 설정되어 있지 않음(확인됨). 한국 통계청 KOSIS는
  API 키 발급이 무료이므로 "무료 소스가 없다"가 아니라 "키 미발급" 상태. 발급 후에도
  위 3.1의 series_id `TBD` 확정 작업이 별도로 필요함.

### 3.4 표본 기간의 구조적 편중

- 백필된 실데이터가 2023-01~2026-07 구간에 한정되어 있고, 이 구간은 반도체/AI 관련
  자산이 여러 차례 급등한 특이 구간이다. 위 1번 섹션에서 `overheat_warning` 신호 이후에도
  6/12개월 수익률이 계속 양수였던 것은 이 편중의 직접적 결과일 가능성이 높다. 하락장이나
  횡보장을 포함한 더 긴 기간의 데이터가 쌓이기 전까지, "과열 신호 = 매도해도 됨" 같은
  결론은 이 표본만으로 내리면 안 된다.

### 3.5 요약: 다음 단계 권고 (실행하지 않음, 기록만)

1. `fundamentals_ingest.ingest_catalog(...)`를 프로덕션에 1회 실행(또는 CLI로 노출)해
   FRED 3개 지표(PMI 제외)를 실제로 채운다 — API 키 이미 있음, 코드 이미 있음.
2. `financial_metric`/`stock_consensus`에 이미 존재하는 종목 풀에서 나머지 16개 산업의
   대표 종목을 선정해 `industry_price_universe.json`/`industry_etfs.json`을 확장하고
   가격을 백필한다 — 새 데이터 소스 불필요.
3. 대시보드/월간 리포트에 `deterioration_confirmed` 관련 적중률을 노출할 때는 "낮을수록
   신호가 유효함"이라는 주석을 반드시 병기한다 (섹션 1 해석 참고).
4. `scripts/run_industry_price_threshold_sensitivity.py`의 `looser_recovery_rs`/
   `looser_overheat` 변형(코드는 이미 수정 완료, `recovery_relative_strength_min=15`,
   `overheat_score_min=60`)을 재실행해 완화 방향의 실제 결과를 얻는다.
5. `KOSIS_API_KEY` 발급 후 `kr_semiconductor_production_index`의 실제 series_id를
   KOSIS 통계표 카탈로그에서 확정한다.
6. 표본 기간이 충분히 길어지고(하락장 포함) `industry_cycle_signal`(전체 결합 모델) 관측치가
   최소 수십 주 이상 쌓이면, 그때 전체 모델에 대한 워크포워드 검증을 별도 Phase로 진행한다.

---

## 4. 변경 파일

- `committee/industry_cycle/price_walkforward.py` (신규): `generate_weekly_as_of_dates`,
  `run_walkforward`, `evaluate_signal_events`, `summarize_by_state`,
  `run_threshold_sensitivity`
- `scripts/run_industry_price_walkforward.py` (신규): 워크포워드 백테스트 CLI (dry-run 기본)
- `scripts/run_industry_price_threshold_sensitivity.py` (신규): 임계값 민감도 CLI (dry-run 기본)
- `tests/test_industry_price_walkforward.py`, `tests/test_run_industry_price_walkforward_cli.py`,
  `tests/test_run_industry_price_threshold_sensitivity_cli.py` (신규 테스트)
- `docs/industry_cycle_phase5_report.md` (본 문서)
- DB(`data/investment.db`)에 `industry_factor_weekly`/`industry_price_state_weekly`/
  `industry_price_signal_performance` 실이력 데이터 적재 (`model_version`:
  `price_only_v1` 및 3개 `__sensitivity_*` 변형) — 기존 `price_only_v1`의 2026-07-25
  단일 시점 데이터는 덮어쓰지 않고 186주 전체 이력으로 확장됨 (동일 UNIQUE 키 upsert이므로
  기존 최신 주는 그대로 유지, 과거 주만 새로 추가).

## 5. 통과한 테스트

- `tests/test_industry_price_walkforward.py` (13 테스트, 전체 통과)
- `tests/test_run_industry_price_walkforward_cli.py` (3 테스트, 전체 통과)
- `tests/test_run_industry_price_threshold_sensitivity_cli.py` (3 테스트, 전체 통과)
- (전체 스위트는 Phase 5 종료 시 1회 실행 — 섹션 6 참고)

## 6. 실데이터로 검증된 부분 / 아직 검증되지 않은 부분

**실데이터로 검증됨:**
- 186주 × 17개 자산 실가격 데이터 기반 워크포워드 백테스트 (실패 0건)
- 3개 임계값 변형에 대한 민감도 비교 (전부 실가격 데이터 기반)
- `deterioration_confirmed`의 "낮은 적중률이 정상"이라는 해석은 실제 평균/중간값
  초과수익이 전부 음수라는 사실로 뒷받침됨

**아직 검증되지 않음 (범위 밖, 다음 단계로 이연):**
- 전체 결합 모델(`industry_cycle_signal`)의 워크포워드 검증 — 실 관측치 부족으로 불가능
- 22개 산업 중 16개 산업의 가격/펀더멘털 데이터 (섹션 3.2)
- `flow_score`/`macro_fit_score` (구현 자체가 없음, 섹션 3.1)
- 하락장/횡보장을 포함한 장기 표본에서의 재검증 (섹션 3.4)
