#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 16:52
# @file:cli_demo.py
import asyncio

from apps.TextSiice.app import Main as TMain
from apps.SpeechSynthesis.app import Main as SMain
from apps.PromptWords.app import Main as PMain
from apps.GeneratePictures.app import Main as GPMain
from apps.GenerateVideo.app import Main as GVMain

# Check if environment variables are present
from config import client_id, client_secret, apikey, appId, ForwardKey, sd_url, file_path

if not all((client_id, client_secret, (all([apikey, appId]), ForwardKey), sd_url, file_path)):
    raise ValueError("Environment variables are missing.")


async def main(bookname: str, tags: dict = None):
    # 处理文本
    t = TMain()
    text_list = list(filter(None, await t.txt_handle(f'{bookname}.txt')))
    print(text_list)

    # 生成音频
    s = SMain()
    audio_list = await s.text_to_audio(text_list)
    print(audio_list)

    # 生成提示词
    p = PMain()
    object_list = await p.create_prompt_words(text_list, tags)
    print(object_list)

    # 生成图片
    gp = GPMain()
    picture_path_list = gp.create_picture(object_list)
    print(picture_path_list)

    # 合并视频
    gv = GVMain()
    gv.merge_video(picture_path_list, audio_list, bookname)
    print("-------视频生成完毕-----------")
    print("------- bye -----------")


if __name__ == '__main__':
    """
    tags 针对人物或者场景增加手动提示词，支持单或多提示词操作
    """
    # tags = {
    #     "时宇": "年轻男性"
    # }
    # main("不科学御兽（第一章：御兽时代）")
    asyncio.run(main("小说"))
