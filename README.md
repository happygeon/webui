# A11yn: GRPO 기반 접근성 준수 웹 UI 코드 생성

LLM이 자연어로부터 **WCAG 접근성을 준수하는** 웹 UI 코드를 생성하도록, **GRPO (Group Relative Policy Optimization)** 강화학습으로 정렬(align)하는 프레임워크입니다.

## 배경 및 문제 정의

LLM 기반 웹 UI 코드 생성 기술이 빠르게 발전하고 있지만, 생성된 코드의 **웹 접근성(Accessibility)**은 심각하게 간과되고 있습니다. 공개 웹사이트의 90% 이상에서 WCAG 위반이 탐지되며, LLM은 이러한 결함이 포함된 대규모 웹 코퍼스로 학습되기 때문에 생성 코드에서도 접근성 문제를 그대로 재현합니다 — 시맨틱 랜드마크 누락, 이미지 alt 텍스트 부재, 불충분한 명암 대비 등이 대표적입니다.

기존 접근법(Feeda11y 등)은 생성 후 반복적으로 LLM에게 위반 사항을 피드백하여 수정하는 방식이지만, 반복마다 추가 추론이 필요해 계산 비용이 높고 느립니다. **A11yn**은 근본적으로 다른 접근을 취합니다: **LLM이 처음부터 접근성을 준수하는 코드를 생성하도록 학습**시킵니다.

## 시스템 아키텍처

```
Prompt (자연어 UI 요청)
          ↓
┌─────────────────────────┐
│  Policy Model            │
│  (Qwen2.5-Coder-7B)     │
│                          │
│  G개의 UI 코드 생성       │
│  (Rollout)               │
└────────┬─────────────────┘
         ↓
┌─────────────────────────┐
│  Accessibility Reward    │
│                          │
│  axe-core WCAG 위반 탐지 │
│  → 심각도별 가중 페널티   │
│  → 보상 점수 산출         │
└────────┬─────────────────┘
         ↓
┌─────────────────────────┐
│  Group Computation       │
│                          │
│  그룹 내 보상 정규화      │
│  → 상대적 Advantage 계산  │
└────────┬─────────────────┘
         ↓
Policy Update (GRPO Objective)
+ KL Divergence 정규화 (Reference Model)
```

## 핵심 구현 내용

### 1. 접근성 보상 함수 설계

프로젝트의 핵심 기여입니다. 모델이 생성한 HTML 코드를 **axe-core**(산업 표준 WCAG 검사 도구)로 검사하고, 탐지된 위반의 심각도에 따라 차등 페널티를 부과합니다.

| 심각도 | 페널티 | 예시 |
|--------|--------|------|
| **Minor** | -0.1 | 사소한 접근성 미비 |
| **Moderate** | -0.2 | 폼 라벨 누락 등 |
| **Serious** | -0.3 | 명암 대비 부족, 랜드마크 누락 |
| **Critical** | -0.4 | 스크린 리더 완전 차단 등 |

```
reward = 2.0 - Σ(severity_weight × violation_count)
```

위반이 없으면 최대 보상 2.0, 심각한 위반일수록 보상이 급격히 감소합니다. Ablation Study에서 균일 페널티(-0.2 고정)와 비교한 결과, **차등 가중치가 Serious 위반을 85.5%, Critical 위반을 60% 더 감소**시켰습니다. 균일 페널티는 오히려 Critical 위반이 80% 증가하는 역효과가 나타났습니다.

### 2. 데이터셋 구축

**학습 데이터셋 (6,800개, prompt-only):**
- 68개 도메인 카테고리(e-commerce, healthcare, education 등)에 걸쳐 자연어 UI 요청 프롬프트를 합성 생성
- Ground-truth 코드 없이 프롬프트만으로 학습 가능 — GRPO가 보상 시그널만으로 최적화
- SFT 방식에서 "접근성 완벽한 정답 코드"를 대량 확보해야 하는 비현실적 요구를 우회

**평가 데이터셋 (300개, 실제 웹사이트 기반):**
- 실제 공개 웹사이트를 Playwright/Selenium으로 크롤링하고 스크린샷 캡처
- VLM(Claude API)으로 스크린샷에서 메타데이터 추출: UI 목적, 페이지 유형, 도메인, 필수 컴포넌트
- 추출된 메타데이터를 구조화하여 평가 쿼리셋으로 변환

