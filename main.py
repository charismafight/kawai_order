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


def queryStock(url, keyword):
    response = requests.get(url)
    response.raise_for_status()
    page_content = response.content.decode("shift_jis")
    if keyword in page_content:
        sendMail(f"tokyokawaiilife有货,{url}", url)


# -------------------------------------------------------------------------------------- tokyokawaiilife

urlTuple = [
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

print("start tokyokawaiilife items query")
for t in urlTuple:
    print(t[0])
    try:
        queryStock(t[0], t[1])
    except Exception as e:
        print(e)


# -------------------------------------------------------------------------------------- angelicpretty
# 规则，url是商品页面链接，后面的值是第几个商品，ctl01,ctl02,ctl03以此类推，注意是CTL的小写，不是CT1
# 删除下面的 #并修改对应的配置来启用
urlNewTuple = [
    # ('https://angelicpretty.com/Form/Product/ProductDetail.aspx?shop=0&pid=252POT12-170030&cat=ITENEW','ct101'),
]

# 国内需要代理
# 注意13服务器上需要改为10809才能正常走代理
proxies = {
    "http": "http://127.0.0.1:10808",  # HTTP代理
    "https": "http://127.0.0.1:10808",  # HTTPS代理
}


def queryAngelic(url, keywordOfId):
    response = requests.get(url, proxies=proxies)
    response.raise_for_status()
    page_content = response.content.decode("utf-8")
    tree = html.fromstring(page_content)
    selector = CSSSelector(f'a[id*="{keywordOfId}"].productAddCartBtn.withbagIcon111')
    elements = selector(tree)
    if len(elements > 0):
        sendMail(f"angelicpretty有货,{url}", url)


print("start angelicpretty query")

for t in urlNewTuple:
    print(t[0])
    try:
        queryAngelic(t[0], t[1])
    except Exception as e:
        print(e)


# 增加需求：监听一个集合的url，如果url是有效的则发邮件


def write_lines_to_file(lines):
    with open("urls.txt", "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def read_file_to_list():
    lines_list = []
    # 检查文件是否存在
    if not os.path.exists("urls.txt"):
        return lines_list  # 返回空列表

    with open("urls.txt", "r", encoding="utf-8") as f:
        for line in f:
            lines_list.append(line.rstrip("\n"))
    return lines_list


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
