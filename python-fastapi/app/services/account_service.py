from io import BytesIO
import base64
import qrcode
import requests
from sqlalchemy.orm import Session

from app.core import wechat_component, auth
from app.core.utils import *
from app.db.entities import *
from app.models.account_models import *
from app.core.logging import logging
from app.config import Config


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def wechat_redirect_url(self):
        """通过微信基础服务来获取跳转地址, 请求远程服务 http://wx.sciotech.cn 来获取接口返回的值"""
        response = requests.get(Config.WE_CHAT_SERVER_URL, params={'state': 'maioria-github-template'})
        json_dict = response.json()
        return json_dict['data']

    def wechat_scan_url(self):
        # 先生成一个uuid，做为state标识
        state = f'client_{short_uuid()}'
        response = requests.get(Config.WE_CHAT_SERVER_URL, params={'state': state})
        json_dict = response.json()
        url = json_dict['data']
        # 生成QRCode并保存为ByteIO对象
        img = qrcode.make(url)
        buffered = BytesIO()
        img.save(buffered)

        # 将ByteIO对象中的数据转换为base64编码
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return {'state': state, 'base64': img_str}

    def wechat_login(self, dto: WechatLoginDTO):
        """通过微信基础服务来获取跳转地址, 请求远程服务 {Config.WE_CHAT_SERVER_URL} 来获取接口返回的值"""

        if not dto.code and not dto.state:
            raise Exception('code与state不能同时为空')

        response = requests.get(f'{Config.WE_CHAT_SERVER_URL}/user-info', params={'code': dto.code, 'state': dto.state})
        json_dict = response.json()
        if json_dict['code'] == '400':
            # 用户还未进行验证
            return None

        data = json_dict['data']
        if hasattr(data, 'errcode') and data['errcode']:
            raise Exception(f'微信授权失败: {data["errcode"]}')

        # 按openid查找，如果用户存在，直接返回登录成功数据，如果用户不存在，生成新用户后再返回登录成功数据
        openid = data['openid']
        account = self.db.query(AccountEntity).filter(AccountEntity.wechat_open_id == openid).first()
        if not account:
            account = AccountEntity(id=f'wechat_{short_uuid()}', wechat_open_id=openid, nickname=data['nickname'],
                                    head_img=data['headimgurl'])
            self.db.add(account)
            self.db.commit()
            self.db.flush()
        return auth.init_token(account.nickname, account.id)

    def visitor_login(self, fingerprint: str, client_host: str, user_agent: str = None):
        """先检查此ip下是否有用户，如果有，直接返回ip下的用户，如果没有，就生成新的访客"""
        visitor = (
            self.db.query(VisitorEntity).filter_by(fingerprint=fingerprint).first()
        )
        if not visitor:
            visitor = VisitorEntity(
                id=f"visitor_{short_uuid()}",
                fingerprint=fingerprint,
                client_host=client_host,
                user_agent=user_agent,
            )
            self.db.add(visitor)
            self.db.commit()
        return auth.init_token(visitor.id, visitor.id)

    def get_account_info(self, account_id: str):
        """获取用户的今日聊天次数与总次数返回"""
        # 如果是访客，就返回访客的信息
        if account_id.startswith("visitor_"):
            account = self.db.query(VisitorEntity).filter_by(id=account_id).first()
            return {
                "account_id": account.id,
                "head_img": None,
                "nickname": account.id
            }
        else:
            account = self.db.query(AccountEntity).filter_by(id=account_id).first()
            return {
                "account_id": account_id,
                "head_img": account.head_img,
                "nickname": account.nickname
            }
        if not account:
            raise Exception("User not found")

