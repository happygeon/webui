#!/usr/bin/env python3
"""
automate_capture_full_selenium.py

– sites.json 기반으로  
  • category/label 폴더 자동 생성  
  • headful 브라우저로 페이지 열기 → 수동 봇 감지/팝업 처리  
  • 'q' 입력 시 해당 엔트리 건너뛰기  
  • before.html, structure.html, screenshot.png 저장  
"""

import os
import re
import json
import time
import base64
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Comment

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ─── 원본 설정 (경로 및 파일명: 요청 반영) ─────────────────────────────────
CHROMEDRIVER_PATH = "./chromedriver-win64/chromedriver.exe"
OUTPUT_ROOT        = "dataset_0630"            # 결과를 저장할 최상위 폴더
SITES_JSON         = "site_list_0630.json"

IGNORE_ATTRS  = {"class", "id", "style"}
EVENT_ATTR_RE = re.compile(r"^on[A-Za-z]+", re.I)

def clean_html(html: str) -> str:
    """BeautifulSoup 기반 전처리 (스크립트·스타일·주석 제거)"""
    soup = BeautifulSoup(html, "html.parser")
    for sel in ["script", "style", "link[rel=stylesheet]", "meta", "base"]:
        for tag in soup.select(sel):
            tag.decompose()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr in IGNORE_ATTRS or EVENT_ATTR_RE.match(attr) or attr.startswith(("data-", "aria-")):
                del tag[attr]
    for c in soup.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()
    return soup.prettify(formatter="minimal")


def main():
    # 1) sites.json 로드
    with open(SITES_JSON, "r", encoding="utf-8") as f:
        sites = json.load(f)

    # 2) OUTPUT_ROOT 생성
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    # 3) Selenium 드라이버 준비 (헤드풀 모드 해제)
    MOBILE_EMULATION = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/15.0 Mobile/15E148 Safari/604.1"
        )
    }
    chrome_opts = Options()
    chrome_opts.add_experimental_option("mobileEmulation", MOBILE_EMULATION)
    # headless 모드 해제 → 실제 창이 뜹니다
    # chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--hide-scrollbars")

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_opts)

    for entry in sites:
        category = entry["category"]
        url      = entry["url"]

        print(f"\n▶ 카테고리: {category}, URL: {url}")
        label = input("    → 저장할 폴더명(라벨)을 입력하세요 ('q' 입력 시 건너뜁니다): ").strip()
        if label.lower() == "q":
            print("    ⚡ 스킵합니다.")
            continue
        if not label:
            print("    ⚠ 라벨이 비어 있습니다. 스킵합니다.")
            continue

        # ─── dst_dir 설정 (원본 그대로) ────────────────────────────────────
        dst_dir = os.path.join(OUTPUT_ROOT, category, label)
        os.makedirs(dst_dir, exist_ok=True)

        # 4) 페이지 열기 & 수동 처리 대기
        driver.get(url)
        print("    • 페이지가 열렸습니다. 봇 감지나 팝업을 수동으로 처리하세요.")
        input("      완료되면 Enter 키를 눌러 캡처를 저장합니다…")
        time.sleep(2)  # 네트워크/렌더링 안정 대기

        # 5) HTML 추출 및 저장
        raw_html = driver.page_source
        before_path = os.path.join(dst_dir, "before.html")
        with open(before_path, "w", encoding="utf-8") as f:
            f.write(raw_html)

        struct_path = os.path.join(dst_dir, "structure.html")
        with open(struct_path, "w", encoding="utf-8") as f:
            f.write(clean_html(raw_html))

        # 6) 전체 페이지 크기 측정 & 뷰포트 조정
        metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
        w = metrics["contentSize"]["width"]
        h = metrics["contentSize"]["height"]
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "mobile": True,
            "width": w,
            "height": h,
            "deviceScaleFactor": MOBILE_EMULATION["deviceMetrics"]["pixelRatio"],
        })

        # 7) 스크린샷 저장
        shot = driver.execute_cdp_cmd("Page.captureScreenshot", {
            "fromSurface": True,
            "clip": {"x":0, "y":0, "width":w, "height":h, "scale":1}
        })
        img_data = base64.b64decode(shot["data"])
        screenshot_path = os.path.join(dst_dir, "screenshot.png")
        with open(screenshot_path, "wb") as img:
            img.write(img_data)

        print(f"    ✔ 저장 완료:\n      - {before_path}\n      - {struct_path}\n      - {screenshot_path}")

    driver.quit()
    print("\n🎉 모든 캡처 및 전처리 작업이 완료되었습니다!")


if __name__ == "__main__":
    main()