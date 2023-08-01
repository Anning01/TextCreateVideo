#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 11:30
# @file:app.py
from config import file_path


class Main:

    def txt_handle(self, filepath):
        """
        txt文件处理
        :return:
        """
        file = open(file_path + filepath, 'r')
        content = file.read().replace('\n', '')
        return content.split('。')


if __name__ == '__main__':
    m = Main()
    m.txt_handle("道诡异仙.txt")
