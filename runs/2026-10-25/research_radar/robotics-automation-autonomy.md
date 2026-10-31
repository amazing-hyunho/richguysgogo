# Research-to-Market Radar — 로봇·자동화·자율주행

- 기준일: `2026-10-25`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **10.23/100**
- 근거 확신도: **14.50/100**
- 핵심 가설: 월드모델·VLA·범용 로봇 학습의 반복 가능한 성능 개선이 센서·액추에이터·제조 자동화 수요로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 40.94 | 58.01 | 12 | 1 | 미통과 |
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
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **SmolVLA-MoE: Sparse Mixture-of-Experts for Efficient Multi-Task Robotic Manipulation** — SmolVLA-MoE는 VLA의 FFN 레이어에 희소 MoE 구조를 도입해 멀티태스크 조작 벤치마크에서 기존 경량 VLA 대비 성공률과 효율성을 모두 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.30732v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **When One Step Is Enough: An Empirical Study of Euler Integration in Flow-Matching Policies** — 충분히 학습된 대형 VLA에서는 단일 스텝 오일러 적분만으로도 다단계 샘플링과 유사한 성능을 보이며, 저지연 배치가 가능함을 실증했다. | [arXiv](https://arxiv.org/abs/2610.30735v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **DRILL: Training World Models to Improve Policies, Not Predict Pixels** — DRILL 프레임워크는 월드모델을 픽셀 예측이 아닌 정책 성능 향상에 맞춰 학습할 때 실제 조작 시뮬레이터에서 정책 성공률이 유의하게 높아짐을 보였다. | [arXiv](https://arxiv.org/abs/2610.30814v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 부정 | **Measuring the Reasoning-Action Coupling in Driving Vision-Language-Action Models through Counterfactuals** — 운전용 VLA 모델의 언어 기반 추론과 실제 행동 간 결합이 약함을 반사실적 개입 실험으로 밝혀, 설명가능성의 한계를 지적했다. | [arXiv](https://arxiv.org/abs/2610.30953v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **Memory before Goal: Role of Pre-History Memory for Humanoid Loco-Manipulation** — WholeBodyMem은 과거 객체 이벤트 기반 메모리를 도입해 휴머노이드 로코-매니퓰레이션 과제에서 정책 성공률을 크게 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.31166v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **Learning Robot Behavior Priors from Non-Robotic Synthetic Data** — 비로봇 합성 데이터로 사전학습한 모델이 실제 로봇 행동 예측에서 비트리비얼한 제로샷 성능을 보이며, 수학적 추상화 기반 데이터가 로봇 행동 사전으로 유용함을 보였다. | [arXiv](https://arxiv.org/abs/2610.31275v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **FocusVLA: Future-Intent Guided Dynamic View Routing for Vision-Language-Action Models** — FocusVLA는 미래 의도 예측을 활용한 동적 뷰 라우팅으로 실제 및 시뮬레이션 조작 과제에서 기존 VLA 대비 성공률을 유의하게 높였다. | [arXiv](https://arxiv.org/abs/2610.31423v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **FastHarness: Experience-Driven Review Scheduling for Vision-Language-Action Policies** — FastHarness는 경험 기반으로 리뷰 빈도를 줄이고, 실패 시 집중 감독을 통해 VLA 정책의 효율적 실행과 성공률 향상을 시뮬레이션 과제에서 실증했다. | [arXiv](https://arxiv.org/abs/2610.31427v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **Skeleton-Grounded Latent Action Model for Robot World Models** — SkeLAM은 로봇 스켈레톤 기반의 잠재 행동 분해를 통해 로봇 제어와 시각적 변화의 분리를 달성하고, 실제 및 시뮬레이션에서 예측 정확도와 정책 일치도를 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.31474v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **Echo: Coupled Action and Task Status Signal Denoising for Vision Language Action Models** — Echo 프레임워크는 세밀한 진행 주석 없이도 VLA 정책 내에서 성공·실패 신호를 학습·예측하고, 실제 로봇 조작 실험에서 정책 성능을 일관되게 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.31569v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **Progress Probes $P^2$: Lightweight Runtime Monitoring for Vision-Language-Action Models** — VLA 모델의 내부 활성값에 선형 프로브를 적용해 정책 실행의 진행 상황을 추정하고, 실패 탐지에서 기존 VLM 기반 모니터보다 경쟁력 있거나 더 우수한 성능을 보였다. | [arXiv](https://arxiv.org/abs/2610.31613v1) |
| 2026-10-22 | 2026-10-22 | 연구 검증 | 긍정 | **Sensorimotor Alignment: A Platonic Proxy for Embodied Policy Success** — Sensorimotor Alignment($S^2$)라는 오프라인 지표가 다양한 임베디드 로봇 모델에서 실제 로봇 과제 성공률과 양의 상관관계를 보여, 비싼 폐루프 평가 없이도 모델 우선순위 선정에 활용될 수 있음을 실험적으로 보였다. | [arXiv](https://arxiv.org/abs/2610.31670v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 40.94점으로 단계 통과 기준에 미달합니다.
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
