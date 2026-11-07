# Research-to-Market Radar — 로봇·자동화·자율주행

- 기준일: `2026-11-01`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **11.80/100**
- 근거 확신도: **15.31/100**
- 핵심 가설: 월드모델·VLA·범용 로봇 학습의 반복 가능한 성능 개선이 센서·액추에이터·제조 자동화 수요로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 47.19 | 61.25 | 12 | 1 | 미통과 |
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
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **Smooth Action Chunking Via Movement-Primitive Representations for Imitation Learning** — 모방학습 기반 로봇 정책의 액션 청킹을 움직임 프리미티브 기반 표현으로 개선하여, 실제 이족 로봇 플랫폼에서 진동 및 경계 불연속성을 크게 줄이면서도 작업 성공률을 유지함을 보였다. | [arXiv](https://arxiv.org/abs/2610.39451v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **PRIME W0: Physical Priors from World Models for Embodied Manipulation** — PRIME W0 프레임워크를 통해 VLA 모델에 계층적 world model 정보를 통합하여, LIBERO 및 실제 로봇 벤치마크에서 state-of-the-art 성능을 달성함을 보였다. | [arXiv](https://arxiv.org/abs/2610.39528v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **From Reasoning to Action: Consequence-Grounded Alignment for Vision-Language-Action Models** — CoRAct 프레임워크를 통해 VLA 모델의 reasoning과 action을 결과 기반으로 정렬하여, 다양한 시뮬레이션 및 실제 조작 작업에서 기존 ECoT 기반 VLA 대비 성공률과 일반화 성능을 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.39543v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **How Much Should a VLA Trust Its Reasoning? Step-Level Guidance as a Measured Action-Value Function** — VLA 정책의 reasoning 신뢰도를 단계별로 조정하는 Q-adaptive guidance를 제안하여, 시뮬레이션 및 실제 자율주행 벤치마크에서 기존 방법 대비 성능을 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.40002v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **LOGIV: Graph-Verified Execution with Causal Local Repair for Long-Horizon Robot Tasks** — LOGIV 프레임워크를 통해 고수준 목표를 실제 로봇 작업으로 안전하게 연결하고, 실행 중 조건 검증 및 실패 복구를 통해 실제 듀얼암 작업에서 성공률을 유의하게 향상시켰음을 보였다. | [arXiv](https://arxiv.org/abs/2610.40016v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 중립 | **RoboSeed: Multidimensional Evaluation of Vision-Language-Action and World-Action Models: Capability, Resource Affordability, and Research Evidence** — VLA 및 WAM 모델의 능력, 비용, 재현성 등 다차원 평가 프레임워크(RoboSeed)를 제안하고, 실제 모델 학습·평가·감사 데이터를 바탕으로 다양한 모델의 선택 기준과 증거 격차를 체계적으로 분석하였다. | [arXiv](https://arxiv.org/abs/2610.40026v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **Learning Safe Flow Matching Robot Policies from Binary Feasibility Oracles** — 피지컬 제약(관절 한계, 충돌 회피 등)을 만족하는 안전한 로봇 정책을 바이너리 피지빌리티 오라클만으로 학습하는 방법을 제안하고, 실제 장애물 인식 조작 작업에서 100% 제약 만족을 실험적으로 보였다. | [arXiv](https://arxiv.org/abs/2610.40075v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **TouchBridge: Tactile-Conditioned Human-to-Robot Transfer for Dexterous Manipulation** — TouchBridge 프레임워크를 통해 인간의 촉각 기반 시연을 로봇 도메인 데이터로 변환하여 VLA 모델을 미세조정하고, 실제 접촉 기반 작업에서 기존 방법 대비 높은 성공률과 데이터 수집 효율을 달성하였다. | [arXiv](https://arxiv.org/abs/2610.40349v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **HiFOR: Hierarchical Foresight with Action-Guided World Grounding for Vision-Language-Action Model** — HiFOR 프레임워크를 통해 VLA 모델이 단기 및 장기 미래 예측을 계층적으로 통합하여 실제 및 시뮬레이션 로봇 조작 작업에서 성능을 향상시킴을 보였다. | [arXiv](https://arxiv.org/abs/2610.40373v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **Improving Fine-Grained Manipulation through Demonstration Expansion and Execution Design** — DEED 프레임워크를 통해 사전학습된 VLA 정책을 다양한 시각 조건과 명령어에 맞춰 적응시키고, 실제 로봇 작업(MetaFine)에서 높은 성능(85.55%)을 달성함을 실험적으로 보였다. | [arXiv](https://arxiv.org/abs/2610.40430v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **BURGER: Benchmarking and Understanding Robotic Generalization via Embodied Drawing** — 언어 조건에 따라 다양한 드로잉 행동을 학습하는 VLA 모델의 일반화 성능을 BURGER 벤치마크(시뮬레이션 및 실제 로봇 팔 적용)에서 체계적으로 평가하고, 실제 로봇에서의 반응적 드로잉 시연을 통해 일부 모델의 일반화 가능성을 실증하였다. | [arXiv](https://arxiv.org/abs/2610.40532v1) |
| 2026-10-29 | 2026-10-29 | 연구 검증 | 긍정 | **Gym-Anything for Robotics: Scaling physical simulations with digital agents** — 코딩 에이전트를 활용해 실제 경제적 가치가 높은 물리 작업을 포괄하는 로봇 시뮬레이션 환경(RoboWorld)을 자동 생성하고, 이를 통해 VLA 모델의 반복 가능한 성능 개선 방법(예: in-context learning, privileged teacher 등)을 실험적으로 제시하였다. | [arXiv](https://arxiv.org/abs/2610.40565v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 47.19점으로 단계 통과 기준에 미달합니다.
- 인재 이동·창업: 기준일 현재 사용 가능한 근거가 없습니다.
- 자본 형성: 기준일 현재 사용 가능한 근거가 없습니다.
- 인프라 병목: 기준일 현재 사용 가능한 근거가 없습니다.
- 상장사 실적 확인: 기준일 현재 사용 가능한 근거가 없습니다.
- 반증·부정 근거가 없어 낙관 편향을 별도로 점검해야 합니다.
- 근거와 연결된 상장사가 없습니다.
- 주간 논문 레이더는 제목·초록만 해석하며 동료평가, 본문 재현성, 상용화를 자동으로 확정하지 않습니다.
- 논문 수와 기술 진전은 투자수익이나 기업 실적을 직접 의미하지 않습니다.
- 실험실 성능이 실제 공장·도로의 경제성으로 이어지는지는 별도 검증이 필요합니다.

## 판정 규칙

- 단계 순서: 연구 검증 → 인재 이동·창업 → 자본 형성 → 인프라 병목 → 상장사 실적 확인
- 단계 통과: 점수 60 이상이면서 확신도 50 이상
- 시점 계약: `known_at <= as_of`인 근거만 사용
- 체인 성숙도: 다섯 단계 점수의 고정 가중합
- 상장사 연결 강도: 근거 품질·강도와 연결 유형을 반영하며 밸류에이션은 반영하지 않음
