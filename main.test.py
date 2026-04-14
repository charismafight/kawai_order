import os

import requests
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from lxml import html
from lxml.cssselect import CSSSelector


def sendMail(msg, url):
    # list of email_id to send the mail
    li = ["yinmingcan1999@gmail.com", "charismafight@hotmail.com", "604670240@qq.com", "1401437683@qq.com"]

    for dest in li:
        s = smtplib.SMTP("smtp.exmail.qq.com", 25)
        s.starttls()
        s.login("ll@champath.cn", "76fUP3YVFak7VTnJ")
        message = MIMEText(msg, "plain", "utf-8")
        message["From"] = Header("L<ll@champath.cn>")
        message["Subject"] = Header(f"来自{url}", "utf-8")
        s.sendmail("ll@champath.cn", dest, message.as_string())


# 国内需要代理
proxies = {
    "http": "http://127.0.0.1:10808",  # HTTP代理
    "https": "http://127.0.0.1:10808",  # HTTPS代理
}

# -------------------------------------------------------------------------------------
# 规则，url是商品页面链接，当url可以被访问的时候会发送一次邮件
# 删除下面的 #并修改对应的配置来启用
urlList = [
    "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-6324-0",
    "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/162-1009-0",
]


def queryUrl(url):
    response = requests.get(url, proxies=proxies)
    if response.status_code == 200:
        sendMail(f"{url} 已经可以访问", url)


print("start kawaii url query")
for url in urlList:
    print(f"testing {url}")
    try:
        queryUrl(url)
    except Exception as e:
        print(e)
