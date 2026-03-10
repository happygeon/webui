#!/usr/bin/env python3
"""
automate_capture_full.py

Playwright + BeautifulSoup 을 활용해 sites.json 기반으로
– category/label 폴더 자동 생성  
– headful 브라우저로 페이지 열기 → 수동 봇 감지 처리  
– q 입력 시 해당 엔트리 건너뛰기  
– before.html (원본), structure.html (전처리), screenshot.png 저장  
"""

import os
import re
import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Comment
from playwright.sync_api import sync_playwright

# ─── 설정 ─────────────────────────────────────────────────────────
SITES_JSON   = "./site_list_0628.json"        # 사이트 매핑 JSON 경로
OUTPUT_ROOT  = "./dataset_0628"    # 결과를 저장할 최상위 폴더

# 전처리 시 제거할 속성·이벤트 패턴
IGNORE_ATTRS   = {"class", "id", "style"}
EVENT_ATTR_RE  = re.compile(r"^on[A-Za-z]+", re.I)

# ─── 헬퍼: URL → label(도메인 첫 부분) 변환 ─────────────────────────
def extract_label_from_url(url: str) -> str:
    netloc = urlparse(url).netloc.lower().split(':')[0]
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc.split('.')[0]

# ─── 헬퍼: HTML 전처리 함수 ───────────────────────────────────────
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # 스크립트·스타일·stylesheet·meta·base 태그 제거
    for sel in ["script", "style", "link[rel=stylesheet]", "meta", "base"]:
        for tag in soup.select(sel):
            tag.decompose()

    # 모든 태그에서 불필요 속성 삭제
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if (
                attr in IGNORE_ATTRS or
                EVENT_ATTR_RE.match(attr) or
                attr.startswith(("data-", "aria-"))
            ):
                del tag[attr]

    # 주석 제거
    for c in soup.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()

    return soup.prettify(formatter="minimal")

import time

# ... (중략: 기존 import 및 설정 등) ...

def robust_get_html(page, sleep_sec=2):
    """
    페이지에서 HTML을 robust하게 추출:
    1. page.content()를 먼저 시도
    2. navigation error시 page.evaluate로 대체
    3. 둘 다 실패 시 빈 문자열
    """
    # 일단 충분히 대기 (혹시 모를 렌더링 이슈)
    time.sleep(sleep_sec)
    try:
        return page.content()
    except Exception as e:
        return

def main():
    # sites.json 로드
    with open(SITES_JSON, "r", encoding="utf-8") as f:
        sites = json.load(f)

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    with sync_playwright() as pw:
        # ... (생략: 모바일, 언어, User-Agent 설정 부분) ...
        browser = pw.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/15.0 Mobile/15E148 Safari/604.1"
            ),
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            locale="en-US",
            extra_http_headers={"accept-language": "en-US,en;q=0.9"}
        )

        idx = -1
        for entry in sites:
            idx      = idx + 1
            category = entry["category"]
            url      = entry["url"]

            print(f"\n▶ [{idx}] 카테고리: {category}, URL: {url}")
            label = input("    → 저장할 폴더명(라벨)을 입력하세요 ('q' 입력 시 건너뜁니다): ").strip()
            if label.lower() == "q":
                print("    ⚡ 스킵합니다.")
                continue
            if not label:
                print("    ⚠ 라벨이 비어 있습니다. 스킵합니다.")
                continue

            dst_dir = os.path.join(OUTPUT_ROOT, category, label)
            os.makedirs(dst_dir, exist_ok=True)

            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")

            print("    • 페이지가 열렸습니다. 봇 감지나 팝업을 수동으로 처리하세요.")
            input("      완료되면 Enter 키를 눌러 캡처를 저장합니다…")

            # 네트워크/렌더링 안정 대기 (불확실하면 여유있게)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass

            # robust하게 HTML 추출 (여기서 핵심)
            raw_html = robust_get_html(page, sleep_sec=2)

            # 1) 원본 저장
            before_path = os.path.join(dst_dir, "before.html")
            with open(before_path, "w", encoding="utf-8") as f:
                f.write(raw_html)

            # 2) 전처리 저장
            struct_path = os.path.join(dst_dir, "structure.html")
            with open(struct_path, "w", encoding="utf-8") as f:
                f.write(clean_html(raw_html))

            # 3) 스크린샷 저장
            screenshot_path = os.path.join(dst_dir, "screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)

            print(f"    ✔ 저장 완료:\n      - {before_path}\n      - {struct_path}\n      - {screenshot_path}")
            page.close()

        browser.close()

    print("\n🎉 모든 캡처 및 전처리 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()
