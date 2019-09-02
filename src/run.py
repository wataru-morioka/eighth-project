# coding: utf-8
from flask import Flask, abort, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from sqlalchemy import func
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import base64
# from email.mime.text import MIMEText
# from apiclient import errors
# import base64
# import pickle
import ssl
import os
import requests
import json
from datetime import datetime
import logging
from logging import getLogger 
import firebase_admin
from firebase_admin import credentials, auth
logger = getLogger(__name__)

GOOGLE_ACCOUNT = os.environ['GOOGLE_ACCOUNT']
GOOGLE_ACCOUNT_PASS = os.environ['GOOGLE_ACCOUNT_PASS']

POSTGRES_URL = os.environ['POSTGRES_URL']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_DB = os.environ['POSTGRES_DB']

# MYSQL_URL = os.environ['MYSQL_URL']
# MYSQL_USER = os.environ['MYSQL_USER']
# MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
# MYSQL_DB = os.environ['MYSQL_DB']

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=POSTGRES_USER,
    pw=POSTGRES_PASSWORD,
    url=POSTGRES_URL,
    db=POSTGRES_DB
    )
# DB_URL = 'mysql+mysqldb://{user}:{pw}@{url}/{db}'.format(
#     user=MYSQL_USER,
#     pw=MYSQL_PASSWORD,
#     url=MYSQL_URL,
#     db=MYSQL_DB
#     )

SCOPES = "https://www.googleapis.com/auth/gmail.send"
CLIENT_SECRET_FILE = "credentials.json"
APPLICATION_NAME = "seventh-project"
MAIL_FROM = "wtrmorioka@gmail.com"
MAIL_TO = "wtrmorioka@gmail.com"

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)
Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)

cred = credentials.Certificate('firebase-service.json')
firebase_admin.initialize_app(cred)

# テストデータ
users = [
    { 'id': 'U001', 'name': 'ユーザ太郎', 'age': 27 },
    { 'id': 'U002', 'name': 'ユーザ二郎', 'age': 20 },
    { 'id': 'U003', 'name': 'ユーザ三郎', 'age': 10 }
]

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=True)

    def __init__(self, id, name):
        self.id = id
        self.name = name

class UsersSchema(ma.Schema):
    class Meta:
        model = Users
        fields = ('id', 'name')
        # table = Users.__table__

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)

class Photos(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    file_name = db.Column(db.String(100), unique=False, nullable=True)
    mimetype = db.Column(db.String(100), unique=False, nullable=True)
    size = db.Column(db.Integer, unique=False, nullable=True)
    data = db.Column(db.LargeBinary, unique=False, nullable=True)
    created_datetime = db.Column(db.DateTime, unique=False, nullable=True)
    modified_datetime = db.Column(db.DateTime, unique=False, nullable=True)

class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), unique=False, nullable=False)
    name = db.Column(db.String(64), unique=False, nullable=False)
    organization = db.Column(db.String(16), unique=False, nullable=False)
    state = db.Column(db.String(16), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=False, nullable=False)
    phone = db.Column(db.String(16), unique=False, nullable=True)
    message = db.Column(db.String(5000), unique=False, nullable=False)
    created_datetime = db.Column(db.DateTime, unique=False, nullable=False)

    def __init__(self, account, name, organization, state, email, phone, message, created_datetime):
        # self.id = id
        self.account = account
        self.name = name
        self.organization = organization
        self.state = state
        self.email = email
        self.phone = phone
        self.message = message
        self.created_datetime = created_datetime

class ContactsSchema(ma.Schema):
    class Meta:
        model = Contacts
        fields = ('id', 'account', 'name', 'organization', 'state', 'email', 'phone', 'message', 'created_datetime')

contact_schema = ContactsSchema()

class UserInfo(Resource):
    def get(self):
        # id = request.args.get('id')
        # result = [n for n in users if n['id'] == id]

        # user = User(1, 'wataru')

        # db.session.add(user)

        # db.session.commit()
        user = Users.query.filter_by(id = 1).first()

        return jsonify(user_schema.dump(user).data)
        # return users[0]

        # if len(result) >= 1: 
        #     # ユーザ情報を返却
        #     return result[0]
        # else:
        #     # 存在しないユーザIDが指定された
        #     abort(404)

    def post(self):
        #ユーザを追加
        resp = requests.post('https://www.googleapis.com/identitytoolkit/v3/'
                                      'relyingparty/getAccountInfo'
                                      '?key={}'.format('AIzaSyBb1EQB5F7Q7O9n8BH1Fy929XhH7tRy6OM'),
                                      params={'idToken': request.json['idToken']})
        logger.debug('userinfo:{}'.format(resp.text))
        print(resp.text)
        data = json.loads(resp.text)
        body = {
            'uid': data['users'][0]['localId'],
            'email': data['users'][0]['email'],
            'displayName': data['users'][0]['displayName'],
        }

        return jsonify(body)

    def put(self):
        user = request.json
        lst = [val for val in users if val['id'] == user['id']]
        
        if len(lst) >= 1: 
            lst[0]['name'] = user['name']
            lst[0]['age'] = user['age']
        else:
            #存在しないユーザIDが指定された場合
            abort(404)

        #正常に更新できたので、HTTP status=204(NO CONTENT)を返す
        return '', 204

    def delete(self):
        id = request.args.get('id')
        lst = [i for i, val in enumerate(users) if val['id'] == id]
        for index in lst:
            del users[index]

        if len(lst) >= 1: 
            #ユーザの削除を行った場合、HTTP status=204(NO CONTENT)を返す
            return '', 204
        else:
            #存在しないユーザIDが指定された場合
            abort(404)

