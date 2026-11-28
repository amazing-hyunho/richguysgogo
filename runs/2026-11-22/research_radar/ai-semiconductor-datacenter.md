# Research-to-Market Radar — AI·반도체·데이터센터

- 기준일: `2026-11-22`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **12.10/100**
- 근거 확신도: **15.31/100**
- 핵심 가설: AI 연산 수요의 성능 개선과 비용 하락이 메모리·패키징·전력·냉각 병목으로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 48.41 | 61.25 | 11 | 1 | 미통과 |
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
| 2026-11-05 | 2026-11-05 | 연구 검증 | 긍정 | **Scaling Up Analog CIM: A Simulation Framework for Topology-Aware Mapping** — Isobar 시뮬레이션 플랫폼은 칩렛 통합 아날로그 CIM 시스템의 토폴로지 인지 매핑이 성능에 미치는 영향을 정량화하고, 실제 실리콘 측정 및 사이클 정확 시뮬레이션과 일치하는 신뢰성 있는 비용 추정과 매핑 최적화 효과를 보였다. | [arXiv](https://arxiv.org/abs/2611.08399v1) |
| 2026-11-07 | 2026-11-07 | 연구 검증 | 긍정 | **PENSA: A Spatial Accelerator for BitNet b1.58 Inference on an HBM-equipped AMD Alveo FPGA** — PENSA는 HBM이 탑재된 FPGA에서 BitNet b1.58 tLLM 추론을 위한 공간 가속기로, 실제 Alveo U50에서 동작하며 동급 Xeon CPU 대비 2.14~3.14배의 처리량을 달성했다. | [arXiv](https://arxiv.org/abs/2611.10648v2) |
| 2026-11-07 | 2026-11-07 | 연구 검증 | 긍정 | **Beyond Host-Side Control: HBM Controller Partitioning Across Host and HBM Base Dies** — HBM4의 컨트롤러 기능을 호스트와 베이스 다이 간에 분할 배치할 때, 대역폭 손실 없이 호스트 면적과 에너지를 절감하고, 공유 제어 방식이 정적 분할 대비 최대 1.72배의 처리량을 제공함을 시뮬레이션 기반으로 보였다. | [arXiv](https://arxiv.org/abs/2611.10930v1) |
| 2026-11-11 | 2026-11-11 | 연구 검증 | 긍정 | **Starscream: Reimagining LLM Sharding on AMD Instinct GPUs with GPU Partitioning** — Starscream은 칩렛 기반 AMD Instinct GPU의 파티셔닝 특성을 활용해 LLM 샤딩 전략을 재설계, 실제 MI300X/MI355X에서 최대 4배의 어텐션 속도 향상 등 칩렛 인지 설계의 효과를 입증했다. | [arXiv](https://arxiv.org/abs/2611.15951v1) |
| 2026-11-13 | 2026-11-13 | 연구 검증 | 긍정 | **CHARMING: Parallel Edge AI Acceleration Across Tensor Processing and In-Memory Computation** — CHARMING은 텐서 처리와 인메모리 컴퓨팅을 병렬로 활용하는 엣지 AI 아키텍처로, 실제 하드웨어에서 LLM 및 비디오 생성 모델의 성능과 에너지 효율을 크게 개선함을 입증했다. | [arXiv](https://arxiv.org/abs/2611.17785v1) |
| 2026-11-14 | 2026-11-14 | 연구 검증 | 긍정 | **DT-MATCH: Defect- and Topology-Aware Chiplet Matching for Yield Optimization in Heterogeneous Integration** — DT-MATCH는 결함 및 토폴로지 인지 칩렛 매칭 프레임워크로, 실제 산업 설계에서 칩렛 기반 SoC 조립의 수율을 최적화할 수 있음을 보였다. | [arXiv](https://arxiv.org/abs/2611.19544v1) |
| 2026-11-16 | 2026-11-16 | 연구 검증 | 긍정 | **ThermLeT: Transformer-based Temperature Prediction for 2.5D Chiplet Architecture** — ThermLeT는 2.5D 칩렛 아키텍처의 온도 예측을 위해 트랜스포머 기반 모델을 제안, 기존 방법 대비 35~71% 정확도 향상과 6~11배 빠른 추론 속도를 달성했다. | [arXiv](https://arxiv.org/abs/2611.21954v1) |
| 2026-11-17 | 2026-11-17 | 연구 검증 | 긍정 | **Computed Permutation Trellis Coding: Near-Optimal Quantization from Two Multiplications and a 64-Byte Table** — CPTC는 1~6비트 범위에서 정보 이론적 최적에 근접하는 저비트 텐서 양자화 포맷을 제안하며, AWS Trainium 4 AI 가속기에 내장되어 FP4/FP8과 동등한 처리량을 보이고, LLM 가중치 양자화에서 기존 대비 KL divergence가 가장 낮다. | [arXiv](https://arxiv.org/abs/2611.22019v1) |
| 2026-11-17 | 2026-11-17 | 연구 검증 | 긍정 | **PAISF: A Partially Adaptive In-Order Selection Function for Routing in On-Chip, Inter-Chiplet, and Wafer-Scale Networks** — PAISF 등 새로운 선택 함수는 온칩·칩렛간·웨이퍼스케일 네트워크의 불규칙 토폴로지에서 순서 보장과 데드락 없는 라우팅을 동시에 제공하며, 기존 전략 대비 처리량 15.2% 향상, 에너지 및 지연 12.1%/11.3% 감소를 달성한다. | [arXiv](https://arxiv.org/abs/2611.22772v1) |
| 2026-11-17 | 2026-11-17 | 연구 검증 | 긍정 | **How well does graph superoptimization transfer? Adapting tensor-graph superoptimizer to a Triton-based NPU** — 그래프 수준 슈퍼옵티마이저(Mirage)를 CUDA에서 Triton 기반 NPU(Huawei Ascend 910B3)로 이식하여, 트랜스포머 관련 워크로드에서 최대 87%의 성능 향상을 달성할 수 있음을 보였다. | [arXiv](https://arxiv.org/abs/2611.22844v1) |
| 2026-11-17 | 2026-11-17 | 연구 검증 | 긍정 | **LASH-PAT: Deadlock-Free Adaptive Shortest-Path Routing for Inter-Chiplet Interconnects** — LASH-PAT은 불규칙한 인터-칩렛 네트워크에서 데드락 없는 최단경로 라우팅과 적응적 경로 다양성을 결합하여, 기존 라우팅 대비 처리량을 21.15% 향상시키고 패킷당 에너지를 12.77% 절감하며, 지연은 최저 지연 기준과 유사하게 유지한다. | [arXiv](https://arxiv.org/abs/2611.22937v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 48.41점으로 단계 통과 기준에 미달합니다.
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
