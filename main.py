import re

import requests
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, JSONResponse

from admin import models
from admin.databases import engine
import admin.views


"""
第一步、将用户输入的文本进行切割，按照逗号或者句号切割
需要的数据，text, bookname
bookname: 书名
text: 书内容文本
输出的数据，[text,text,...]

第二步、使用chatGPT生成提示词
需要的的数据 [text,text,...]
输出的数据，[{text,index,prompt,negative},...]
text:原文本
index:原文本坐标
prompt:英文提示词
negative:英文反向提示词

第三步、调用百度语音合成包进行语音合成
需要的的数据 [{text,index}, {text,index},...]
输出的数据，[index.wav, index.wav, ...]

第四步、使用stable diffusion生成图片
需要的的数据 [{prompt, negative, index},...]
输出的数据，[index.png, index.png, ...]

第五步、使用moviepy将图片和语音结合起来生成视频
需要的的数据 [{index.png, index.wav},...]
输出的数据，[index.mp4, ...]
"""

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "*",
]


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse({"code": 0, "message": str(e)}, status_code=200)


# 自定义中间件
class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        # 获取请求头的Authorization
        headers = dict(scope['headers'])
        token = headers.get(b'authorization')
        token = str(token)
        if 'Bearer' in token:
            token = token.replace("Bearer ", "")
            if token:
                # 验证token
                verify_token(token)
        await self.app(scope, receive, send)


app.middleware('http')(catch_exceptions_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)


# 验证token函数
def verify_token(token: str):
    mac = admin.views.get_mac_address()
    # mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    token = token[2:-1]
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    res = requests.get(f"http://8.134.91.58/mac/?mac_address={mac}", headers=headers)
    data = res.json()
    if res.status_code != 200 or data.get("code") != 200:
        raise Exception(data.get("msg", "服务器异常"))
    return True


@app.get("/", response_class=HTMLResponse)
async def root():
    return open("dist/index.html", 'r').read()


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(
    admin.views.router,
    prefix="",
    tags=["后台"],
    responses={404: {"description": "Not found"}},
)

app.mount('/media', StaticFiles(directory="media"), 'media')
app.mount('', StaticFiles(directory="dist"), 'dist')

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)