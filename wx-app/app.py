from hashlib import sha1
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from config import Config
from database import get_db
from exceptions import ApiException
from services import WxService

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class ApiResponse:
    def __init__(self, code: str = '200', status: str = 'SUCCESS', data=None, message: str = 'success'):
        self.code = code
        self.status = status
        self.data = data
        self.message = message


# 有任何异常抛出都转到error.html页面
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("error.html", {"request": request, "exception": exc})


# ApiException要以json的方式返回
@app.exception_handler(ApiException)
async def exception_handler(request: Request, exc: ApiException):
    """返回code为401的json数据"""
    return JSONResponse(headers={
        'Access-Control-Allow-Origin': "*",
        'Access-Control-Allow-Methods': "*",
        'Access-Control-Allow-Headers': "*",
    }, content=ApiResponse(code='400', status='FAILED', message=str(exc)))


@app.get("/")
async def root(state: str = None, db=Depends(get_db)):
    wx_service = WxService(db)
    return ApiResponse(data=wx_service.get_wechat_login_url(state))


@app.get("/test")
async def root(db=Depends(get_db)):
    wx_service = WxService(db)
    wx_service.save_user_info_by_token(2)
    return {"wechat_login_url": ''}


@app.get("/wechat/callback")
async def wechat_callback(request: Request, code: str, state: str = None, db=Depends(get_db)):
    if state and state == 'xiaowen':
        # 如果state是xiaowen，页面重定向到 http://192.168.5.7:8080/pages/login/index?code={code}
        return RedirectResponse(url=f'http://192.168.5.7:8080/pages/login/index?code={code}')
    wx_service = WxService(db)
    wx_service.save_token_by_code(code, state)
    return templates.TemplateResponse("callback.html", {"request": request})


# 根据微信返回的openid来获取用户信息
@app.get("/user-info")
async def user_info_api(code: str = None, state: str = None,
                        db=Depends(get_db)):
    if not code and not state:
        raise Exception('code, state 不能同时为空')
    wx_service = WxService(db)
    user_info = None
    # 捕获所有的异常，重新抛出ApiException
    try:
        if code:
            user_info = wx_service.save_token_by_code(code, state)
        elif state:
            user_info = wx_service.get_user_info_by_state(state)
    except Exception as e:
        raise ApiException(e)
    return ApiResponse(data=user_info)


# 微信服务器验证接口
@app.get("/check_signature")
def check_signature(signature: str, timestamp: str, nonce: str, echostr: str) -> Response:
    tmp_arr = [Config.WECHAT_CHECK_SIGNATURE_TOKEN, timestamp, nonce]
    tmp_arr.sort()
    tmp_str = "".join(tmp_arr)
    tmp_str = sha1(tmp_str.encode()).hexdigest()

    if tmp_str == signature:
        # 返回时不需要带上双引号
        return Response(content=echostr, media_type="text/plain")
    else:
        raise HTTPException(status_code=403, detail="Invalid signature")


if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8086, reload=True)
