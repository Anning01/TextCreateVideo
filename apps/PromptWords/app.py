#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 13:54
# @file:app.py
from SDK.ChatGPT.FastGPT.app import Main as FM
from SDK.ChatGPT.API2D.app import Main as AM
from config import apikey, appId, ForwardKey


class Main:

    # 默认反向提升词
    negative = "NSFW,sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, bad anatomy,(long hair:1.4),DeepNegative,(fat:1.2),facing away, looking away,tilted head, {Multiple people}, lowres,bad anatomy,bad hands, text, error, missing fingers,extra digit, fewer digits, cropped, worstquality, low quality, normal quality,jpegartifacts,signature, watermark, username,blurry,bad feet,cropped,poorly drawn hands,poorly drawn face,mutation,deformed,worst quality,low quality,normal quality,jpeg artifacts,signature,watermark,extra fingers,fewer digits,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,text,error,missing fingers,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,"
    # 默认提示词
    prompt = "best quality,masterpiece,illustration, an extremely delicate and beautiful,extremely detailed,CG,unity,8k wallpaper, "

    def create_prompt_words(self, text_list: list):
        """
        生成英文提示词
        :return: [{prompt, negative, text, index},...]
        """
        # 包含着 坐标、英文提示词、英文反向提示词、中文文本 列表
        data = []
        instance_class_list = []
        if all([apikey, appId]):
            instance_class_list.append(FM())
        if ForwardKey:
            instance_class_list.append(AM())
        for index, value in enumerate(text_list):
            prompt = instance_class_list[0].prompt_generation_chatgpt(value)
            if not prompt:
                if len(instance_class_list) >= 1:
                    instance_class_list.pop(0)
                    prompt = instance_class_list[0].prompt_generation_chatgpt(value)
                    if not prompt:
                        print("------fastgpt和API2D都无法使用---------")
                        raise Exception("请检查代码")
                else:
                    print("------fastgpt和API2D都无法使用---------")
                    raise Exception("请检查代码")
            print(f"-----------生成第{index}段提示词-----------")
            data.append({
                "index": index,
                "text": value,
                "prompt": self.prompt + prompt,
                "negative": self.negative,
            })
        return data
