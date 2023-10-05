import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 是否开启SQL语句打印
    SQL_ECHO: bool = os.getenv('SQL_ECHO').lower() == 'true'
    # JWT配置
    TOKEN_SECRET = os.getenv('TOKEN_SECRET')
    # JWT算法
    ALGORITHM = 'HS256'
    # JWT用户key
    DECODED_TOKEN_USER_KEY = "sub"
    # JWT签发时间key
    DECODED_TOKEN_IAT_KEY = "iat"
    # JWT过期时间
    TOKEN_EXPIRE_TIME = int(os.getenv("TOKEN_EXPIRE_TIME"))
    # 数据库连接信息，需要判断不能为空
    SQLALCHEMY_DATABASE_URL: str = os.getenv('DATABASE_URL')
    # API前缀
    API_PREFIX = os.getenv('API_PREFIX', '/api')
    # 微信基础服务地址
    WE_CHAT_SERVER_URL = os.getenv('WE_CHAT_SERVER_URL')
    # WeChat AppID
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
    # WeChat AppSecret
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')