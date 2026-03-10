# WebUI: GRPO 강화학습 기반 UI 코드 생성

자연어 요청으로부터 고품질 HTML/CSS/JS를 생성하도록 LLM을 **GRPO (Group Relative Policy Optimization)** 강화학습으로 파인튜닝하는 프로젝트입니다.

## 개요

[Qwen2.5-Coder](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct) 모델을 디자인 품질 기반 보상 함수로 학습시켜, 구조적으로 올바르고 시각적으로 조화로운 웹 UI 코드를 생성합니다.

- 100개 이상의 실제 웹사이트 크롤링으로 구축한 **6,800개 쿼리-HTML 데이터셋**
- **다중 보상 기반 GRPO 학습**: 출력 포맷, 색상 조화, 명암 대비(WCAG), 채도/명도 균형, CSS 완성도, 접근성(axe-core)
- 다중 모델 평가 파이프라인 (GPT-4o, Claude, Llama, Gemma)
- Google Forms 기반 전문가 휴먼 평가

## 파이프라인

```
1. 데이터 수집      →  웹사이트 크롤링, 스크린샷 캡처, HTML 추출
2. 데이터 가공      →  HTML 정제, 캡션 생성, 구조 간소화, 실제 이미지 삽입
3. GRPO 학습       →  디자인 품질 보상 함수로 Qwen2.5-Coder 파인튜닝
4. HTML 생성       →  자연어 → HTML 변환 (다중 LLM 활용)
5. 평가            →  자동 품질 평가 + 전문가 순위 평가
```

## 프로젝트 구조

```
├── data_collection/         # 웹 크롤링 & 스크린샷 캡처
│   ├── crawl.py             # 자동 크롤러 (Playwright, headless)
│   ├── capture_playwright.py # 수동 캡처 (봇 감지 대응, Playwright)
│   ├── capture_selenium.py  # 수동 캡처 (Selenium)
│   ├── captioning.py        # Claude API로 스크린샷 캡션 생성
│   ├── minimize_html.py     # GPT API로 HTML 간소화
│   └── site_lists/          # 크롤링 세션별 대상 사이트 목록
│
├── dataset_processing/      # 데이터셋 가공
│   ├── dataset_modify.py    # Unsplash API로 실제 이미지 삽입
│   └── img_insert_prompt.txt
│
├── training/                # 모델 학습
│   ├── grpo_train.ipynb     # 메인 GRPO 학습 (Qwen2.5-Coder-0.5B)
│   └── grpo_train_qwen1.5b.ipynb  # 초기 실험 (Qwen2.5-1.5B)
│
├── evaluation/              # HTML 품질 평가
│   ├── eval.py              # 보상 함수 클래스 (구조, 반응형, 색상 조화, CSS)
│   └── main.py              # 생성 결과물 평가 실행
│
├── generation/              # LLM 기반 HTML 생성
│   ├── LLM.py              # 통합 LLM 래퍼 (GPT-4o, Claude, Llama, Gemma)
│   ├── text2html.py         # 프롬프트 → HTML 생성
│   └── html_gen_api.py      # Qwen2.5-Coder 데모 API 클라이언트
│
├── expert_evaluation/       # 전문가 평가
│   ├── build_form.gs        # Google Apps Script (평가 설문 자동 생성)
│   ├── select_image.py      # Tkinter GUI (이미지 비교 & 순위 선정)
│   └── trans.py             # 캡션 번역 유틸리티
│
├── token_analysis/          # 모델별 토큰 수 분석
│
└── data/                    # 데이터셋
    ├── ui_design_data.json  # 메인 학습 데이터셋 (6,800쌍)
    ├── data_merged_raw/     # 원본 크롤링 데이터 (HTML + 스크린샷)
    └── data_merged/         # 전처리된 텍스트 데이터
```

## 보상 함수 (GRPO)

GRPO 학습에 사용되는 다중 보상 시그널:

| 보상 | 설명 |
|------|------|
| **포맷** | `<think>...</think><html>...</html>` 출력 구조 준수 여부 |
| **명암 대비** | WCAG 2.0 텍스트-배경 대비율 (≥ 4.5:1) |
| **색상 거리** | Delta E (CIE2000) 색상 간 차이 |
| **채도/명도** | 색상이 균형 잡힌 범위 내에 있는지 검증 |
| **색상 조화** | 단색, 유사색, 보색 등 팔레트 조화 검사 |
| **CSS 완성도** | 반응형 단위, hover 효과, transition 존재 여부 |
| **접근성** | axe-core WCAG 2.0 AA 위반 감점 |

## 기술 스택

- **학습**: [Unsloth](https://github.com/unslothai/unsloth) + [TRL](https://github.com/huggingface/trl) (GRPO)
- **모델**: Qwen2.5-Coder-0.5B-Instruct (4-bit 양자화)
- **크롤링**: Playwright, Selenium
- **API**: OpenAI (GPT-4o-mini), Anthropic (Claude 3.5 Sonnet), Groq (Llama), Unsplash
- **평가**: BeautifulSoup, colorspacious, axe-core (Pyppeteer)
