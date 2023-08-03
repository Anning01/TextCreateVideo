#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 11:30
# @file:app.py
import os

from config import file_path


class Main:

    def txt_handle(self, filepath):
        """
        txt文件处理
        :return:
        """
        path = os.path.join(file_path, filepath)
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在，根路名为{path}")
        file = open(path, 'r')
        content = file.read().replace('\n', '')
        return self.txt_short(content.split('。'))

    def txt_short(self, text_list: list):
        """
        处理文本过短的问题
        :return:
        """
        for index, value in enumerate(text_list):
            # 一段话少于15字，则拼接上一段话
            if len(value) < 15:
                if index == (len(text_list) - 1):
                    x = False
                elif index == 0:
                    x = True
                else:
                    x = len(text_list[index - 1]) - len(text_list[index + 1]) >= 0
                if index == 0 or x:
                    text_list[index + 1] = f"{value}。" + text_list[index + 1]
                else:
                    text_list[index - 1] = text_list[index - 1] + f"。{value}"
                text_list.pop(index)
        return text_list


if __name__ == '__main__':
    m = Main()
    m.txt_handle("道诡异仙.txt")