class Contact(Resource):
    def post(self):
        header = request.headers.get('Authorization')
        if header == None:
            abort(404)

        _, id_token = header.split()
        decoded_token = {}
        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            print(e)
            res = {'result': 'false'}
            return jsonify(res)

        request_json = request.json
        account = ''
        email = decoded_token.get('email')
        if email == None:
            account = 'annonymaous'
        else:
            account = decoded_token['uid'] 

        #メール送信
        msg = MIMEText(request_json.get('message'))
        msg['Subject'] = 'seventh-projectにcontact'
        msg['From'] = 'seventh-project'
        msg['To'] = GOOGLE_ACCOUNT
        msg['Date'] = formatdate()
        smtpobj = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        smtpobj.login(GOOGLE_ACCOUNT, GOOGLE_ACCOUNT_PASS)
        smtpobj.sendmail('seventh-project', GOOGLE_ACCOUNT, msg.as_string())
        smtpobj.close()

        # creds = None
        # if os.path.exists('token.pickle'):
        #     with open('token.pickle', 'rb') as token:
        #         creds = pickle.load(token)
        # if not creds or not creds.valid:
        #     if creds and creds.expired and creds.refresh_token:
        #         creds.refresh(Request())
        #     else:
        #         flow = InstalledAppFlow.from_client_secrets_file(
        #             'credentials.json', SCOPES)
        #         creds = flow.run_local_server()
        #     with open('token.pickle', 'wb') as token:
        #         pickle.dump(creds, token)
        # service = build('gmail', 'v1', credentials=creds)
        # # 6. メール本文の作成
        # sender = 'wtrmorioka@gmail.com'
        # to = 'wtrmorioka@gmail.com'
        # subject = 'メール送信自動化テスト'
        # message_text = 'メール送信の自動化テストをしています。'
        # message = create_message(sender, to, subject, message_text)
        # # 7. Gmail APIを呼び出してメール送信
        # send_message(service, 'me', message)


        #db登録
        contact = Contacts(
            account,
            request_json.get('name'),
            request_json.get('organization'),
            request_json.get('state'),
            request_json.get('email'),
            request_json.get('phone'),
            request_json.get('message'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(contact)

        try:
            db.session.commit()
        except Exception as e:
            print(e)
            res = {'result': 'false'}
            return jsonify(res)

        res = {'result': 'true'}
        return jsonify(res)

api.add_resource(UserInfo, '/user')
api.add_resource(Contact, '/contact')

def setLogger():
    #handler1を作成
    handler1 = logging.StreamHandler()
    handler1.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s %(message)s'))

    #handler2を作成
    handler2 = logging.FileHandler(filename='test.log')  #handler2はファイル出力
    handler2.setLevel(logging.WARN)     #handler2はLevel.WARN以上
    handler2.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s %(message)s'))

    #loggerに2つのハンドラを設定
    logger.addHandler(handler1)
    logger.addHandler(handler2)

# def get_credentials():
#     script_dir =os.path.abspath(os.path.dirname(__file__)) 
#     credential_dir = os.path.join(script_dir, ".credentials")

#     if not os.path.exists(credential_dir):
#         os.makedirs(credential_dir)
#     credential_path = os.path.join(credential_dir, "my-gmail-sender.json")


#     store = oauth2client.file.Storage(credential_path)
#     print('test')

#     credentials = store.get()
#     if not credentials or credentials.invalid:
#         flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
#         flow.user_agent = APPLICATION_NAME
#         credentials = oauth2client.tools.run_flow(flow, store, flags)
#         print("Storing credentials to " + credential_path)
#     return credentials

# 2. メール本文の作成
# def create_message(sender, to, subject, message_text):
#     message = MIMEText(message_text)
#     message['to'] = to
#     message['from'] = sender
#     message['subject'] = subject
#     encode_message = base64.urlsafe_b64encode(message.as_bytes())
#     return {'raw': encode_message.decode()}
# # 3. メール送信の実行
# def send_message(service, user_id, message):
#     try:
#         message = (service.users().messages().send(userId=user_id, body=message)
#                    .execute())
#         print('Message Id: %s' % message['id'])
#         return message
#     except errors.HttpError as error:
#         print('An error occurred: %s' % error)


if __name__ == '__main__':
    setLogger()
    # get_credentials()
    app.run(debug=True)
