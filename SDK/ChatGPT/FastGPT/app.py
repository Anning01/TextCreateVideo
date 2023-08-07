#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 13:55
# @file:app.py
import requests
import json
from config import apikey, appId


class Main:
    apikey = apikey
    appId = appId
    url = "https://fastgpt.run/api/openapi/v1/chat/completions"

    async def prompt_generation_chatgpt(self, param):
        # 发送HTTP POST请求
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
            'Authorization': f'Bearer {self.apikey}-{self.appId}'
        }
        data = {
            "stream": False,
            # "chatId": "3232",
            "messages": [
                {
                    "content": '根据下面的内容描述，生成一副画面并用英文单词表示：' + param,
                    "role": "user"
                }
            ]
        }
        json_data = json.dumps(data)
        # 发送HTTP POST请求
        response = requests.post(self.url, data=json_data, headers=headers, timeout=3)
        result_json = json.loads(response.text)
        if response.status_code != 200:
            print("-----------FastAPI出错了-----------")
            return False
        # 输出结果
        if result_json.get('responseData'):
            return result_json['responseData'][0]['answer']
        else:
            print(f"-----------FastAPI {result_json.get('message')}-----------")
            return False


if __name__ == '__main__':
    m = Main()
    m.prompt_generation_chatgpt("天空一声惊响，老子闪亮登场。")