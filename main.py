from fastapi import FastAPI

app = FastAPI()

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
