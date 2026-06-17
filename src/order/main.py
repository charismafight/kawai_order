import time
import schedule
import requests
import smtplib
import importlib
import sys
from email.mime.text import MIMEText

# ---------------------------- 配置 ----------------------------
CHECK_INTERVAL_SECONDS = 5  # 商品检查间隔（秒）
HEALTH_CHECK_MINUTES = 30  # 健康检查间隔（分钟）

# 邮件接收人列表
EMAIL_RECIPIENTS = ["yinmingcan1999@gmail.com", "charismafight@hotmail.com", "604670240@qq.com", "1401437683@qq.com"]

# 发件人配置
SMTP_CONFIG = {"server": "smtp.exmail.qq.com", "port": 25, "username": "ll@champath.cn", "password": "76fUP3YVFak7VTnJ"}


# ---------------------------- 动态加载函数 ----------------------------
def load_config_data():
    """
    动态加载配置文件，每次调用都会重新读取文件内容
    """
    global TOKYO_ITEMS, URL_WATCH_LIST

    # 1. Load Tokyo Items
    try:
        # If module already exists, reload it. If not, import it.
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


# Initialize global variables
TOKYO_ITEMS = []
URL_WATCH_LIST = []


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


# ---------------------------- 健康检查函数 ----------------------------
def health_check():
    """每30分钟执行一次，发送健康状态通知"""
    # Reload config before health check to ensure counts are current
    load_config_data()

    msg = (
        f"监控程序运行正常 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"检查间隔: {CHECK_INTERVAL_SECONDS}秒\n"
        f"TokyoKawaiiLife监控数量: {len(TOKYO_ITEMS)}\n"
        f"URL有效性监控数量: {len(URL_WATCH_LIST)}"
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
    # *** RELOAD CONFIGURATION EVERY LOOP ***
    load_config_data()

    print(f"\n[检查开始] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前监控 Tokyo 物品数: {len(TOKYO_ITEMS)}")
    print(f"当前监控 URL 数: {len(URL_WATCH_LIST)}")

    # 检查TokyoKawaiiLife商品
    for url, keyword, memo in TOKYO_ITEMS:
        check_tokyo_item(url, keyword, memo)

    # 检查URL有效性
    for url, memo in URL_WATCH_LIST:
        check_url_validity(url, memo)

    print(f"[检查完成] {time.strftime('%Y-%m-%d %H:%M:%S')}")


# ---------------------------- 调度器 ----------------------------
def run_scheduler():
    """运行定时任务调度器"""
    # Initial load
    load_config_data()

    # 每5秒执行商品检查
    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(run_all_checks)

    # 每30分钟执行健康检查
    schedule.every(HEALTH_CHECK_MINUTES).minutes.do(health_check)

    print(f"监控程序已启动 (动态加载模式)")
    print(f"商品检查间隔: {CHECK_INTERVAL_SECONDS}秒")
    print(f"健康检查间隔: {HEALTH_CHECK_MINUTES}分钟")
    print("-" * 50)

    # 立即执行一次健康检查（标记启动）
    health_check()

    # 循环执行调度任务
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run_scheduler()
