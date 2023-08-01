#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 13:54
# @file:app.py

from SDK.StableDiffusion.app import Main as M


class Main:

    def create_picture(self, obj_list: list):
        """
        使用AI生成图片
        参数要求 包含着 坐标、英文提示词、英文反向提示词、中文文本 列表
        :return: 图片路径列表
        """
        m = M()
        picture_path_list = m.draw_picture(obj_list)
        return picture_path_list
