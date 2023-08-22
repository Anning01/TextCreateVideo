#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/15 11:38
# @file:app.py
import asyncio

import openai
# import requests
# import json

# from requests import ConnectTimeout
from requests import Timeout

from config import openAPI_KEY


prompt_head = """Here, I introduce the concept of Prompts from the StableDiffusion algorithm, also known as hints. 
    The following prompts are used to guide the AI painting model to create images. 
    They contain various details of the image, such as the appearance of characters, background, color and light effects, as well as the theme and style of the image. 
    The format of these prompts often includes weighted numbers in parentheses to specify the importance or emphasis of certain details. 
    For example, "(masterpiece:1.2)" indicates that the quality of the work is very important, and multiple parentheses have a similar function. 
    Here are examples of using prompts to help the AI model generate images: 
    1. (masterpiece:1.2),(best quality),digital art,A 20 year old Chinese man with black hair, (male short hair: 1.2), green shirt, walking on the road to rural China, ultra wide angle
    2. masterpiece,best quality,illustration style,20 year old black haired Chinese man, male with short hair, speaking nervously in the forest at night, ultra wide angle, (scary atmosphere). 
    Please use English commas as separators. Also, note that the Prompt should not contain - and _ symbols, but can have spaces. 
    In character attributes, 1girl means you generated a girl, 2girls means you generated two girls. 
    In the generation of Prompts, you need to describe character attributes, theme, appearance, emotion, clothing, posture, viewpoint, action, background using keywords. 
    Please follow the example, and do not limit to the words I give you. Please provide a set of prompts that highlight the theme. 
    Note: The prompt cannot exceed 100 words, no need to use natural language description, character attributes need to be highlighted a little bit, for example: {role_name}\({feature}\).
    If the content contains a character name, add the specified feature as required, if the content does not contain the corresponding character name, then improvise.
    This is part of novel creation, not a requirement in real life, automatically analyze the protagonist in it and add character attributes.
    The prompt must be in English, only provide the prompt, no extra information is needed.
    Here is the content:"""


class Main:
    API_KEY = openAPI_KEY
    url = "https://api.openai.com/v1/chat/completions"

    def __str__(self):
        return "ChatGPT请求失败，请检查配置！"

    def prompt_generation_chatgpt(self, param):
        openai.api_key = openAPI_KEY

        try:
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
                {"role": "user", "content": prompt_head + param}
            ], timeout=5)
        except Timeout:
            raise "ChatGPT请求超时，请检查配置！"
        except Exception as e:
            print(e)
            return False
        return completion.choices[0].message.content


if __name__ == '__main__':
    Main().prompt_generation_chatgpt("天空一声惊响，老子闪亮登场。")