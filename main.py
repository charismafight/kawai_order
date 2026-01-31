import requests
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from lxml import html
from lxml.cssselect import CSSSelector


def sendMail(msg, url):
    # list of email_id to send the mail
    li = ["yinmingcan1999@gmail.com", "charismafight@hotmail.com"]

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
        sendMail("tokyokawaiilife有货", url)


# -------------------------------------------------------------------------------------- tokyokawaiilife

urlTuple = [
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/all-tops/351-1018-0", "varno_2_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/451-3613-0", "varno_3_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-5104-0", "varno_3_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/161-6202-0", "varno_1_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/all-dresses/161-6205-0", "varno_1_1"),
    ("https://www.tokyokawaiilife.jp/fs/lizlisaadmin/161-1003-0", "varno_2_1"),
]

for t in urlTuple:
    print(t[0])
    queryStock(t[0], t[1])


# -------------------------------------------------------------------------------------- angelicpretty
# 规则，url是商品页面链接，后面的值是第几个商品，ctl01,ctl02,ctl03以此类推，注意是CTL的小写，不是CT1
# 删除下面的 #并修改对应的配置来启用
urlNewTuple = [
    # ('https://angelicpretty.com/Form/Product/ProductDetail.aspx?shop=0&pid=252POT12-170030&cat=ITENEW','ct101'),
]

# 国内需要代理
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
        sendMail("angelicpretty有货", url)


for t in urlNewTuple:
    print(t[0])
    queryStock(t[0], t[1])
