import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import ssl
import os

GOOGLE_ACCOUNT = os.environ['GOOGLE_ACCOUNT']
GOOGLE_ACCOUNT_PASS = os.environ['GOOGLE_ACCOUNT_PASS']

# 管理者へメール送信（googleメールサーバを利用）
def send_mail(request_json):
    message = 'name: ' + request_json.get('name')
    message += '\n' + 'organization: ' + request_json.get('organization')
    message += '\n' + 'state: ' + request_json.get('state')
    message += '\n' + 'email: ' + request_json.get('email')
    message += '\n' + 'phone: ' + request_json.get('phone')
    message += '\n' + 'message: ' + '\n' +  request_json.get('message')

    msg = MIMEText(message)
    msg['Subject'] = '【seventh-project】Contact'
    msg['From'] = 'seventh-project'
    msg['To'] = GOOGLE_ACCOUNT
    msg['Date'] = formatdate()
    smtpobj = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
    smtpobj.login(GOOGLE_ACCOUNT, GOOGLE_ACCOUNT_PASS)
    smtpobj.sendmail('seventh-project', GOOGLE_ACCOUNT, msg.as_string())
    smtpobj.close()