# Research-to-Market Radar — AI·반도체·데이터센터

- 기준일: `2026-11-01`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **11.13/100**
- 근거 확신도: **15.31/100**
- 핵심 가설: AI 연산 수요의 성능 개선과 비용 하락이 메모리·패키징·전력·냉각 병목으로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 44.53 | 61.25 | 8 | 1 | 미통과 |
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
| 2026-10-20 | 2026-10-20 | 연구 검증 | 긍정 | **KPage: Cross-Block Page Compaction for Hardware-Efficient Sparse Attention** — KPage는 블록 스파스 어텐션에서 HBM에 컴팩트 텐서를 별도 저장하지 않고, 타일 단위로 직접 적재하여 최대 4.25배의 속도와 2배의 메모리 절감을 실증하였다. | [arXiv](https://arxiv.org/abs/2610.28096v1) |
| 2026-10-21 | 2026-10-21 | 연구 검증 | 긍정 | **HAWK: Heterogeneity-Aware KV Cache Transfer for Efficient GPU-NPU Phase-Disaggregated LLM Inference** — HAWK는 GPU-NPU 이기종 시스템에서 LLM 인퍼런스의 prefill-decode 분리와 KV 캐시 전송 병목을 RDMA 기반 전송 및 텐서 레이아웃 변환으로 해결하여, GPU 단독 대비 최대 1.26배 전력 효율 및 1.72배 비용 효율을 실증하였다. | [arXiv](https://arxiv.org/abs/2610.29873v2) |
| 2026-10-23 | 2026-10-23 | 연구 검증 | 긍정 | **Tile-Based Decompression in Compiled GPU Engines** — GPU 쿼리 엔진에서 타일 기반 압축 해제 연산을 커널 내에 통합하여, HBM 내 압축 해제 데이터의 중복 저장 없이 최대 4배의 메모리 절감과 6배의 대역폭 절감을 실증하였다. | [arXiv](https://arxiv.org/abs/2610.32695v1) |
| 2026-10-24 | 2026-10-24 | 연구 검증 | 긍정 | **Speeding up Log-Sum-Exp: Kernel Fusion at the Memory Wall, Integer Arithmetic at the Compute Wall** — FuseLSE와 IntLSE 커널을 통해 GPU와 CPU에서 Log-Sum-Exp 연산의 HBM 트래픽 및 실행 병목을 완화하고, PyTorch 대비 최대 11배의 속도 향상을 실측하였다. | [arXiv](https://arxiv.org/abs/2610.33647v3) |
| 2026-10-26 | 2026-10-26 | 연구 검증 | 긍정 | **FrontGI: Architecture-Aware Parallel GNN Inference on Chiplet-Based Multicore Systems** — FrontGI는 칩렛 기반 멀티코어 시스템에서 대규모 GNN 추론의 병목을 해소하며, 기존 라이브러리 대비 최대 3.35배의 속도 향상을 128코어 AMD EPYC 시스템에서 실증하였다. | [arXiv](https://arxiv.org/abs/2610.34911v1) |
| 2026-10-27 | 2026-10-27 | 연구 검증 | 긍정 | **p-DCIM: A 28nm Probabilistic SRAM DCIM based Ising Machine for Near-Memory Context Selection in LLM-RAG Pipeline** — 28nm 공정의 SRAM DCIM 기반 Ising 머신을 LLM-RAG 파이프라인의 컨텍스트 선택에 적용하여, 기존 LLM 기반 선택 대비 67% 에너지 절감과 동등한 정확도를 실측하였다. | [arXiv](https://arxiv.org/abs/2610.37033v1) |
| 2026-10-28 | 2026-10-28 | 연구 검증 | 긍정 | **A Case Study of a Multi-Agent Kernel-Optimization Loop That Learns a New AI Accelerator** — LLM 기반 멀티에이전트 커널 최적화 루프가 FuriosaAI RNGD NPU와 같은 희귀 아키텍처에서 실제 커널 성능을 9.293배까지 향상시킬 수 있음을 사례로 실증하였다. | [arXiv](https://arxiv.org/abs/2610.38329v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 중립 | **When Does Heterogeneity Pay Off? Understanding GPU-WSE System Complementarity** — GPU와 WSE(wafer-scale engine) 이기종 시스템에서의 상호보완성과 병목 조건을 계층적 벤치마킹 및 분석 모델로 규명하여, 이기종 통합이 실제 성능 이득 또는 병목으로 작용하는 조건을 제시한다. | [arXiv](https://arxiv.org/abs/2610.39222v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 44.53점으로 단계 통과 기준에 미달합니다.
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
