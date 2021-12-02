from datetime import datetime

from ext import db


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    # 性别用布尔类型，1表示男性，0表示女性
    gender = db.Column(db.Boolean, nullable=False)
    # 多对多关系
    comments = db.relationship('Comment', backref='user')
    saves = db.relationship('Save', backref='user')


class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=True)
    time = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', backref='messages')

