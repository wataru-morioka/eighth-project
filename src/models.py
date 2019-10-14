from run import app, db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from sqlalchemy import (Column, String, Text, ForeignKey, \
                        create_engine, MetaData, DECIMAL, DATETIME, exc, event, Index, func, desc)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import (sessionmaker, relationship, scoped_session)
import os
import traceback

ma = Marshmallow(app)
    
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
    
    def insert(self):
        db.session.add(self)
        try:
            db.session.commit()
            return True
        except Exception:
            print(traceback.format_exc())
            return False

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