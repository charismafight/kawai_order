from playwright.sync_api import sync_playwright
import time


def load_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=False)  # 直接使用 Edge

        page = browser.new_page()

        print("正在加载页面...")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)

        html = page.content()
        print(f"✅ 成功！页面长度: {len(html)} 字符")

        browser.close()
        return html


content = load_with_playwright("https://tokyokawaiilife.com")
