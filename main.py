import time
import schedule
import requests
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from lxml import html
from lxml.cssselect import CSSSelector

# ---------------------------- 配置 ----------------------------
CHECK_INTERVAL_SECONDS = 5  # 商品检查间隔（秒）
HEALTH_CHECK_MINUTES = 30  # 健康检查间隔（分钟）

# 邮件接收人列表
EMAIL_RECIPIENTS = ["yinmingcan1999@gmail.com", "charismafight@hotmail.com", "604670240@qq.com", "1401437683@qq.com"]

# 发件人配置
SMTP_CONFIG = {"server": "smtp.exmail.qq.com", "port": 25, "username": "ll@champath.cn", "password": "76fUP3YVFak7VTnJ"}

# Angelic Pretty 代理配置（国内需要代理）
PROXIES = {
    "http": "http://127.0.0.1:10808",
    "https": "http://127.0.0.1:10808",
}

# ---------------------------- 商品监控列表 ----------------------------
# TokyoKawaiiLife 商品列表 (url, keyword)
TOKYO_ITEMS = [
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/451-3613-0", "varno_3_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/all-dresses/161-6205-0", "varno_1_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/161-1003-0", "varno_2_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/all-bottoms/163-5102-0", "varno_2_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/all-dresses/161-6214-0", "varno_3_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-5102-0", "varno_2_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/161-1006-0", "varno_1_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/161-1006-0", "varno_3_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/162-6019-0", "varno_3_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-5104-0", "varno_1_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-5104-0", "varno_2_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-5104-0", "varno_3_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/162-1009-0", "varno_3_1"),
]

# Angelic Pretty 商品列表 (url, keyword_of_id)
ANGELIC_ITEMS = [
    # ('https://angelicpretty.com/Form/Product/ProductDetail.aspx?shop=0&pid=252POT12-170030&cat=ITENEW','ct101'),
]

# URL有效性监控列表
URL_WATCH_LIST = [
    "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-6324-0",
    "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/162-1009-0",
    "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/161-1003-0",
]


# ---------------------------- 邮件发送函数 ----------------------------
def send_mail(msg, url=None):
    """发送邮件通知"""
    subject = f"来自{url}" if url else "健康状态通知"
    try:
        with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as s:
            s.starttls()
            s.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
            message = MIMEText(msg, "plain", "utf-8")
            message["From"] = Header(f"L<{SMTP_CONFIG['username']}>")
            message["Subject"] = Header(subject, "utf-8")
            for dest in EMAIL_RECIPIENTS:
                s.sendmail(SMTP_CONFIG["username"], dest, message.as_string())
    except Exception as e:
        print(f"邮件发送失败: {e}")


# ---------------------------- 健康检查函数 ----------------------------
def health_check():
    """每30分钟执行一次，发送健康状态通知"""
    msg = (
        f"监控程序运行正常 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"检查间隔: {CHECK_INTERVAL_SECONDS}秒\n"
        f"TokyoKawaiiLife监控数量: {len(TOKYO_ITEMS)}\n"
        f"AngelicPretty监控数量: {len(ANGELIC_ITEMS)}\n"
        f"URL有效性监控数量: {len(URL_WATCH_LIST)}"
    )
    send_mail(msg)
    print(f"[健康检查] {time.strftime('%Y-%m-%d %H:%M:%S')} - 已发送健康通知")


# ---------------------------- 商品监控函数 ----------------------------
def check_tokyo_item(url, keyword):
    """检查TokyoKawaiiLife商品是否有货"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        page_content = response.content.decode("shift_jis")
        if keyword in page_content:
            send_mail(f"tokyokawaiilife有货,{url}", url)
            print(f"[有货] Tokyo: {url}")
    except Exception as e:
        print(f"[错误] Tokyo {url}: {e}")


def check_angelic_item(url, keyword_of_id):
    """检查AngelicPretty商品是否有货"""
    try:
        response = requests.get(url, proxies=PROXIES)
        response.raise_for_status()
        page_content = response.content.decode("utf-8")
        tree = html.fromstring(page_content)
        selector = CSSSelector(f'a[id*="{keyword_of_id}"].productAddCartBtn.withbagIcon111')
        elements = selector(tree)
        if len(elements) > 0:
            send_mail(f"angelicpretty有货,{url}", url)
            print(f"[有货] Angelic: {url}")
    except Exception as e:
        print(f"[错误] Angelic {url}: {e}")


def check_url_validity(url):
    """检查URL是否可访问"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            send_mail(f"{url} 已经可以访问", url)
            print(f"[URL有效] {url}")
    except Exception as e:
        print(f"[错误] URL检查 {url}: {e}")


# ---------------------------- 主检查函数（每5秒执行） ----------------------------
def run_all_checks():
    """执行所有商品检查"""
    print(f"\n[检查开始] {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查TokyoKawaiiLife商品
    for url, keyword in TOKYO_ITEMS:
        check_tokyo_item(url, keyword)

    # 检查AngelicPretty商品
    for url, keyword in ANGELIC_ITEMS:
        check_angelic_item(url, keyword)

    # 检查URL有效性
    for url in URL_WATCH_LIST:
        check_url_validity(url)

    print(f"[检查完成] {time.strftime('%Y-%m-%d %H:%M:%S')}")


# ---------------------------- 调度器 ----------------------------
def run_scheduler():
    """运行定时任务调度器"""
    # 每5秒执行商品检查
    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(run_all_checks)

    # 每30分钟执行健康检查
    schedule.every(HEALTH_CHECK_MINUTES).minutes.do(health_check)

    print(f"监控程序已启动")
    print(f"商品检查间隔: {CHECK_INTERVAL_SECONDS}秒")
    print(f"健康检查间隔: {HEALTH_CHECK_MINUTES}分钟")
    print(f"TokyoKawaiiLife监控: {len(TOKYO_ITEMS)}个")
    print(f"AngelicPretty监控: {len(ANGELIC_ITEMS)}个")
    print(f"URL有效性监控: {len(URL_WATCH_LIST)}个")
    print("-" * 50)

    # 立即执行一次健康检查（标记启动）
    health_check()

    # 循环执行调度任务
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run_scheduler()
