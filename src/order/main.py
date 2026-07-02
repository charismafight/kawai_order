import time
import schedule
import requests
import smtplib
import importlib
import sys
import urllib.parse
from email.mime.text import MIMEText
from bs4 import BeautifulSoup  # 需要安装: pip install beautifulsoup4

# ---------------------------- 配置 ----------------------------
CHECK_INTERVAL_SECONDS = 5
HEALTH_CHECK_MINUTES = 30

EMAIL_RECIPIENTS = ["yinmingcan1999@gmail.com", "charismafight@hotmail.com", "604670240@qq.com", "1401437683@qq.com"]

SMTP_CONFIG = {"server": "smtp.exmail.qq.com", "port": 25, "username": "ll@champath.cn", "password": "76fUP3YVFak7VTnJ"}

# 搜索基础URL
SEARCH_BASE_URL = "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/GoodsSearchList.html"

# ---------------------------- 全局变量 ----------------------------
TOKYO_ITEMS = []
URL_WATCH_LIST = []
KEYWORD_WATCH_LIST = []


# ---------------------------- 动态加载函数 ----------------------------
def load_config_data():
    """动态加载配置文件，每次调用都会重新读取文件内容"""
    global TOKYO_ITEMS, URL_WATCH_LIST, KEYWORD_WATCH_LIST

    # 1. Load Tokyo Items
    try:
        if "tokyo_items_data" in sys.modules:
            tokyo_module = importlib.reload(sys.modules["tokyo_items_data"])
        else:
            tokyo_module = __import__("tokyo_items_data")
        TOKYO_ITEMS = getattr(tokyo_module, "TOKYO_ITEMS_DATA", [])
    except Exception as e:
        print(f"[配置错误] 加载 tokyo_items_data.py 失败: {e}")
        TOKYO_ITEMS = []

    # 2. Load URL Watch List
    try:
        if "url_watch_data" in sys.modules:
            url_module = importlib.reload(sys.modules["url_watch_data"])
        else:
            url_module = __import__("url_watch_data")
        URL_WATCH_LIST = getattr(url_module, "URL_WATCH_DATA", [])
    except Exception as e:
        print(f"[配置错误] 加载 url_watch_data.py 失败: {e}")
        URL_WATCH_LIST = []

    # 3. Load Keyword Watch List (新增)
    try:
        if "keyword_watch_data" in sys.modules:
            keyword_module = importlib.reload(sys.modules["keyword_watch_data"])
        else:
            keyword_module = __import__("keyword_watch_data")
        KEYWORD_WATCH_LIST = getattr(keyword_module, "KEYWORD_WATCH_DATA", [])
    except Exception as e:
        print(f"[配置错误] 加载 keyword_watch_data.py 失败: {e}")
        KEYWORD_WATCH_LIST = []


# ---------------------------- 邮件发送函数 ----------------------------
def send_mail(msg, subject_prefix="通知", memo=None):
    """发送邮件通知"""
    if memo:
        msg += f"\n备注: {memo}"

    try:
        with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as s:
            s.starttls()
            s.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])

            message = MIMEText(msg, "plain", "utf-8")
            message["From"] = f"L<{SMTP_CONFIG['username']}>"
            message["Subject"] = subject_prefix

            for dest in EMAIL_RECIPIENTS:
                s.sendmail(SMTP_CONFIG["username"], dest, message.as_string())
    except Exception as e:
        print(f"邮件发送失败: {e}")


# ---------------------------- 新增：关键字搜索监控函数 ----------------------------
def check_keyword_search(keyword):
    """
    搜索关键字，如果有结果则发送邮件通知
    返回: (has_result, result_count, html_content)
    """
    try:
        # 构建搜索URL - keyword需要按Shift-JIS编码
        encoded_keyword = keyword.encode("shift_jis")
        # 使用 urllib.parse.quote 进行百分号编码
        encoded_keyword_quoted = urllib.parse.quote(encoded_keyword, safe="")
        search_url = f"{SEARCH_BASE_URL}?_e_k=%82%60&keyword={encoded_keyword_quoted}"

        print(f"[搜索] 关键字: {keyword} -> {search_url}")

        response = requests.get(search_url, timeout=10)
        response.raise_for_status()

        # 解码页面内容（使用shift_jis）
        page_content = response.content.decode("shift_jis", errors="ignore")

        # 检查是否有商品结果
        # 根据需求：有 <div class="error_content">検索条件に該当する商品はありません。</div> 表示无结果
        if 'class="error_content"' in page_content and "検索条件に該当する商品はありません。" in page_content:
            print(f"[搜索] 关键字 '{keyword}' 无结果")
            return False, 0, None

        # 有结果！尝试解析商品数量
        result_count = 0
        # 方法1：从页面提取 "xx件" 信息
        import re

        match = re.search(r"(\d+)\s*件", page_content)
        if match:
            result_count = int(match.group(1))
        else:
            # 方法2：统计商品列表中的元素数量
            soup = BeautifulSoup(page_content, "html.parser")
            # 根据网站结构，商品可能在 ul.list 或 div.item 中
            items = soup.select("ul.list li, div.item, div.product")
            if items:
                result_count = len(items)
            else:
                result_count = 1  # 至少有结果，但无法统计具体数量

        print(f"[搜索] 关键字 '{keyword}' 有结果! 找到 {result_count} 件商品")
        return True, result_count, search_url

    except Exception as e:
        print(f"[搜索错误] 关键字 '{keyword}': {e}")
        return False, 0, None


