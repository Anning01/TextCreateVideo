#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 13:55
# @file:app.py
import requests
import json

from requests import ConnectTimeout

from config import apikey, appId


class Main:
    apikey = apikey
    appId = appId
    url = "https://fastgpt.run/api/openapi/v1/chat/completions"

    def __str__(self):
        return "FastGPT请求失败，请检查配置！"

    def prompt_generation_chatgpt(self, param, gpt_prompt):
        # 发送HTTP POST请求
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
            'Authorization': f'Bearer {self.apikey}-{self.appId}'
        }
        data = {
            "stream": False,
            "messages": [
                {
                    "content": gpt_prompt.get("prompt") + param,
                    "role": "user"
                }
            ]
        }
        json_data = json.dumps(data)
        print("-----------开始请求FastGPT-----------")
        try:
            response = requests.post(self.url, data=json_data, headers=headers, timeout=15)
        except ConnectTimeout:
            return False, "FastGPT连接超时，15秒未响应！"
        result_json = json.loads(response.text)
        if response.status_code != 200:
            return False, "FastAPI返回状态码错误，请检查配置！"
        # 输出结果
        if result_json.get('choices'):
            try:
                return result_json['choices'][0]['message']['content'], ""
            except:
                return False, "FastAPI 接口格式发生变化，请加群联系开发者！"
        else:
            return False, result_json.get('message')


if __name__ == '__main__':
    m = Main()
    m.prompt_generation_chatgpt("天空一声惊响，老子闪亮登场。")