import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 数据库连接信息
    SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
    # JWT密钥
    SECRET_KEY = os.getenv('SECRET_KEY')
    # API前缀
    API_PREFIX = os.getenv('API_PREFIX', '/api')
    # 微信APP_ID
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
    # 微信APP_SECRET
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')
    # 微信API地址
    WECHAT_API_URL = os.getenv('WECHAT_API_URL')
    # 微信授权地址
    WECHAT_AUTH_URL = os.getenv('WECHAT_AUTH_URL')
    # 微信服务器验证token
    WECHAT_CHECK_SIGNATURE_TOKEN = os.getenv('WECHAT_CHECK_SIGNATURE_TOKEN')
    # 微信回调地址
    SCIO_REDIRECT_URI = os.getenv('SCIO_REDIRECT_URI')
