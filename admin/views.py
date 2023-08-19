#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/04 20:52
# @file:views.py

import sys

if sys.platform.startswith('linux'):
    print('当前系统为 Linux')
    __import__('views.cpython-310-darwin.so')
elif sys.platform.startswith('win'):
    print('当前系统为 Windows')
    __import__('views.cp310-win_amd64.pydimport.pyd')

elif sys.platform.startswith('darwin'):
    print('当前系统为 macOS')
    __import__('views.cpython-310-darwin.so')

else:
    print('无法识别当前系统')
    raise Exception('无法识别当前系统')

