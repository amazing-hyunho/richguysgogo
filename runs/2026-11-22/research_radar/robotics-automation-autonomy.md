# Research-to-Market Radar — 로봇·자동화·자율주행

- 기준일: `2026-11-22`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **7.26/100**
- 근거 확신도: **13.40/100**
- 핵심 가설: 월드모델·VLA·범용 로봇 학습의 반복 가능한 성능 개선이 센서·액추에이터·제조 자동화 수요로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 29.06 | 53.62 | 12 | 1 | 미통과 |
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
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **CauSyncVLA: Causal Latent World Modeling for Asynchronous Robot Control** — CauSyncVLA는 비동기 인지-제어 정렬을 통해, LIBERO-10에서 93.8% 성공률과 5배 이상의 추론 처리량을 달성하며, 폐루프 강인성과 로봇 동작 부드러움을 개선했다. | [arXiv](https://arxiv.org/abs/2611.25667v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 부정 | **DMT-Attack: Diffusion-Prior Texture Search for Closed-Loop Vision-Language-Action Policies** — DMT-Attack은 자연스러운 텍스처를 생성해 VLA 정책의 시각 피드백을 교란하며, 4개 벤치마크에서 공격 성공률과 탐지 회피율이 기존 대비 크게 높음을 보였다. | [arXiv](https://arxiv.org/abs/2611.25695v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **Point Dynamics as Proxy for Robotic World Models** — 3D 포인트 기반 동역학 예측을 영상 렌더링과 분리함으로써, 로봇 월드모델의 객체 운동 정확도를 시뮬레이션과 실제 양쪽에서 6~8% 개선하였다. | [arXiv](https://arxiv.org/abs/2611.25946v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **One View, One Action: Spatially Generalizable VLAs through Observation-Aligned Experts and Cross Graph Consistency** — OVOA-VLA는 관찰 정렬 전문가와 그래프 일관성 학습을 통해, 다양한 시점 변화와 초기 상태 변화에도 조작 성공률을 시뮬레이션(88.1%)과 실제(58.3%)에서 크게 향상시켰다. | [arXiv](https://arxiv.org/abs/2611.26161v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **Teaching Vision-Language-Action Models to Stop Safely** — SAFI 기법은 VLA 기반 로봇이 실행 중 금지된 작업을 안전하게 중단하고, 물리적 사고 없이 대체 행동을 수행하도록 하여, takeover 후 성공률을 1.3%로 낮추고 안전성을 높였다. | [arXiv](https://arxiv.org/abs/2611.26239v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **FastRoverVLA: Fast Vision-Language-Action Execution for Off-Road Autonomous Driving** — FastRoverVLA는 오프로드 자율주행에서 시각-언어-행동 계획과 실제 차량 운동을 분리해, 실제 데이터셋에서 경로 오차를 18~36.7% 감소시키고 처리 비용을 16~20배 절감했다. | [arXiv](https://arxiv.org/abs/2611.26242v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **TacInno: Teaching Vision-Language-Action Models the Contact Dynamics Beyond Vision and Action** — TacInno는 시각과 행동으로 설명되지 않는 촉각 변화를 감독 신호로 활용해, 접촉이 풍부한 조작에서 기존 대비 실제 및 시뮬레이션 모두에서 성공률을 9~10.7%p 향상시켰다. | [arXiv](https://arxiv.org/abs/2611.26405v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **Awaken-HI: Scaling Humanoid Intelligence with Whole-Body Human Experience** — Awaken-HI 모델은 대규모 인간 동작 데이터로 사전학습하여 휴머노이드 로봇의 로코-매니퓰레이션 기술 전이와 실제 작업 성공률(평균 93.75%)을 크게 향상시켰다. | [arXiv](https://arxiv.org/abs/2611.26420v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **Risk-Controlled Test-Time Adaptation for Vision-Language-Action Models** — R2-VLA 프레임워크는 VLA 모델의 테스트 시점 적응에서 위험 제어와 전문가 개입 최소화를 결합해, 4개 벤치마크에서 평균 작업 성공률을 9.2~11.2%p 향상시켰다. | [arXiv](https://arxiv.org/abs/2611.26438v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 부정 | **Mind2Act World: A Diagnostic Benchmark for Embodied Mind, Physical Action, and Mind-Action Composition in Robotic Manipulation** — Mind2Act World 벤치마크를 통해 VLA 및 WAM 등 최신 에이전트가 인지적 추론과 물리적 실행의 조합(피드백 기반)에서 현저히 낮은 성공률(12%)을 보이며, 이 조합이 주요 병목임을 진단했다. | [arXiv](https://arxiv.org/abs/2611.26444v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 부정 | **PhyDEX: A Benchmark for Physical Reasoning in Vision-Language-Action Models via Dynamic Extrinsic Dexterity** — PhyDEX 벤치마크를 통해 기존 VLA 모델들이 실제 물리적 속성(질량, 마찰 등)을 제대로 이해하지 못하며, 실제 및 시뮬레이션 모두에서 성공률이 3% 미만임을 보였다. | [arXiv](https://arxiv.org/abs/2611.26565v1) |
| 2026-11-19 | 2026-11-19 | 연구 검증 | 긍정 | **PGX: Physically Grounded Execution for Long-Horizon Humanoid Loco-Manipulation** — PGX 프레임워크는 VLA 모델의 장기 휴머노이드 로코-매니퓰레이션 과제에서 단계 진행과 작업 성공률을 개선함을 시뮬레이션 3개 및 실제 로봇 1개 실험으로 입증하였다. | [arXiv](https://arxiv.org/abs/2611.26596v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 29.06점으로 단계 통과 기준에 미달합니다.
- 인재 이동·창업: 기준일 현재 사용 가능한 근거가 없습니다.
- 자본 형성: 기준일 현재 사용 가능한 근거가 없습니다.
- 인프라 병목: 기준일 현재 사용 가능한 근거가 없습니다.
- 상장사 실적 확인: 기준일 현재 사용 가능한 근거가 없습니다.
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
