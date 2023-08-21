#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/04 23:41
# @file:type_annotation.py
from typing import Optional

from pydantic import BaseModel, Field

#
# class BookModel(BaseModel):
#     name: str
#     path: Optional[str] = None
#
#     class Config:
#         orm_mode = True
from admin.models import SwitchType

# video_type: Optional[SwitchType]


class BaiduConfig(BaseModel):
    spd: int = Field(ge=0, le=15, description="语速，取值0-15，默认为5中语速", default=5)
    pit: int = Field(ge=0, le=15, description="音调，取值0-15，默认为5中语调", default=5)
    vol: int = Field(ge=0, le=15, description="音量，基础音库取值0-9，精品音库取值0-15，默认为5中音量（取值为0时为音量最小值，并非为无声）", default=5)
    per: int = Field(description="(基础音库) 度小宇=1，度小美=0，度逍遥（基础）=3，度丫丫=4 (精品音库) 度逍遥（精品）=5003，度小鹿=5118，度博文=106，度小童=110，度小萌=111，度米朵=103，度小娇=5", default=5003)


class systemConfig(BaseModel):
    video_type: SwitchType


class Config(BaseModel):
    baidu_api_key: Optional[str] = ""
    baidu_secret_key: Optional[str] = ""
    fastgpt_appid: Optional[str] = ""
    fastgpt_api_key: Optional[str] = ""
    api2d_forward_key: Optional[str] = ""
    sd_url: Optional[str] = ""
    openAPI_KEY: Optional[str] = ""
    baidu_config: BaiduConfig


class BookSectionType(BaseModel):
    id: int
    book_id: int
    paragraph: str
    index: int
    prompt: str
    negative: str
    name: str

    class Config:
        from_attributes = True


class BookVoiceType(BaseModel):
    id: int
    book_id: int
    path: str
    index: int
    name: str

    class Config:
        from_attributes = True


class BookPicturesType(BaseModel):
    id: int
    book_id: int
    path: str
    index: int
    name: str

    class Config:
        from_attributes = True


class BookClassType(BaseModel):
    id: int
    name: str


class PromptTagsType(BaseModel):
    id: Optional[int]
    book_id: int
    content: str
    prompt: str
    negative: str
    name: Optional[str]


class PromptTagsCreateType(BaseModel):
    book_id: int
    content: str
    prompt: str
    negative: str
