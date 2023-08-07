#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/04 23:41
# @file:type_annotation.py
from typing import Optional

from pydantic import BaseModel


#
# class BookModel(BaseModel):
#     name: str
#     path: Optional[str] = None
#
#     class Config:
#         orm_mode = True


class Config(BaseModel):
    baidu_api_key: Optional[str] = ""
    baidu_secret_key: Optional[str] = ""
    fastgpt_appid: Optional[str] = ""
    fastgpt_api_key: Optional[str] = ""
    api2d_forward_key: Optional[str] = ""
    sd_url: Optional[str] = ""


