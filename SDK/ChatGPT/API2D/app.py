#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 18:08
# @file:app.py

import requests
from config import ForwardKey
from requests import ConnectionError
from requests import Timeout

class Main:
    ForwardKey = ForwardKey
    url = "https://oa.api2d.net/v1/chat/completions"

    def __str__(self):
        return "API2D请求失败，请检查配置！"

    def prompt_generation_chatgpt(self, param, gpt_prompt):
        # 发送HTTP POST请求
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ForwardKey}'
            # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格。
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": gpt_prompt.get("prompt") + param, }]
        }
        print("-----------开始请求API2D-----------")
        try:
            response = requests.post(self.url, headers=headers, json=data, timeout=15)
        except Timeout:
            return False, "API2D连接超时，15秒未响应！"
        except ConnectionError:
            return False, f"连接错误，{self.url} 建立连接失败，请检查网络。"
        except Exception as e:
            return False, str(e)
        if response.status_code != 200:
            return False, response.json().get("message", "API2D返回状态码错误，请检查配置！")
        # 发送HTTP POST请求
        result_json = response.json()
        # 输出结果
        return result_json["choices"][0]["message"]["content"], ""


if __name__ == '__main__':
    Main().prompt_generation_chatgpt("天空一声惊响，老子闪亮登场。")

