from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
# from flask_sqlalchemy import SQLAlchemy
from app import create_app
# from my_blog.app.articles.view import article_bp
# from my_blog.app.user.view import user_bp
from ext import db

app = create_app()
# 设置数据库的配置信息(数据库地址，自动跟踪修改设置为False)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/myblog'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.register_blueprint(user_bp)
# app.register_blueprint(article_bp)

# 创建SQLAlchemy对象，关联app
# db = SQLAlchemy(app)
# 通过Manager类创建对象manager，管理app
manager = Manager(app)
# 使用Migrate关联app和db
migrate = Migrate(app, db)
# 给manager添加一条操作命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.run()
