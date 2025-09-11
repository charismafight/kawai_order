import requests
import smtplib
from email.header import Header
from email.mime.text import MIMEText


def sendMail(msg):
    # list of email_id to send the mail
    li = ["yinmingcan1999@gmail.com", "charismafight@hotmail.com"]

    for dest in li:
        s = smtplib.SMTP('smtp.exmail.qq.com', 25)
        s.starttls()
        s.login("ll@champath.cn", "76fUP3YVFak7VTnJ")
        message = MIMEText(msg, 'plain', 'utf-8')
        message['From'] = Header('L<ll@champath.cn>')
        message['Subject'] = Header(
            '来自https://www.tokyokawaiilife.jp/fs/lizlisaadmin/351-6238-0的监控提醒', 'utf-8')
        s.sendmail("ll@champath.cn", dest, message.as_string())


itemUrl = 'https://www.tokyokawaiilife.jp/fs/lizlisaadmin/351-6238-0'
response = requests.get(itemUrl)
response.raise_for_status()
page_content = response.content.decode('shift_jis')

if 'ブラック(104)/SOLD OUT' in page_content:
    print("卖完")
else:
    print("有货")
    sendMail('有货')
