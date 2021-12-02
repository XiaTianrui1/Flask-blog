import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from werkzeug.routing import BaseConverter

import settings
from app.articles.view import article_bp
from app.user.view import user_bp
from ext import db


def create_app():
    # 调用日志方法，记录程序运行信息
    log_file()
    # 创建app对象
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    # 加载配置
    app.config.from_object(settings.DevelopmentConfig)
    db.init_app(app)
    # 注册蓝图,绑定蓝图对象
    app.register_blueprint(user_bp)
    app.register_blueprint(article_bp)
    # app.url_map.converters['re'] = RegexConverter
    return app


def log_file():
    # 设置日志等级
    logging.basicConfig(level=logging.DEBUG)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler('log.txt', maxBytes=1024 * 1024 * 300, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(asctime)s: %(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flaskapp使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

# class RegexConverter(BaseConverter):
#     """"""
#
#     def __init__(self, url_map, regex):
#         # 调用父类的初始化方法(python2中super()必须写参数)
#         super(RegexConverter, self).__init__(url_map)
#         # 将正则表达式的参数保存到对象属性中，flask会去使用这个属性来进行路由的正则匹配
#         self.regex = regex
