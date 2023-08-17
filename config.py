#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 16:02
# @file:config.py
"""
该文件，将media下的xxx.txt转为视频
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 百度API配置 填后面 "" 里面就行
client_id = os.getenv("client_id") or ""  # 这里填写百度的 API Key
client_secret = os.getenv("client_secret") or ""  # 这里填写百度的 Secret Key

# fastgpt 配置 需要自己配置 填后面 "" 里面就行  https://fastgpt.run/
apikey = os.getenv("apikey") or ""
appId = os.getenv("appId") or ""

# API2D 的配置 防止 fastapi 出错 # 和fastapi 选一个就行
ForwardKey = os.getenv("ForwardKey") or ""
openAPI_KEY = os.getenv("openAPI_KEY") or ""

# Stable Diffusion 启动路径配置 默认
sd_url = os.getenv("sd_url") or "http://127.0.0.1:7860/sdapi/v1/txt2img"

# 项目绝对路径
project_path = Path(__file__).resolve().parent

# 文件默认位置
file_path = os.path.join(os.getcwd(), "media")
if not os.path.exists(file_path):
    os.makedirs(file_path)


