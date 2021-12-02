from datetime import datetime

from ext import db


class Article(db.Model):
    article_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.String(30), nullable=False)
    click = db.Column(db.Integer, default=1)
    like = db.Column(db.Integer, default=0)
    save = db.Column(db.Integer, default=0)
    # uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relation('Comment', backref='article')
    saves = db.relation('Save', backref='article')


# 评论类
class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.String(500), nullable=False)
    comment_time = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.article_id'))


# 收藏夹类
class Save(db.Model):
    save_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.article_id'))
