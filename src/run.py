# coding: utf-8
from flask import Flask, abort, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
<<<<<<< HEAD
from flask_marshmallow import Marshmallow
from sqlalchemy import func
import os

POSTGRES_URL = os.environ["POSTGRES_URL"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
=======
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import ssl
import os
import requests
from datetime import datetime
import json
import firebase_admin
from firebase_admin import credentials, auth
import sys
sys.path.append('/app/site/src')
import utils 

app = Flask(__name__)
CORS(app)
api = Api(app)

GOOGLE_ACCOUNT = os.environ['GOOGLE_ACCOUNT']
GOOGLE_ACCOUNT_PASS = os.environ['GOOGLE_ACCOUNT_PASS']

POSTGRES_URL = os.environ['POSTGRES_URL']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_DB = os.environ['POSTGRES_DB']
>>>>>>> develop

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=POSTGRES_USER,
    pw=POSTGRES_PASSWORD,
    url=POSTGRES_URL,
    db=POSTGRES_DB
<<<<<<< HEAD
    )

app = Flask(__name__)
CORS(app)
=======
)

>>>>>>> develop
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)
<<<<<<< HEAD
Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)

# テストデータ
users = [
    { "id": "U001", "name": "ユーザ太郎", "age": 27 },
    { "id": "U002", "name": "ユーザ二郎", "age": 20 },
    { "id": "U003", "name": "ユーザ三郎", "age": 10 }
]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), unique=False, nullable=True)

    def __init__(self, id, name):
        self.id = id
        self.token = name

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'token')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class UserInfo(Resource):
    def get(self):
        """
        ユーザを１件取得する
        """
        # id = request.args.get('id')
        # result = [n for n in users if n["id"] == id]

        user = User(1, 'wataru')

        db.session.add(user)

        db.session.commit()
        user = User.query.filter_by(id = 1).first()

        return jsonify(user_schema.dump(user).data)
        # return users[0]

        # if len(result) >= 1: 
        #     # ユーザ情報を返却
        #     return result[0]
        # else:
        #     # 存在しないユーザIDが指定された
        #     abort(404)

    def post(self):
        """
        ユーザを登録する
        """
        #ユーザを追加
        users.append(request.json)

        #正常に登録できたので、HTTP status=204(NO CONTENT)を返す
        return '', 204

    def put(self):
        """
        ユーザを更新する
        """
        user = request.json
        lst = [val for val in users if val["id"] == user["id"]]
        
        if len(lst) >= 1: 
            lst[0]["name"] = user["name"]
            lst[0]["age"] = user["age"]
        else:
            #存在しないユーザIDが指定された場合
            abort(404)

        #正常に更新できたので、HTTP status=204(NO CONTENT)を返す
        return '', 204

    def delete(self):
        """
        ユーザを削除する
        """
        id = request.args.get('id')
        lst = [i for i, val in enumerate(users) if val["id"] == id]
        for index in lst:
            del users[index]

        if len(lst) >= 1: 
            #ユーザの削除を行った場合、HTTP status=204(NO CONTENT)を返す
            return '', 204
        else:
            #存在しないユーザIDが指定された場合
            abort(404)

api.add_resource(UserInfo, '/user')

if __name__ == "__main__":
    app.run(debug=True)
=======

import models
Migrate(app, db)

if (not len(firebase_admin._apps)):
    cred = credentials.Certificate('/app/site/src/firebase-service.json')
    firebase_admin.initialize_app(cred)

class Contact(Resource):
    res = {'result': 'false'}
    def post(self):
        header = request.headers.get('Authorization')
        if header == None:
            abort(404)

        _, id_token = header.split()
        decoded_token = {}
        try:
            # ヘッダのトークンがfirebaseに登録されているかチェック
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            print(e)
            return jsonify(res)

        request_json = request.json

        # 管理者へメール送信
        utils.send_mail(request_json)

        account = ''
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')

        if email == None:
            # firebaseにてgoogle認証がされていない場合、匿名認証
            account = 'annonymaous'
        else:
            account = decoded_token.get('email')

        contact = models.Contacts(
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

        # db登録
        if not models.Contacts.insert(contact):
            return jsonify(res)

        res = {'result': 'true'}
        return jsonify(res)

api.add_resource(Contact, '/contact')
print('flask apiサーバ起動')

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> develop
