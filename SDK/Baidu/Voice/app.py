#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 09:33
# @file:app.py
import urllib
from urllib.parse import quote_plus
import uuid
from datetime import datetime

import requests
import os
import json
from config import client_id, client_secret, file_path


class Main:
    client_id = client_id
    client_secret = client_secret

    def create_access_token(self):
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}"
        payload = ""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print("-----------向百度获取 access_token API 发起请求了-----------")
        access_token = response.json()
        access_token.update({"time": datetime.now().strftime("%Y-%m-%d")})
        with open('access_token.json', 'w', encoding='utf-8') as f:
            json.dump(access_token, f)
        return access_token

    def get_access_token(self):
        if os.path.exists('access_token.json'):
            with open('access_token.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            time = data.get("time")
            if time and (datetime.now() - datetime.strptime(time, '%Y-%m-%d')).days >= 29:
                return self.create_access_token()
            return data
        return self.create_access_token()

    def text_to_audio(self, text: str, index: int):
        url = "https://tsn.baidu.com/text2audio"
        text = text.encode('utf8')
        FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
        FORMAT = FORMATS[6]
        data = {
            # 合成的文本，文本长度必须小于1024GBK字节。建议每次请求文本不超过120字节，约为60个汉字或者字母数字。
            "tex": text,
            # access_token
            "tok": self.get_access_token().get("access_token"),
            # 用户唯一标识，用来计算UV值。建议填写能区分用户的机器 MAC 地址或 IMEI 码，长度为60字符以内
            "cuid": hex(uuid.getnode()),
            # 客户端类型选择，web端填写固定值1
            "ctp": "1",
            # 固定值zh。语言选择,目前只有中英文混合模式，填写固定值zh
            "lan": "zh",
            # 语速，取值0-15，默认为5中语速
            "spd": 5,
            # 音调，取值0-15，默认为5中语调
            "pit": 5,
            # 音量，基础音库取值0-9，精品音库取值0-15，默认为5中音量（取值为0时为音量最小值，并非为无声）
            "vol": 5,
            # (基础音库) 度小宇=1，度小美=0，度逍遥（基础）=3，度丫丫=4
            # (精品音库) 度逍遥（精品）=5003，度小鹿=5118，度博文=106，度小童=110，度小萌=111，度米朵=103，度小娇=5
            "per": 5003,
            # 3为mp3格式(默认)； 4为pcm-16k；5为pcm-8k；6为wav（内容同pcm-16k）; 注意aue=4或者6是语音识别要求的格式，但是音频内容不是语音识别要求的自然人发音，所以识别效果会受影响。
            "aue": FORMAT
        }
        data = urllib.parse.urlencode(data)
        response = requests.post(url, data)
        if response.status_code == 200:
            if response.json().get("err_no"):
                print(f"-----------Baidu API 返回错误代码：{response.json().get('err_msg')}-----------")
                return False
            result_str = response.content
            save_file = str(index) + '.' + FORMAT
            audio = os.path.join(file_path, "audio")
            if not os.path.isdir(audio):
                os.mkdir(audio)
            audio_path = os.path.join(audio, save_file)
            with open(audio_path, 'wb') as of:
                of.write(result_str)
            return audio_path
        else:
            return False


if __name__ == '__main__':
    m = Main()
    m.text_to_audio("叶无名是一个少林寺的俗家弟子，他天资聪颖，博览群书，精通天文地理和阴阳八卦", 1)