### 3. GRPO 학습

- **베이스 모델**: Qwen2.5-Coder-7B-Instruct
- **학습 프레임워크**: HuggingFace TRL (GRPOTrainer) + vLLM 기반 샘플링
- **인프라**: 8× NVIDIA A6000 (48GB), bfloat16 mixed-precision
- 프롬프트당 **G=6**개의 후보 코드를 생성하고, 그룹 내 보상을 정규화하여 상대적으로 나은 출력에 업데이트를 집중
- **Dr.GRPO** loss variant를 적용하여 시퀀스 길이 편향을 보정
- KL divergence 정규화(β=0.001)로 frozen reference model 대비 과도한 policy drift 방지

### 4. 평가 체계

| 지표 | 설명 |
|------|------|
| **심각도별 위반 수** | Minor/Moderate/Serious/Critical 각각의 평균 위반 횟수 |
| **WVS (Weighted Violation Score)** | 심각도 가중 위반 점수 (Minor×1 + Moderate×2 + Serious×3 + Critical×4) |
| **Inaccessibility Rate** | WVS / 전체 DOM 요소 수 (UI 복잡도를 보정한 정규화 지표) |

추가로 WebGenBench의 **Appearance Score**(GPT-4.1이 5점 척도로 미적 품질 평가)를 사용하여, 접근성 개선이 디자인 품질을 훼손하지 않는지도 확인했습니다.

## 프로젝트 구조

```
├── data_collection/            # 평가 데이터셋 큐레이션 (크롤링 & 캡셔닝)
│   ├── crawl.py                # 자동 크롤러 (Playwright, headless)
│   ├── capture_playwright.py   # 수동 캡처 (봇 감지 대응, Playwright)
│   ├── capture_selenium.py     # 수동 캡처 (Selenium)
│   ├── captioning.py           # Claude API로 스크린샷 메타데이터 추출
│   ├── minimize_html.py        # GPT API로 HTML 간소화
│   ├── structure_html_preprocess.py  # HTML 정제 및 전처리
│   ├── count_dom.py            # DOM 노드 수 집계
│   └── site_lists/             # 크롤링 대상 사이트 목록
│
├── dataset_processing/         # 데이터셋 후처리
│   ├── dataset_modify.py       # Unsplash API로 실제 이미지 삽입
│   └── img_insert_prompt.txt   # 이미지 삽입 프롬프트
│
├── training/                   # GRPO 학습
│   ├── grpo_train.ipynb        # 메인 GRPO 학습 (Qwen2.5-Coder-7B)
│   └── grpo_train_qwen1.5b.ipynb  # 초기 실험 (Qwen2.5-1.5B)
│
├── evaluation/                 # 접근성 평가
│   ├── eval.py                 # 보상 함수 (구조 검증, 접근성, 색상 분석)
│   ├── main.py                 # 평가 실행
│   └── visualization/          # 평가 결과 시각화
│
├── generation/                 # LLM 기반 HTML 생성 (베이스라인 추론)
│   ├── LLM.py                  # 통합 LLM 래퍼 (GPT-4o, Claude, Llama, Gemma)
│   ├── text2html.py            # 프롬프트 → HTML 생성
│   └── html_gen_api.py         # Qwen2.5-Coder API 클라이언트
│
├── expert_evaluation/          # 외관 품질 평가
│   ├── build_form.gs           # Google Apps Script (평가 설문 자동 생성)
│   ├── select_image.py         # Tkinter GUI (이미지 비교 & 순위 선정)
│   └── trans.py                # 캡션 번역 유틸리티
│
├── token_analysis/             # 모델별 토큰 수 분석
│
└── data/                       # 데이터셋
    ├── ui_design_data.json     # 학습 데이터셋 (6,800 프롬프트)
    ├── data_merged_raw/        # 원본 크롤링 데이터 (HTML + 스크린샷)
    └── data_merged/            # 전처리된 데이터
```

## 결과

A11yn은 5개 베이스라인을 모두 능가했습니다.

