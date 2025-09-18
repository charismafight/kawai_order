import requests
import smtplib
from email.header import Header
from email.mime.text import MIMEText


def sendMail(msg, url):
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


def queryStock(url, keyword):
    response = requests.get(url)
    response.raise_for_status()
    page_content = response.content.decode('shift_jis')
    if keyword in page_content:
        sendMail('有货', url)


urlTuple = [
    ('https://www.tokyokawaiilife.jp/fs/lizlisaadmin/351-6238-0',
     'varno_1_1'),
    ('https://www.tokyokawaiilife.jp/fs/lizlisaadmin/all-bottoms/353-5117-0',
     'varno_3_1'),
    ('https://www.tokyokawaiilife.jp/fs/lizlisaadmin/all-tops/351-1018-0',
     'varno_2_1'),
]

for t in urlTuple:
    print(t[0])
    queryStock(t[0], t[1])
