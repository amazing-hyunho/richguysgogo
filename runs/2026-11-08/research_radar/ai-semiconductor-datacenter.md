# Research-to-Market Radar — AI·반도체·데이터센터

- 기준일: `2026-11-08`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **10.45/100**
- 근거 확신도: **15.31/100**
- 핵심 가설: AI 연산 수요의 성능 개선과 비용 하락이 메모리·패키징·전력·냉각 병목으로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 41.79 | 61.25 | 7 | 1 | 미통과 |
| 인재 이동·창업 | 0.00 | 0.00 | 0 | 0 | 미통과 |
| 자본 형성 | 0.00 | 0.00 | 0 | 0 | 미통과 |
| 인프라 병목 | 0.00 | 0.00 | 0 | 0 | 미통과 |
| 상장사 실적 확인 | 0.00 | 0.00 | 0 | 0 | 미통과 |

## 공개시장 연결고리

| 종목 | 기업 | 역할 | 연결 유형 | 연결 강도 | 사용 근거 |
|---|---|---|---|---:|---|
| - | - | - | - | 0.00 | 연결된 상장사 없음 |

## 증거 타임라인

| 사건일 | 인지일 | 단계 | 방향 | 근거와 주장 | 출처 |
|---|---|---|---|---|---|
| 2026-10-24 | 2026-10-24 | 연구 검증 | 긍정 | **Speeding up Log-Sum-Exp: Kernel Fusion at the Memory Wall, Integer Arithmetic at the Compute Wall** — Log-Sum-Exp 연산의 메모리 및 연산 병목을 각각 GPU용 커널 퓨전(FuseLSE)과 CPU용 정수 근사(IntLSE)로 완화하여, PyTorch 대비 GPU에서 최대 10~11배, CPU에서 3~6배 속도 향상을 실험적으로 보였다. | [arXiv](https://arxiv.org/abs/2610.33647v3) |
| 2026-10-27 | 2026-10-27 | 연구 검증 | 긍정 | **p-DCIM: A 28nm Probabilistic SRAM DCIM based Ising Machine for Near-Memory Context Selection in LLM-RAG Pipeline** — 28nm 공정의 SRAM 기반 DCIM Ising 머신을 실제 제작하여 LLM-RAG 파이프라인의 컨텍스트 선택을 근거리 메모리에서 수행, LLM 기반 선택 대비 쿼리당 총 에너지를 67% 절감하면서 유사한 F1 성능을 달성했다. | [arXiv](https://arxiv.org/abs/2610.37033v1) |
| 2026-10-28 | 2026-10-28 | 연구 검증 | 긍정 | **A Case Study of a Multi-Agent Kernel-Optimization Loop That Learns a New AI Accelerator** — LLM이 잘 알려지지 않은 AI 가속기(예: FuriosaAI RNGD NPU)에서 커널 최적화를 반복적으로 수행하여, 공식 베이스라인 대비 최대 9.293배 속도 향상 및 하드웨어 한계에 근접한 성능을 달성했다. | [arXiv](https://arxiv.org/abs/2610.38329v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 중립 | **Characterizing Performance Tradeoffs in Heterogeneous GPU-Wafer-Scale Accelerator Systems** — GPU와 웨이퍼스케일 엑셀러레이터(WSE) 이기종 시스템에서 아키텍처적 상호보완성과 병목 조건을 계층적 벤치마킹 및 분석 모델로 특성화하였다. | [arXiv](https://arxiv.org/abs/2610.39222v2) |
| 2026-11-03 | 2026-11-03 | 연구 검증 | 긍정 | **Scheduling Data to Compute: Hierarchical Data Pipelining for LLM Training on AMD GPUs** — AMD GPU에서 LLM 학습 시 데이터 이동 병목을 TDM, transpose-load, SDMA, RDMA 등 하드웨어 기능을 활용한 계층적 파이프라이닝으로 완화하여, 커널 및 시스템 수준에서 최대 1.88배(커널), 1.33배(통신 중첩) 속도 향상을 실측했다. | [arXiv](https://arxiv.org/abs/2611.05751v1) |
| 2026-11-04 | 2026-11-04 | 연구 검증 | 긍정 | **Shallow Encoding Emits Deep Memories** — 하이브리드 언어모델의 메모리(키-값 캐시 및 recurrent state) 저장·로드 병목을 완화하는 SEED 기법을 제안하여, 실제 GPU(GB300)에서 프롬프트 처리시 레이어 실행 수와 상태 표현을 줄여 1.2~1.4배 처리량 향상을 달성했다. | [arXiv](https://arxiv.org/abs/2611.06084v1) |
| 2026-11-05 | 2026-11-05 | 연구 검증 | 긍정 | **TACT-KV: Tri-Axis Cosine Transform for Compressing Volumetric KV Caches in Medical VLMs** — 3D 의료 영상 VLM의 KV 캐시를 3축 DCT 기반으로 압축하여 HBM 사용량을 줄이고, 동일 HBM에서 디코딩 배치 크기를 최대 8배까지 확장할 수 있음을 여러 모델과 벤치마크에서 실험적으로 보였다. | [arXiv](https://arxiv.org/abs/2611.07593v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 41.79점으로 단계 통과 기준에 미달합니다.
- 인재 이동·창업: 기준일 현재 사용 가능한 근거가 없습니다.
- 자본 형성: 기준일 현재 사용 가능한 근거가 없습니다.
- 인프라 병목: 기준일 현재 사용 가능한 근거가 없습니다.
- 상장사 실적 확인: 기준일 현재 사용 가능한 근거가 없습니다.
- 반증·부정 근거가 없어 낙관 편향을 별도로 점검해야 합니다.
- 근거와 연결된 상장사가 없습니다.
- 주간 논문 레이더는 제목·초록만 해석하며 동료평가, 본문 재현성, 상용화를 자동으로 확정하지 않습니다.
- 논문 수와 기술 진전은 투자수익이나 기업 실적을 직접 의미하지 않습니다.
- 논문은 기술 가능성을 보여줄 뿐 설비투자·수주·실적을 직접 증명하지 않습니다.

## 판정 규칙

- 단계 순서: 연구 검증 → 인재 이동·창업 → 자본 형성 → 인프라 병목 → 상장사 실적 확인
- 단계 통과: 점수 60 이상이면서 확신도 50 이상
- 시점 계약: `known_at <= as_of`인 근거만 사용
- 체인 성숙도: 다섯 단계 점수의 고정 가중합
- 상장사 연결 강도: 근거 품질·강도와 연결 유형을 반영하며 밸류에이션은 반영하지 않음
