# Research-to-Market Radar — 로봇·자동화·자율주행

- 기준일: `2026-10-11`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **11.68/100**
- 근거 확신도: **15.31/100**
- 핵심 가설: 월드모델·VLA·범용 로봇 학습의 반복 가능한 성능 개선이 센서·액추에이터·제조 자동화 수요로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 46.70 | 61.25 | 11 | 1 | 미통과 |
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
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **Tell Robot What Not to Do: A Negation Understanding Perspective** — NegaAlign은 VLA 모델에 부정 명령 이해 능력을 추가하여, 시뮬레이션 및 실제 작업에서 부정 명령 성공률을 기존 대비 대폭 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.11952v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **CAPABLE: Capability-Aware Policy Adaptation via Behavioral Latent Encoding** — CAPABLE은 고정된 VLA 정책에 자기지도적 능력 추론과 잔차 강화학습을 결합해, 실제 및 시뮬레이션에서 미지의 액추에이터 결함에 대한 복원력을 크게 높였다. | [arXiv](https://arxiv.org/abs/2610.11971v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **REACT: Rolling Denoising and Dual Decoupling for Reactive Robot Control with VLA Models** — REACT는 VLA 기반 로봇 제어에서 rolling-denoising과 dual decoupling을 도입해, 실제 및 시뮬레이션 환경에서 반응성·성공률·궤적 부드러움을 개선하였다. | [arXiv](https://arxiv.org/abs/2610.12007v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **Humanoid World Action Model With Joint State--Action Generation** — HWAM은 휴머노이드 로봇에서 정책 참조와 실제 실행 상태를 공동 예측하여, 실제 로봇 작업에서 기존 WAM 대비 성공률을 크게 높였다. | [arXiv](https://arxiv.org/abs/2610.12026v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 중립 | **ManiUnit: A Manipulation Skill Dataset and Benchmark for Long-Horizon Tasks** — ManiUnit은 장기 모바일 조작을 위한 세분화된 스킬 데이터셋과 벤치마크를 제공하며, 실제 정책 평가에서 스킬별 진단과 상태 교란에 대한 민감도를 체계적으로 분석하였다. | [arXiv](https://arxiv.org/abs/2610.12089v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **Recompose and Refine Latent Reasoning Flows for Vision-Language-Action Models** — FLOWMEM은 성공적 잠재 추론 경로를 재사용하는 VLA 정책으로, 실제 벤치마크에서 메모리 미사용 정책 대비 성공률을 소폭 향상시켰다. | [arXiv](https://arxiv.org/abs/2610.12090v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **Residual Modeling Closes the Regression and Generative Policy Gap in Robot Learning** — HT-Policies는 로봇 시연 데이터의 heavy-tailed 잔차를 반영한 이질적 Student-t 회귀로, 기존 MSE 및 생성 정책과 유사한 성공률을 더 빠른 학습·추론으로 달성하였다. | [arXiv](https://arxiv.org/abs/2610.12231v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **PLaW-VLA: Predictive Latent World Modeling for Vision-Language-Action Policies** — PLaW-VLA는 예측 지향적 잠재공간에서 미래 상태를 모델링하여, 장기 제어와 분포 변화에 대한 일반화 성능을 실제 벤치마크에서 기존 정책 대비 개선하였다. | [arXiv](https://arxiv.org/abs/2610.12285v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **ARC: A Reasoning Recipe for Robot Foundation Models** — ARC는 로봇 파운데이션 모델의 제로샷 성능을 reasoning trace와 자동 라벨링 파이프라인을 통해 추가 데이터 없이 크게 향상시켰으며, 실제 로봇 실험에서 성공률을 대폭 개선하였다. | [arXiv](https://arxiv.org/abs/2610.12386v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **VersaCamVLA: Camera-Configurable VLA Policies for Robotic Manipulation** — VersaCamVLA는 카메라 구성이 달라져도 강인한 VLA 정책을 위해 카메라 집합 표현을 분리하고, 실제 로봇 및 다양한 벤치마크에서 기존 VLA 대비 일관된 성능 우위를 보였다. | [arXiv](https://arxiv.org/abs/2610.12451v1) |
| 2026-10-08 | 2026-10-08 | 연구 검증 | 긍정 | **DreamTrue: Action-Faithful Robot World Model with Counterfactual Post-Training** — DreamTrue는 다관점·다로봇 월드모델로, 실제 로봇 데이터셋의 한계를 극복하기 위해 오프라인 기하학적 보정과 반사실적 후학습을 도입하여, 실제 로봇 상에서 행동 충실도와 상호작용 결함률을 크게 개선하였다. | [arXiv](https://arxiv.org/abs/2610.12468v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 46.70점으로 단계 통과 기준에 미달합니다.
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
