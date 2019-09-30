# coding: utf-8
from flask import Flask, abort, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
# from sqlalchemy import func
from sqlalchemy import (Column, String, Text, ForeignKey, \
                create_engine, MetaData, DECIMAL, DATETIME, exc, event, Index, func, desc)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import (sessionmaker, relationship, scoped_session)
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import ssl
import os
import requests
import json
from datetime import datetime
import logging
from logging import getLogger 
import firebase_admin
from firebase_admin import credentials, auth
import base64
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

cred = credentials.Certificate('/app/site/src/firebase-service.json')
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
    uid = db.Column(db.String(128), unique=False, nullable=False)
    name = db.Column(db.String(64), unique=False, nullable=False)
    organization = db.Column(db.String(16), unique=False, nullable=False)
    state = db.Column(db.String(16), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=False, nullable=False)
    phone = db.Column(db.String(16), unique=False, nullable=True)
    message = db.Column(db.String(5000), unique=False, nullable=False)
    created_datetime = db.Column(db.DateTime, index=True, unique=False, nullable=False)

    def __init__(self, account, uid,  name, organization, state, email, phone, message, created_datetime):
        self.account = account
        self.uid = uid
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

class Photographs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub_title = db.Column(db.String(64), unique=False, nullable=True)
    title = db.Column(db.String(64), unique=False, nullable=True)
    mimetype = db.Column(db.String(64), unique=False, nullable=False)
    file_name = db.Column(db.String(64), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=False)
    data = db.Column(db.Binary, unique=False, nullable=False)
    created_datetime = db.Column(db.DateTime, unique=False, nullable=False)
    modified_datetime = db.Column(db.DateTime, unique=False, nullable=False)

class PhotographsSchema(ma.Schema):
    class Meta:
        model = Photographs
        fields = ('id', 'sub_title', 'title', 'mimetype', 'file_name', 'size', 'data', 'created_datetime', 'modified_datetime')

photo_schema = PhotographsSchema()
photos_schema = PhotographsSchema(many=True)

class Videos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photograph_id = db.Column(db.Integer, ForeignKey('photographs.id', ondelete='CASCADE'), index=True, unique=True, nullable=False)
    mimetype = db.Column(db.String(64), unique=False, nullable=False)
    file_name = db.Column(db.String(64), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=False)
    data = db.Column(db.Binary, unique=False, nullable=False)
    created_datetime = db.Column(db.DateTime, unique=False, nullable=False)
    modified_datetime = db.Column(db.DateTime, unique=False, nullable=False)

    photographs = relationship('Photographs', backref='photographs')

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
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        if email == None:
            account = 'annonymaous'
        else:
            account = decoded_token.get('email')

        message = 'name: ' + request_json.get('name')
        message += '\n' + 'organization: ' + request_json.get('organization')
        message += '\n' + 'state: ' + request_json.get('state')
        message += '\n' + 'email: ' + request_json.get('email')
        message += '\n' + 'phone: ' + request_json.get('phone')
        message += '\n' + 'message: ' + '\n' +  request_json.get('message')

        #メール送信
        msg = MIMEText(message)
        msg['Subject'] = '【seventh-project】Contact'
        msg['From'] = 'seventh-project'
        msg['To'] = GOOGLE_ACCOUNT
        msg['Date'] = formatdate()
        smtpobj = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        smtpobj.login(GOOGLE_ACCOUNT, GOOGLE_ACCOUNT_PASS)
        smtpobj.sendmail('seventh-project', GOOGLE_ACCOUNT, msg.as_string())
        smtpobj.close()

        #db登録
        contact = Contacts(
            account,
            uid,
            request_json.get('name'),
            request_json.get('organization'),
            request_json.get('state'),
            request_json.get('email'),
            request_json.get('phone'),
            request_json.get('message'),
            datetime.now()
            # datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

class Photograph(Resource):
    def get(self):
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

        # TODO adminチェック
        print('test')

        photos = Photographs.query.order_by(desc(Photographs.created_datetime)).all()

        print(photos_schema.dump(photos).data)

        return jsonify(photos_schema.dump(photos).data)

api.add_resource(UserInfo, '/user')
api.add_resource(Contact, '/contact')
api.add_resource(Photograph, '/photographs')

if __name__ == '__main__':
    app.run(debug=True)
