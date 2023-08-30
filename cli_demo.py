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

prompt_dict = {
    "negative_prompt": "badhandv4,ng_deepnegative_v1_64t,worst quality,low quality,normal quality,lowers,monochrome,grayscales,skin spots,acnes,skin blemishes,age spot,6 more fingers on one hand,deformity,bad legs,error legs,bad feet,malformed limbs,extra limbs,ugly,poorly drawn hands,poorly drawn feet,poorly drawn face,text,mutilated,extra fingers,mutated hands,mutation,bad anatomy,cloned face,disfigured,fused fingers",
    "prompt": "Task: I will tell you the theme of the prompt to generate in natural language, and your task is to imagine a complete picture based on this theme, then transform it into a detailed, high-quality prompt, so that Stable Diffusion can generate high-quality images. Prompt concept: A prompt is used to describe images, composed of common, often used words, using English half-width ',' as a separator. Each word or phrase separated by ',' is known as a tag. So a prompt consists of a series of tags separated by ','. Below, I will explain the steps to generate a prompt, where the prompt can be used to describe characters, scenery, objects or abstract digital art drawings. Prompt requirements: The prompt should contain elements such as the main subject of the image, texture, additional details, image quality, artistic style, color tone, lighting, etc. Attention, the prompt you output cannot be split into sections, for example, descriptions like 'medium:','Main subject:','Keywords:','Prompt:','texture:','additional details:','image quality:','artistic style:','color tone:','lighting:','tags:' are not needed and it cannot contain ':' or '.'! Main subject: Briefly describe the main subject of the picture in English, such as 'A girl in a garden'. This encapsulates the core content of the image (the subject can be people, things, objects, landscapes). This part is generated based on the theme I give you each time. You can add more reasonable details related to the theme. For character themes, you must describe the character's eyes, nose, and lips, for example 'beautiful detailed eyes, beautiful detailed lips, extremely detailed eyes and face, long eyelashes', to avoid Stable Diffusion randomly generating deformed facial features, this is very important. The theme I provide is:",
    "default_prompt": "Big scene, best quality,masterpiece, illustration, an extremely delicate and beautiful, extremely detailed,CG, unity, 8k wallpaper,"
}


def main(bookname: str, tags: list | None = None):
    # 处理文本
    t = TMain()
    text_list = list(filter(None, t.txt_handle(f'{bookname}.txt')))
    print(text_list)

    # 生成提示词
    p = PMain()
    object_list = p.create_prompt_words(text_list, tags, prompt_dict)
    print(object_list)

    # 生成音频
    s = SMain()
    audio_list = s.text_to_audio(text_list)
    print(audio_list)

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

    main("小说")
