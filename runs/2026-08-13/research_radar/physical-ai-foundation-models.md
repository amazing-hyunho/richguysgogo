# Research-to-Market Radar — 피지컬 AI·로봇 파운데이션 모델

- 기준일: `2026-08-13`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **8.20/100**
- 근거 확신도: **14.39/100**
- 핵심 가설: 월드모델·VLA·범용 로봇 학습의 반복 가능한 성능 개선이 로봇 데이터와 연산·센서·액추에이터 병목으로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 32.81 | 57.56 | 20 | 1 | 미통과 |
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
| 2026-08-07 | 2026-08-07 | 연구 검증 | 중립 | **Depth-Wise Probing and Pruning of the Planning Token in a Driving Vision-Language-Action Model** — VLA 기반 자율주행 모델에서 플래닝 토큰의 계층별 분석을 통해, 초기 레이어에서 명령 해독이 가능하며 일부 레이어를 제거해도 성능 저하 없이 속도 향상이 가능함을 보였다. | [arXiv](https://arxiv.org/abs/2608.07361v1) |
| 2026-08-08 | 2026-08-08 | 연구 검증 | 긍정 | **Auditing Instruction-Trajectory Mismatches in Multimodal Robot Demonstrations** — MMPF는 멀티모달 로봇 데모에서 언어-행동 불일치(ITM)를 효과적으로 감지·교정하여, 실제 로봇 실험에서 정책 성능을 개선할 수 있음을 보였다. | [arXiv](https://arxiv.org/abs/2608.07895v1) |
| 2026-08-09 | 2026-08-09 | 연구 검증 | 긍정 | **WA-SpecDec: World-Aware Speculative Decoding for Vision-Language-Action Models** — WA-SpecDec는 월드모델 기반 장면 인식을 활용해 VLA 정책의 speculative decoding 속도와 안전성을 기존 대비 향상시킨다. | [arXiv](https://arxiv.org/abs/2608.08725v1) |
| 2026-08-09 | 2026-08-09 | 연구 검증 | 부정 | **From Recovery to Drop-off: How Action Post-training Reduces a VLM's Late-Layer Depth Decodability** — VLM을 VLA로 액션 포스트트레이닝할 때, 깊은 레이어에서의 공간적 이해(깊이 디코더빌리티)가 현저히 저하됨을 계층별 분석으로 확인했다. | [arXiv](https://arxiv.org/abs/2608.08904v1) |
| 2026-08-10 | 2026-08-10 | 연구 검증 | 긍정 | **Trajectory Divergence Horizon Decision for Reliable Dual-Arm Surgical Subtask Manipulation** — TDHD는 실제 다빈치형 이중팔 수술 로봇 벤치마크에서 VLA 정책의 실행 신뢰성과 성공률을 향상시킨다. | [arXiv](https://arxiv.org/abs/2608.09125v1) |
| 2026-08-10 | 2026-08-10 | 연구 검증 | 긍정 | **JEPA-WAM: Learning Vision-Language-Action Policies with Joint-Embedding World Modeling** — JEPA-WAM은 V-JEPA 기반 라티트 월드모델로, 예측적 전이와 행동 생성을 결합해 다양한 벤치마크와 실제 이중팔 조작에서 강한 일반화 성능을 보인다. | [arXiv](https://arxiv.org/abs/2608.09381v1) |
| 2026-08-10 | 2026-08-10 | 연구 검증 | 긍정 | **Skills in Weights, Memory in Code: Hybrid Learning for Memory-Dependent Robot Manipulation** — HyMeS는 코딩 에이전트 기반 메모리 관리와 VLA 정책을 결합해, 장기 메모리 의존 조작에서 데이터 효율적이고 강한 일반화 성능을 보인다. | [arXiv](https://arxiv.org/abs/2608.09410v1) |
| 2026-08-10 | 2026-08-10 | 연구 검증 | 긍정 | **VANE: Reliable Test-Time Training for Vision-Language-Action Models via Future Visual Representation Prediction** — VANE는 미래 시각 결과 기반의 증거 중심 테스트타임 트레이닝을 통해 VLA 정책의 상호작용 중 적응 신뢰성을 높인다. | [arXiv](https://arxiv.org/abs/2608.09448v2) |
| 2026-08-10 | 2026-08-10 | 연구 검증 | 긍정 | **RecoverFly: A Failure-Aware Reinforcement Learning Post-Training Framework for Aerial Vision-Language Navigation** — RecoverFly는 UAV-VLA 정책에 RL 기반 사후 학습을 적용해 복잡한 환경에서 성공률과 일반화 성능을 향상시킨다. | [arXiv](https://arxiv.org/abs/2608.09467v1) |
| 2026-08-10 | 2026-08-10 | 연구 검증 | 긍정 | **World Tokens: Enhancing Embodied Policies with Training-Time World Modeling** — World Tokens는 훈련 시 월드모델을 활용해 정책의 표현력을 강화하면서도, 배포 시 효율성을 유지하며 실제 로봇 및 벤치마크에서 경쟁력 있는 성능을 보인다. | [arXiv](https://arxiv.org/abs/2608.09730v1) |
| 2026-08-10 | 2026-08-10 | 연구 검증 | 긍정 | **SLIM-0.5B: Learning Action-Grounded Predictive Latents for Robot Manipulation** — SLIM은 소형 라티트 기반 정책으로, 대형 VLA 및 월드모델 기반 정책과 유사하거나 더 나은 성능을 시뮬레이션 및 실제 로봇 평가에서 달성한다. | [arXiv](https://arxiv.org/abs/2608.09771v1) |
| 2026-08-11 | 2026-08-11 | 연구 검증 | 부정 | **Hidden in Plain Sight: Diffusion-Based Unrestricted Robotic Attacks on Vision-Language-Action Models** — DURA는 VLA 모델에 대해 시각적으로 자연스러운 적대적 패치를 생성하여 실제 및 시뮬레이션 환경 모두에서 기존 공격법보다 효과적으로 물리적 오작동을 유발한다. | [arXiv](https://arxiv.org/abs/2608.10393v1) |
| 2026-08-11 | 2026-08-11 | 연구 검증 | 긍정 | **DriveVLA-M0: Failure-Aware Memory Augmentation for Autonomous Driving** — DriveVLA-M0는 실패 사례 기반의 메모리 증강과 테스트타임 트레이닝을 통해 자율주행 VLA 모델의 분포 변화 적응성과 성능을 향상시킨다. | [arXiv](https://arxiv.org/abs/2608.10413v1) |
| 2026-08-11 | 2026-08-11 | 연구 검증 | 긍정 | **Lost in Reconstruction: Aligning Action Representations with Language in Vision-Language-Action Models** — SALT 토크나이저는 행동 표현에 언어적 의미를 보존함으로써, 언어 조건 제어 성능을 기존 방식 대비 크게 향상시킨다. | [arXiv](https://arxiv.org/abs/2608.10484v1) |
| 2026-08-11 | 2026-08-11 | 연구 검증 | 긍정 | **Embodied Multimodal Grounding for Open-Vocabulary Mobile Manipulation via Semantic 3D Gaussian Splatting** — Semantic 3D Gaussian Splatting 기반의 멀티모달 그라운딩 프레임워크가 실제 모바일 매니퓰레이션에서 기존 VLA 방식 대비 장기 성공률과 견고성을 크게 향상시킨다. | [arXiv](https://arxiv.org/abs/2608.10756v1) |
| 2026-08-11 | 2026-08-11 | 연구 검증 | 긍정 | **Neural Introspection Gating for Adaptive KV-Cache Reuse in Vision-Language-Action Models** — Gated VLA-Cache는 VLA 모델의 실시간 제어에서 신경망 기반 introspection을 활용해 캐시 재사용의 신뢰성과 효율성을 개선한다. | [arXiv](https://arxiv.org/abs/2608.10824v1) |
| 2026-08-11 | 2026-08-11 | 연구 검증 | 긍정 | **XCoT-VLA: Executable Chain-of-Thought for Vision-Language-Action Driving** — XCoT-VLA는 실행 가능한 체인 오브 쏘트 토큰을 도입하여 자율주행에서 실시간 계획과 추론 오버헤드를 크게 줄이면서도 성능을 향상시킨다. | [arXiv](https://arxiv.org/abs/2608.10976v1) |
| 2026-08-12 | 2026-08-12 | 연구 검증 | 긍정 | **StellaVLA: In-Context Structured Demonstration for Generalizable Vision-Language-Action Models** — StellaVLA는 구조화된 데모를 활용한 인컨텍스트 적응을 통해 OOD 상황에서 강한 일반화 성능을 보이며, 실제 로봇 벤치마크에서 기존 모델 대비 우수한 성과를 달성했다. | [arXiv](https://arxiv.org/abs/2608.11671v1) |
| 2026-08-12 | 2026-08-12 | 연구 검증 | 긍정 | **G0.5: One Autoregressive Stream for Robot Reasoning and Action** — G0.5는 reasoning과 action을 단일 오토리그레시브 스트림으로 통합하여, 다양한 실제 로봇 및 벤치마크에서 기존 SOTA 모델을 능가하는 성능을 보인다. | [arXiv](https://arxiv.org/abs/2608.11739v1) |
| 2026-08-12 | 2026-08-12 | 연구 검증 | 중립 | **Policy-Induced Hand Priors in Humanoid Dual-Arm Manipulation: Diagnosing and Mitigating Initial-Pose Dependence** — VLA 기반 휴머노이드 이중팔 조작에서 초기 자세 의존성이 정책 유도 손 선호로 나타나며, 훈련 데이터의 초기 자세 다양성 확대와 특정 저성능 자세에 대한 증강이 초기 자세 강건성을 크게 개선한다. | [arXiv](https://arxiv.org/abs/2608.11769v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 32.81점으로 단계 통과 기준에 미달합니다.
- 인재 이동·창업: 기준일 현재 사용 가능한 근거가 없습니다.
- 자본 형성: 기준일 현재 사용 가능한 근거가 없습니다.
- 인프라 병목: 기준일 현재 사용 가능한 근거가 없습니다.
- 상장사 실적 확인: 기준일 현재 사용 가능한 근거가 없습니다.
- 근거와 연결된 상장사가 없습니다.
- 주간 논문 레이더는 제목·초록만 해석하며 동료평가, 본문 재현성, 상용화를 자동으로 확정하지 않습니다.
- 논문 수와 기술 진전은 투자수익이나 기업 실적을 직접 의미하지 않습니다.
- 첫 버전은 연구 검증 단계만 자동 추적하며 인재·투자·공급망·실적은 별도 출처 수집기가 추가될 때까지 통과시키지 않습니다.

## 판정 규칙

- 단계 순서: 연구 검증 → 인재 이동·창업 → 자본 형성 → 인프라 병목 → 상장사 실적 확인
- 단계 통과: 점수 60 이상이면서 확신도 50 이상
- 시점 계약: `known_at <= as_of`인 근거만 사용
- 체인 성숙도: 다섯 단계 점수의 고정 가중합
- 상장사 연결 강도: 근거 품질·강도와 연결 유형을 반영하며 밸류에이션은 반영하지 않음
