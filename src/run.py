# coding: utf-8
from flask import Flask, abort, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import ssl
import os
import requests
from datetime import datetime
import json
import traceback
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

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=POSTGRES_USER,
    pw=POSTGRES_PASSWORD,
    url=POSTGRES_URL,
    db=POSTGRES_DB
)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

import models
Migrate(app, db)

# firebase authentication（匿名認証）サービスを使用
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
        except Exception:
            print(traceback.format_exc())
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
