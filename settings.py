class Config:
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/myblog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "aerffghdsdfghh"


class DevelopmentConfig(Config):
    ENV = 'development'


class ProductConfig(Config):
    ENV = 'production'
    DEBUG = False
