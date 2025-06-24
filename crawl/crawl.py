import os
import json
import requests
from playwright.sync_api import sync_playwright

# Default headers to reduce 403 errors when fetching HTML
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

# Block common analytics/ads to speed up networkidle
BLOCKED_RESOURCE_PATTERNS = [
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "adsystem.com",
    "adservice.google.com"
]

def crawl_and_capture(sites, output_dir='output'):
    """
    Fetch HTML (with headers + fallback), capture full-page screenshots
    with robust timeout and minimal waiting, and save metadata including purpose.

    :param sites: List of dicts with 'url', 'category', 'purpose'.
    :param output_dir: Base directory for html, screenshots, metadata.
    """
    html_dir = os.path.join(output_dir, 'html')
    img_dir = os.path.join(output_dir, 'screenshots')
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        # Block trackers/ads
        context.route("**/*", lambda route, request: (
            route.abort() if any(pat in request.url for pat in BLOCKED_RESOURCE_PATTERNS)
            else route.continue_()
        ))
        # Extend default timeouts
        context.set_default_navigation_timeout(120000)  # 2 minutes
        context.set_default_timeout(120000)

        i = -1
        for site in sites:
            i += 1
            url = site.get('url')
            category = site.get('category', '')
            purpose = site.get('purpose', '')
            if not url:
                print(f"Skipping invalid entry: {site}")
                continue

            safe_name = url.replace('://', '_').replace('/', '_').strip('_')

            # 1. HTML fetch with headers and fallback to Playwright
            html_content = None
            html_path = os.path.join(html_dir, f"{i}.html")
            try:
                resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
                resp.raise_for_status()
                html_content = resp.text
            except Exception:
                try:
                    page = context.new_page()
                    page.goto(url, timeout=120000, wait_until='domcontentloaded')
                    html_content = page.content()
                    page.close()
                except Exception as e:
                    print(f"HTML fetch failed for {url}: {e}")

            if html_content:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

            # 2. Screenshot with minimal waiting
            try:
                page = context.new_page()
                page.goto(url, timeout=120000, wait_until='domcontentloaded')
                page.wait_for_timeout(5000)  # wait 5 seconds for images
                screenshot_path = os.path.join(img_dir, f"{i}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                page.close()
            except Exception as e:
                print(f"Screenshot failed for {url}: {e}")

            results.append({
                'index': i,
                'url': url,
                'category': category,
                'purpose': purpose
            })

        browser.close()

    # Save metadata JSON
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'sites.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Crawl static HTML and capture screenshots with robust timeout'
    )
    parser.add_argument('-i', '--input', default='sites_list.json', help='JSON file with list of sites')
    parser.add_argument('-o', '--output', default='output', help='Directory to save results')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            sites = json.load(f)
    except Exception as e:
        print(f"Could not load input JSON '{args.input}': {e}")
        exit(1)

    crawl_and_capture(sites, output_dir=args.output)

# Requirements:
#   pip install requests playwright
#   playwright install
