#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 13:54
# @file:app.py
import asyncio

from SDK.StableDiffusion.app import Main as M


class Main:

    def create_picture(self, obj_list: list, book_name=None, sd_config=None):
        """
        使用AI生成图片
        参数要求 包含着 坐标、英文提示词、英文反向提示词、中文文本 列表
        :return: 图片路径列表
        """
        picture_path_list = asyncio.run(M().draw_picture(obj_list, book_name, sd_config))
        return picture_path_list
