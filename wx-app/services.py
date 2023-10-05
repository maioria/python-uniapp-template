from datetime import datetime
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from config import Config
from database.entities import Token, UserInfo, StateTokenRelation
import requests
from core.logging import logging


class WxService:
    def __init__(self, db: Session):
        self.db = db

    def get_wechat_login_url(self, state: str):
        redirect_uri = Config.SCIO_REDIRECT_URI
        params = urlencode({
            "appid": Config.WECHAT_APP_ID,  # 替换为实际的App ID
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_userinfo",
            "state": state,  # 可选，自定义的参数，用于验证请求的合法性等
        })
        return f"{Config.WECHAT_AUTH_URL}?{params}"

    def get_user_info_by_openid(self, openid: str):
        logging.info(f'get_user_info_by_openid, openid: {openid}')
        user_info = self.db.query(UserInfo).filter(UserInfo.openid == openid).first()
        return self.__get_user_info_result(user_info)

    def save_token_by_code(self, code: str, state: str = None):
        logging.info(f'save_token_by_code, code: {code}')
        # 根据回调URL获取到的code，向微信服务器请求access_token和refresh_token
        access_token_url = f'{Config.WECHAT_API_URL}/sns/oauth2/access_token'
        params = {
            "appid": Config.WECHAT_APP_ID,
            "secret": Config.WECHAT_APP_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        }
        response = requests.get(access_token_url, params=params)
        data = response.json()
        logging.info(data)
        # 检查data是否有errcode属性，并且具有值
        if hasattr(data, 'errcode') and data['errcode']:
            return data
        token_id = self.save_token(data, state)
        user_info = self.save_user_info_by_token(token_id)
        return self.__get_user_info_result(user_info)

    def get_user_info_by_state(self, state: str):
        logging.info(f'get_user_info_by_state, state: {state}')
        # 根据state获取到的openid，查询数据库，获取用户信息，state调整为从state_token_relation表中获取
        relation = self.db.query(StateTokenRelation).filter(StateTokenRelation.state == state).first()
        if not relation:
            raise Exception('state不存在')
        token = self.db.query(Token).filter(Token.id == relation.token_id).first()
        user_info = self.db.query(UserInfo).filter(UserInfo.openid == token.openid).first()
        if not user_info:
            raise Exception('用户信息不存在')
        return self.__get_user_info_result(user_info)

    def save_token(self, data: dict, state: str = None) -> int:
        # 根据openid检查是否存在数据，存在则更新，不存在则插入
        token = self.db.query(Token).filter(Token.openid == data['openid']).first()
        if token:
            token.access_token = data['access_token']
            token.expires_in = data['expires_in']
            token.refresh_token = data['refresh_token']
            token.scope = data['scope']
            token.update_time = datetime.now()
        else:
            token = Token(
                access_token=data['access_token'],
                expires_in=data['expires_in'],
                refresh_token=data['refresh_token'],
                openid=data['openid'],
                scope=data['scope'],
            )
            self.db.add(token)
        self.db.commit()

        # 如果存在state，则保存state与token_id的关联关系，数据保存在StateTokenRelation实体中，如果关联关系已经存在，则不需要保存
        if state:
            relation = self.db.query(StateTokenRelation).filter(StateTokenRelation.state == state,
                                                                StateTokenRelation.token_id == token.id).first()
            if not relation:
                relation = StateTokenRelation(
                    state=state,
                    token_id=token.id,
                )
                self.db.add(relation)
                self.db.commit()

        return token.id

    def save_user_info_by_token(self, token_id: int) -> UserInfo:
        # 查询出token数据，然后保存用户信息
        token = self.db.query(Token).filter(Token.id == token_id).first()
        if not token:
            raise Exception('token不存在')
        user_info_url = f'{Config.WECHAT_API_URL}/sns/userinfo'
        user_info_params = {
            "access_token": token.access_token,
            "openid": token.openid,
            "lang": "zh_CN",
        }
        user_info_response = requests.get(user_info_url, params=user_info_params)
        user_info_response.encoding = 'utf-8'
        user_info_data = user_info_response.json()
        return self.save_user_info(token_id, user_info_data)

    def save_user_info(self, token_id: int, user_info_data: dict) -> UserInfo:
        # 解析data信息，保存到数据库的user_info表中
        # 根据openid检查是否存在数据，存在则更新，不存在则插入
        user_info = self.db.query(UserInfo).filter(UserInfo.openid == user_info_data['openid']).first()
        if user_info:
            user_info.token_id = token_id
            user_info.nickname = user_info_data['nickname']
            user_info.sex = user_info_data['sex']
            user_info.province = user_info_data['province']
            user_info.city = user_info_data['city']
            user_info.country = user_info_data['country']
            user_info.headimgurl = user_info_data['headimgurl']
            user_info.privilege = ','.join(user_info_data['privilege']),
        else:
            user_info = UserInfo(
                token_id=token_id,
                openid=user_info_data['openid'],
                nickname=user_info_data['nickname'],
                sex=user_info_data['sex'],
                province=user_info_data['province'],
                city=user_info_data['city'],
                country=user_info_data['country'],
                headimgurl=user_info_data['headimgurl'],
                privilege=','.join(user_info_data['privilege']),
            )
            self.db.add(user_info)
        self.db.commit()
        return user_info

    def __get_user_info_result(self, user_info: UserInfo):
        return {
            "openid": user_info.openid,
            "nickname": user_info.nickname,
            "headimgurl": user_info.headimgurl
        }