def run_keyword_search_checks():
    """执行所有关键字搜索检查"""
    load_config_data()  # 确保读取最新配置

    if not KEYWORD_WATCH_LIST:
        print("[搜索] 无关键字监控列表")
        return

    print(f"[搜索检查] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前监控关键字数: {len(KEYWORD_WATCH_LIST)}")

    found_keywords = []

    for keyword in KEYWORD_WATCH_LIST:
        has_result, count, search_url = check_keyword_search(keyword)

        if has_result:
            found_keywords.append((keyword, count, search_url))

    # 如果有搜索结果，汇总发送一封邮件
    if found_keywords:
        subject = f"🔔 搜索到 {len(found_keywords)} 个关键字有结果"
        msg = f"搜索时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for keyword, count, url in found_keywords:
            msg += f"【{keyword}】 找到 {count} 件商品\n"
            msg += f"  链接: {url}\n\n"

        msg += "\n---\n请点击链接查看详情"

        send_mail(msg, subject_prefix="商品搜索提醒")
        print(f"[搜索] 已发送提醒邮件，共 {len(found_keywords)} 个关键字有结果")


# ---------------------------- 健康检查函数 ----------------------------
def health_check():
    """每30分钟执行一次，发送健康状态通知"""
    load_config_data()

    msg = (
        f"监控程序运行正常 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"检查间隔: {CHECK_INTERVAL_SECONDS}秒\n"
        f"TokyoKawaiiLife监控数量: {len(TOKYO_ITEMS)}\n"
        f"URL有效性监控数量: {len(URL_WATCH_LIST)}\n"
        f"关键字监控数量: {len(KEYWORD_WATCH_LIST)}"
    )
    send_mail(msg, subject_prefix="健康状态通知")
    print(f"[健康检查] {time.strftime('%Y-%m-%d %H:%M:%S')} - 已发送健康通知")


# ---------------------------- 商品监控函数 ----------------------------
def check_tokyo_item(url, keyword, memo):
    """检查TokyoKawaiiLife商品是否有货"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        page_content = response.content.decode("shift_jis")
        if keyword in page_content:
            send_mail(f"tokyokawaiilife有货,{url}", subject_prefix=f"有货提醒: {memo}", memo=memo)
            print(f"[有货] Tokyo: {url} | 备注: {memo}")
    except Exception as e:
        print(f"[错误] Tokyo {url}: {e}")


def check_url_validity(url, memo):
    """检查URL是否可访问"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            send_mail(f"{url} 已经可以访问", subject_prefix="URL有效提醒", memo=memo)
            print(f"[URL有效] {url} | 备注: {memo}")
    except Exception as e:
        print(f"[错误] URL检查 {url}: {e}")


# ---------------------------- 主检查函数（每5秒执行） ----------------------------
def run_all_checks():
    """执行所有商品检查"""
    load_config_data()

    print(f"\n[检查开始] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前监控 Tokyo 物品数: {len(TOKYO_ITEMS)}")
    print(f"当前监控 URL 数: {len(URL_WATCH_LIST)}")
    print(f"当前监控 关键字数: {len(KEYWORD_WATCH_LIST)}")

    # 检查TokyoKawaiiLife商品
    for url, keyword, memo in TOKYO_ITEMS:
        check_tokyo_item(url, keyword, memo)

    # 检查URL有效性
    for url, memo in URL_WATCH_LIST:
        check_url_validity(url, memo)

    # 新增：关键字搜索检查
    run_keyword_search_checks()

    print(f"[检查完成] {time.strftime('%Y-%m-%d %H:%M:%S')}")


# ---------------------------- 调度器 ----------------------------
def run_scheduler():
    """运行定时任务调度器"""
    load_config_data()

    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(run_all_checks)
    schedule.every(HEALTH_CHECK_MINUTES).minutes.do(health_check)

    print(f"监控程序已启动 (动态加载模式)")
    print(f"商品检查间隔: {CHECK_INTERVAL_SECONDS}秒")
    print(f"健康检查间隔: {HEALTH_CHECK_MINUTES}分钟")
    print(f"关键字监控数量: {len(KEYWORD_WATCH_LIST)}")
    print("-" * 50)

    health_check()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run_scheduler()
