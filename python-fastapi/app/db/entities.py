import datetime

from sqlalchemy import Column, String, DateTime, Integer, Index, Text
from app.db import Base, engine


class AccountEntity(Base):
    """用户表"""

    __tablename__ = "account"

    id = Column("id", String(80), primary_key=True)
    nickname = Column("nickname", String(80), nullable=True)
    head_img = Column("head_img", String(250), nullable=True)
    wechat_open_id = Column("wechat_open_id", String(250), nullable=True)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class VisitorEntity(Base):
    """访客表"""

    __tablename__ = "visitor"

    id = Column("id", String(80), primary_key=True)
    client_host = Column("client_host", String(50), nullable=False)
    user_agent = Column("user_agent", String(512), nullable=True)
    fingerprint = Column("fingerprint", String(64), nullable=True)
    status = Column("status", String(50), default="ACTIVE")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

class SysCacheEntity(Base):
    """系统缓存表"""

    __tablename__ = "sys_cache"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    key = Column("key", String(80), nullable=False)
    value = Column("value", String(512), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

class FeedbackEntity(Base):
    """用户反馈表"""

    __tablename__ = "sys_feedback"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    account_id = Column("account_id", String(80), nullable=False)
    content = Column("content", String(2500), nullable=False)
    contact = Column("contact", String(250), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)

class SysDictTypeEntity(Base):
    """系统字典类型表"""

    __tablename__ = "sys_dict_type"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    dict_type = Column("dict_type", String(80), nullable=False)
    dict_name = Column("dict_name", String(80), nullable=False)
    status = Column("status", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

class SysDictDataEntity(Base):
    """系统字典数据表"""

    __tablename__ = "sys_dict_data"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    dict_type = Column("dict_type", String(80), nullable=False)
    dict_label = Column("dict_label", String(80), nullable=False)
    dict_value = Column("dict_value", String(80), nullable=False)
    status = Column("status", String(80), nullable=False, default= "1")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

# 数据库未创建表的话自动创建表
Base.metadata.create_all(engine)
