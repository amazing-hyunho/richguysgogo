# Research-to-Market Radar — 로봇·자동화·자율주행

- 기준일: `2026-11-15`
- 현재 단계: **초기 관찰** (`emerging`)
- 체인 성숙도: **10.23/100**
- 근거 확신도: **15.31/100**
- 핵심 가설: 월드모델·VLA·범용 로봇 학습의 반복 가능한 성능 개선이 센서·액추에이터·제조 자동화 수요로 전달되는지 추적한다.

> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.

## 단계별 판정

| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |
|---|---:|---:|---:|---:|---|
| 연구 검증 | 40.91 | 61.25 | 11 | 1 | 미통과 |
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
| 2026-11-11 | 2026-11-11 | 연구 검증 | 긍정 | **Scaling VLA Serving Under Robotic Execution Constraints** — XInfer는 실제 수백 대의 VLA 기반 로봇이 운영되는 환경에서, VLA 추론 인프라 비용을 절감하고 실행 제약 하에서 로봇 처리량을 기존 대비 1.26~3.75배 향상시켰음을 실증했다. | [arXiv](https://arxiv.org/abs/2611.14969v1) |
| 2026-11-11 | 2026-11-11 | 연구 검증 | 긍정 | **CARE-Drive: Coupled Alternating Refinement for Ego-trajectories** — CARE-Drive는 자율주행 VLA 모델의 경로 예측을 위치·방향 특화 전문가로 분리·교차 최적화하여, 시뮬레이션 벤치마크에서 기존 대비 경로 품질을 개선함을 보였다. | [arXiv](https://arxiv.org/abs/2611.15360v1) |
| 2026-11-11 | 2026-11-11 | 연구 검증 | 중립 | **Low-Cost Mobile Bimanual Manipulation for Long-Horizon Toilet Cleaning** — 저비용 모바일 양팔 조작 플랫폼에서 VLA 기반 장기 화장실 청소 작업을 실험적으로 수행하여, 일부 모델이 제한적 성공률을 보였으나, 진행 신호·메모리 보강이 추가적 개선을 제공하지 않음을 밝혔다. | [arXiv](https://arxiv.org/abs/2611.15381v1) |
| 2026-11-11 | 2026-11-11 | 연구 검증 | 긍정 | **ActionCodec2: A Streaming Action Tokenizer** — ActionCodec2는 스트리밍 방식의 행동 토크나이저로, 실제 로봇 및 시뮬레이션에서 기존 토크나이저 대비 성능을 개선하고, 상태 피드백을 활용한 정책 실행의 견고성을 높였음을 보였다. | [arXiv](https://arxiv.org/abs/2611.15490v1) |
| 2026-11-11 | 2026-11-11 | 연구 검증 | 중립 | **What Makes a VLA Reactive? A Study of Execution Strategies for Dynamic Manipulation** — VLA의 반응성에 영향을 미치는 실행 전략(예측·실행 구간, 동기/비동기, 연속성 유지 등)을 실제 로봇 및 시뮬레이션에서 비교 분석하여, 정책 자체뿐 아니라 실행 파이프라인이 성능에 큰 영향을 미침을 밝혔다. | [arXiv](https://arxiv.org/abs/2611.15491v1) |
| 2026-11-11 | 2026-11-11 | 연구 검증 | 긍정 | **Recover, Don't Just Continue: Learning from Feedback for Physical Failure Understanding and Correction** — Embodied-Corrector는 실행 실패 원인 분석 및 복구 계획 학습을 통해, 실제 VLA 기반 복합 작업에서 성공률을 유의하게 향상시켰음을 보였다. | [arXiv](https://arxiv.org/abs/2611.15651v1) |
| 2026-11-11 | 2026-11-11 | 연구 검증 | 긍정 | **MOSAIC: Modular Obstacle and Spatial-Aware Framework for Manipulation In Cluttered Scenes** — MOSAIC은 VLA 기반 로봇 조작에 명시적 공간·장애물 인식 모듈을 추가하여, 실제 및 벤치마크 환경의 복잡한 장면에서 성공률을 개선함을 실험적으로 보였다. | [arXiv](https://arxiv.org/abs/2611.15937v1) |
| 2026-11-12 | 2026-11-12 | 연구 검증 | 긍정 | **What Can a VLA Learn from the Agent That Calls It? Task-Level Experience Distillation for Embodied Navigation** — H2E는 LLM 기반 플래너의 성공 경험을 VLA 모델로 증류하여, 실제 네비게이션 과제에서 VLA 단독 실행 시 성공률을 유의하게 향상시켰음을 보였다. | [arXiv](https://arxiv.org/abs/2611.16246v1) |
| 2026-11-12 | 2026-11-12 | 연구 검증 | 긍정 | **I See What You Want: Decoding Hierarchical Operator Intent from Visual Teleoperation History** — VIM은 시각 텔레오퍼레이션 기록에서 계층적 작업 의도를 해석하여, 실제 환경에서 VLA 정책이 인간 조작자를 대체해 작업 시간을 단축하고 의도 예측 지연을 크게 줄였음을 보였다. | [arXiv](https://arxiv.org/abs/2611.16419v1) |
| 2026-11-12 | 2026-11-12 | 연구 검증 | 긍정 | **STVLA: Spatial-aware and Temporal-memory forVision-Language-Action Models** — STVLA는 사전학습된 시각 기하 정보와 시각 표현을 통합한 메모리 구조를 도입하여, 실제 블록 쌓기·정리·포장 등 다양한 로봇 조작 과제에서 기존 방법 대비 성공률을 크게 향상시켰음을 실험적으로 입증했다. | [arXiv](https://arxiv.org/abs/2611.16589v1) |
| 2026-11-12 | 2026-11-12 | 연구 검증 | 긍정 | **SALA: Semantically Aligned Latent Actions Enable Dual-Axis Scaling of Embodied Foundation Models** — SALA는 언어 기반 의미 정렬을 통해 인간과 로봇의 비쌍(pairing) 데이터 없이도 잠재 행동 공간을 공유하고, 인간 비디오 사전학습 및 사후학습 데이터가 실제 로봇 작업 성공률과 행동 예측 오류 개선에 반복적으로 기여함을 실험적으로 보였다. | [arXiv](https://arxiv.org/abs/2611.17110v1) |

## 데이터 공백과 한계

- 연구 검증: 순신호 40.91점으로 단계 통과 기준에 미달합니다.
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
