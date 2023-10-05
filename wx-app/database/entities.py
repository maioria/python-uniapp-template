import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from database import Base, engine


# 定义Token模型
class Token(Base):
    """
    {
      "access_token":"ACCESS_TOKEN",
      "expires_in":7200,
      "refresh_token":"REFRESH_TOKEN",
      "openid":"OPENID",
      "scope":"SCOPE"
    }
    """
    __tablename__ = "wechat_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(String(512))
    expires_in = Column(Integer)
    refresh_token = Column(String(512))
    openid = Column(String(512))
    scope = Column(String(128))
    state = Column(String(256))
    status = Column('status', String(50), default='ACTIVE')
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    update_time = Column('update_time', DateTime, default=datetime.datetime.now)


class StateTokenRelation(Base):
    """
    state为参数，这个表只存储state与token表的主键的关联关系
    """
    __tablename__ = "wechat_state_token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(512))
    token_id = Column(Integer)
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)


# 微信返回的用户信息
class UserInfo(Base):
    """
    {
      "openid": "OPENID",
      "nickname": NICKNAME,
      "sex": 1,
      "language": "",
      "province":"PROVINCE",
      "city":"CITY",
      "country":"COUNTRY",
      "headimgurl":"https://thirdwx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/46",
      "privilege":[ "PRIVILEGE1" "PRIVILEGE2"     ]
    }
    """
    __tablename__ = "wechat_user_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(Integer)
    openid = Column(String(128))
    nickname = Column(String(128))
    sex = Column(Integer)
    province = Column(String(128))
    city = Column(String(128))
    country = Column(String(128))
    headimgurl = Column(String(512))
    privilege = Column(String(128))
    status = Column('status', String(50), default='ACTIVE')
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    update_time = Column('update_time', DateTime, default=datetime.datetime.now)


Base.metadata.create_all(engine)
