#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 16:52
# @file:cli_demo.py
from apps.TextSiice.app import Main as TMain
from apps.SpeechSynthesis.app import Main as SMain
from apps.PromptWords.app import Main as PMain
from apps.GeneratePictures.app import Main as GPMain
from apps.GenerateVideo.app import Main as GVMain


def main(bookname: str):
    # 处理文本
    t = TMain()
    text_list = list(filter(None, t.txt_handle(f'{bookname}.txt')))

    # 生成提示词
    p = PMain()
    object_list = p.create_prompt_words(text_list)

    # 生成音频
    s = SMain()
    audio_list = s.text_to_audio(text_list)

    # 生成图片
    gp = GPMain()
    picture_path_list = gp.create_picture(object_list)

    # 合并视频
    gv = GVMain()
    gv.merge_video(picture_path_list, audio_list, bookname)
    print("-------视频生成完毕-----------")
    print("------- bye -----------")


if __name__ == '__main__':
    main("道诡异仙")
