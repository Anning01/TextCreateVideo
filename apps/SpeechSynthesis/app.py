#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 14:12
# @file:app.py
import asyncio

from SDK.Baidu.Voice.app import Main as M


class Main:

    async def text_to_audio(self, text_list: list, bookname=None, config=None):
        """
        文字转语音方法
        :param text_list:
        :return: [0.wav, 1.wav,...]
        """
        audio_list = []

        for index, value in enumerate(text_list):
            if len(value) > 60:
                print("----------text_to_speech 方法传入文本长度不能超过60个字----------")
                print("-----------下个版本对60字以上自动做长文本转语音操作----------------")
            m = M()
            result = await m.text_to_audio(value, index, bookname, config)
            print(f"-----------生成第{index}段音频-----------")
            if not result:
                print("----------text_to_speech 百度语音库异常----------")
                raise Exception("百度语音库异常")
            audio_list.append(result)

        return audio_list
