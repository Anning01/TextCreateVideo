#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 16:02
# @file:config.py
"""
启动该文件，将media下的xxx.txt转为视频
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 百度API配置 填后面 "" 里面就行
client_id = os.getenv("client_id") or ""
client_secret = os.getenv("client_secret") or ""

# fastgpt 配置 需要自己配置 填后面 "" 里面就行
apikey = os.getenv("apikey") or ""
appId = os.getenv("appId") or ""

# API2D 的配置 防止 fastapi 出错 # 和fastapi 选一个就行
ForwardKey = os.getenv("ForwardKey") or ""

# Stable Diffusion 启动路径配置 默认
sd_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# 文件默认位置
file_path = os.getcwd() + "/media/"
if not os.path.exists(file_path):
    os.makedirs(file_path)

# Check if environment variables are present
if not all((client_id, client_secret, (all([apikey, appId]), ForwardKey), sd_url, file_path)):
    raise ValueError("Environment variables are missing.")
