# A11yn: Aligning LLMs for Accessible Web UI Code Generation

GRPO(Group Relative Policy Optimization) 강화학습으로 코드 생성 LLM의 출력을 WCAG 접근성 기준에 정렬(align)하는 프레임워크입니다.

## Overview

LLM이 생성하는 웹 UI 코드는 학습 데이터의 접근성 결함을 그대로 재현합니다. A11yn은 생성 후 반복 수정(Feeda11y 등) 대신, **모델 자체가 접근성을 준수하는 코드를 생성하도록 GRPO로 학습**시키는 접근을 취합니다.

- **Accessibility Reward**: axe-core 기반 WCAG 위반 탐지 → 심각도별 차등 페널티 보상 함수
- **Training**: 6,800개 합성 프롬프트(prompt-only)로 Qwen2.5-Coder-7B-Instruct를 GRPO 학습
- **Evaluation**: 300개 실제 웹사이트 기반 평가셋, WVS/Inaccessibility Rate 지표

## Architecture

```
Prompt (NL UI Request)
    ↓
Policy Model (Qwen2.5-Coder-7B) → G개 후보 코드 생성 (Rollout)
    ↓
Accessibility Reward (axe-core WCAG 위반 → 심각도별 가중 페널티 → 보상 산출)
    ↓
Group Computation (그룹 내 보상 정규화 → Advantage 계산)
    ↓
Policy Update (GRPO Objective + KL Divergence 정규화)
```

## Accessibility Reward

생성된 HTML을 axe-core로 검사하고, 위반 심각도에 따라 차등 페널티를 부과합니다.

| Severity | Penalty |
|----------|---------|
| Minor | -0.1 |
| Moderate | -0.2 |
| Serious | -0.3 |
| Critical | -0.4 |

```
reward = 2.0 - Σ(severity_weight × violation_count)
```

Ablation Study에서 균일 페널티(-0.2 고정) 대비 차등 가중치가 Serious 85.5%, Critical 60% 추가 감소를 달성했습니다.

## Dataset

| | Training Set | Evaluation Set |
|---|---|---|
| **크기** | 6,800 prompts | 300 queries |
| **소스** | 68개 도메인 카테고리 합성 생성 | 실제 웹사이트 크롤링 + VLM 캡셔닝 |
| **형태** | Prompt-only (ground-truth 코드 없음) | UI 목적, 페이지 유형, 도메인, 필수 컴포넌트 |

## Training

- **Base Model**: Qwen2.5-Coder-7B-Instruct
- **Framework**: HuggingFace TRL (GRPOTrainer) + vLLM
- **Infrastructure**: 8× NVIDIA A6000 (48GB), bfloat16
- **Config**: G=6 completions/prompt, β=0.001 (KL), Dr.GRPO loss, Cosine LR 5e-5

## Results

| Model | WVS (↓) | Inaccessibility Rate (↓) |
|-------|---------|--------------------------|
| Qwen2.5-Coder-7B (base) | 8091 | 0.42 |
| + Feeda11y | 2440 | 0.143 |
| Qwen2.5-Coder-14B | 8313 | 0.415 |
| GPT-4.1 | 8206 | 0.277 |
| Claude Sonnet 4 | 11197 | 0.29 |
| **A11yn (Ours)** | **1583** | **0.127** |

Appearance Score(5점 척도): base 3.28 → A11yn 3.07 (미적 품질 저하 최소화)

## Project Structure

```
├── data_collection/            # 평가 데이터셋 큐레이션 (크롤링 & 캡셔닝)
│   ├── crawl.py                # 자동 크롤러 (Playwright)
│   ├── capture_playwright.py   # 수동 캡처 (봇 감지 대응)
│   ├── capture_selenium.py     # 수동 캡처 (Selenium)
│   ├── captioning.py           # VLM 기반 스크린샷 메타데이터 추출
│   ├── minimize_html.py        # HTML 간소화
│   ├── count_dom.py            # DOM 노드 수 집계
│   └── site_lists/             # 크롤링 대상 사이트 목록
│
├── training/                   # GRPO 학습
│   ├── grpo_train.ipynb        # 메인 학습 노트북
│   └── grpo_train_qwen1.5b.ipynb
│
├── evaluation/                 # 접근성 평가
│   ├── eval.py                 # 보상 함수 구현
│   ├── main.py                 # 평가 실행
│   └── visualization/          # 결과 시각화
│
├── generation/                 # 베이스라인 추론
│   ├── LLM.py                  # 통합 LLM 래퍼 (GPT-4o, Claude, Llama, Gemma)
│   ├── text2html.py            # 프롬프트 → HTML 생성
│   └── html_gen_api.py         # Qwen API 클라이언트
│
├── expert_evaluation/          # 외관 품질 평가 (Appearance Score)
├── token_analysis/             # 토큰 수 분석
├── dataset_processing/         # 데이터셋 후처리
│
└── data/
    ├── ui_design_data.json     # 학습 데이터셋 (6,800 prompts)
    ├── data_merged_raw/        # 원본 크롤링 데이터
    └── data_merged/            # 전처리된 데이터
```

## Tech Stack

| Component | Tools |
|-----------|-------|
| Training | TRL (GRPOTrainer), vLLM, DeepSpeed |
| Model | Qwen2.5-Coder-7B-Instruct |
| Crawling | Playwright, Selenium |
| Accessibility | axe-core (Pyppeteer) |
| APIs | OpenAI, Anthropic, Groq, Unsplash |
| Analysis | BeautifulSoup, Pandas, Matplotlib |