| 모델 | WVS (↓) | Inaccessibility Rate (↓) |
|------|---------|--------------------------|
| Qwen2.5-Coder-7B (base) | 8091 | 0.42 |
| Qwen-7B + Feeda11y | 2440 | 0.143 |
| Qwen2.5-Coder-14B | 8313 | 0.415 |
| GPT-4.1 | 8206 | 0.277 |
| Claude Sonnet 4 | 11197 | 0.29 |
| **A11yn (Ours)** | **1583** | **0.127** |

**핵심 개선:**
- Serious 위반: 1231 → 179 (85.5% 감소)
- Region(랜드마크) 위반: 1856 → 399
- Color contrast 위반: 863 → 176
- Link-name 위반: 203 → 3
- Appearance Score: base model 3.28 대비 3.07로 미적 품질 저하 최소화
- Feeda11y가 반복당 평균 4,584 토큰을 소모하는 반면, A11yn은 **single forward pass**로 동일 수준 달성

## 기술적 의사결정

| 의사결정 | 선택 | 이유 |
|---------|------|------|
| 학습 방식 | GRPO (RL) | 접근성 완벽한 "정답 코드" 대량 확보 불가 → 보상 시그널 기반 RL이 유일한 현실적 방법 |
| 보상 설계 | 심각도별 차등 가중치 | Ablation에서 균일 페널티가 Critical 위반 오히려 증가 → 차등 가중치가 심각한 위반부터 제거 유도 |
| 베이스 모델 | Qwen2.5-Coder-7B-Instruct | 웹 코드 생성 특화 사전학습, 오픈소스로 GRPO 적용 가능 |
| WCAG 검사 도구 | axe-core | 산업 표준 오픈소스 접근성 엔진, 심각도 4단계 분류 제공 |
| 학습 안정화 | Dr.GRPO + KL 정규화 | 시퀀스 길이 편향 보정 + reference model 대비 과도한 drift 방지 |
| 평가셋 | 실제 웹사이트 크롤링 기반 300개 | 합성 프롬프트가 아닌 real-world 시나리오에서의 일반화 검증 |

## 본인 기여

4인 팀에서 다음을 담당했습니다:

- **평가 데이터셋 크롤링 및 구축**: Playwright/Selenium 기반 크롤링 파이프라인, VLM 캡셔닝을 통한 메타데이터 추출, 300개 평가셋 큐레이션
- **아키텍처 및 보상 함수 설계**: axe-core 기반 심각도별 차등 페널티 보상 함수 설계, GRPO 학습 파이프라인 구조 설계
- **논문 작성**: Anonymous submission으로 학회 제출

## 회고

이 프로젝트에서 가장 큰 인사이트는 **"정답이 없는 영역에서도 RL이 작동한다"**는 것이었습니다. 접근성이 완벽한 UI 코드의 ground-truth를 대량으로 확보하는 건 비현실적이지만, axe-core라는 자동 검사 도구를 보상 시그널로 활용하면 prompt-only 데이터만으로 의미 있는 정렬이 가능했습니다.

보상 함수 설계에서는 Ablation Study가 결정적이었습니다. 직관적으로 "위반은 다 똑같이 나쁘다"고 생각하고 균일 페널티를 적용했을 때, 오히려 Critical 위반이 증가하는 역효과가 발생했습니다. 심각한 위반에 더 큰 페널티를 부여해야 모델이 "무엇부터 고쳐야 하는지"를 학습한다는 것을 경험적으로 확인했고, 이는 **RL에서 보상 설계가 왜 핵심인지를 체감한 계기**였습니다.

또한 접근성과 미적 품질 사이의 트레이드오프를 정량적으로 측정한 경험은, "사용자 경험"이라는 복합적인 목표를 ML로 최적화할 때 어떤 지표를 세우고 어떻게 균형을 잡아야 하는지에 대한 실질적인 감각을 키워주었습니다.

## 기술 스택

- **학습**: HuggingFace TRL (GRPOTrainer) + vLLM + DeepSpeed
- **모델**: Qwen2.5-Coder-7B-Instruct
- **크롤링**: Playwright, Selenium
- **API**: OpenAI (GPT-4o-mini), Anthropic (Claude 3.5 Sonnet), Groq (Llama), Unsplash
- **접근성 평가**: axe-core (Pyppeteer), BeautifulSoup
- **시각화**: Pandas, Matplotlib
