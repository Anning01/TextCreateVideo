#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 11:30
# @file:app.py
import os

from config import file_path


class Main:

    async def txt_handle(self, filepath):
        """
        txt文件处理
        :return:
        """
        path = os.path.join(file_path, filepath)
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在，根路名为{path}")
        file = open(path, 'r', encoding='utf-8')
        content = file.read().replace('\n', '')
        text_list = await self.txt_long(content.split('。'))
        return await self.txt_short(text_list)

    async def txt_short(self, text_list: list):
        """
        处理文本过短的问题
        :return:
        """
        for index, value in enumerate(text_list):
            # 一段话少于15字，则拼接上一段话
            if len(value) < 15 and len(text_list) > 1:
                if index == (len(text_list) - 1):
                    x = False
                elif index == 0:
                    x = True
                else:
                    x = len(text_list[index - 1]) - len(text_list[index + 1]) >= 0
                if index == 0 or x:
                    print(text_list)
                    print(len(text_list))
                    print(index)
                    text_list[index + 1] = f"{value}。" + text_list[index + 1]
                else:
                    text_list[index - 1] = text_list[index - 1] + f"。{value}"
                text_list.pop(index)
        return text_list

    async def txt_long(self, text_list: list):
        """
        处理文本过长的问题
        :return:
        """
        for index, value in enumerate(text_list):
            if len(value) > 60:
                value_list = await self.recursion(value)
                text_list.pop(index)
                for i, v in enumerate(value_list):
                    text_list.insert(index + i, v)
        return text_list

    async def recursion(self, value):
        value_list = value.split("，")
        if len(value_list) >= 2:
            for i in value_list:
                if len(i) > 60:
                    return await self.recursion(i)
            head_str = ""
            foot_str = ""
            while value_list:
                if len(head_str) > len(foot_str):
                    foot_str += f'{value_list[-1]}，'
                    value_list.pop(-1)
                elif len(head_str) < len(foot_str):
                    head_str += f'{value_list[0]}，'
                    value_list.pop(0)
                else:
                    foot_str += f'{value_list[-1]}，'
                    value_list.pop(-1)
                    head_str += f'{value_list[0]}，'
                    value_list.pop(0)
            return [head_str, foot_str]
        else:
            value_list = value[len(value) // 2]
            for i in value_list:
                if len(i) > 60:
                    return await self.recursion(i)
            return value_list


if __name__ == '__main__':
    import asyncio
    asyncio.run(Main().txt_handle("道诡异仙.txt"))
