#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/04 20:03
# @file:models.py
import enum
from datetime import datetime
from admin.databases import Base
from sqlalchemy import String, Column, Integer, Text, DateTime, Enum


# -----------------------------------------------------------------------------
#                         下面是生产视频必须要的参数                         ------
# -----------------------------------------------------------------------------

class StatusEnum(enum.Enum):
    default = '未开始'
    underway = "进行中"
    complete = '已完成'
    failure = '失败'


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, comment="书名")
    path = Column(String, comment="书路径")
    create_dt = Column(DateTime, default=datetime.now, comment="创建时间")
    video_path = Column(String, comment="视频路径")
    status = Column(Enum(StatusEnum), default=StatusEnum.default, comment="状态")
    fail_info = Column(String, comment="失败信息")

    def __repr__(self):
        return '<Book: %s>' % self.name


class BookSection(Base):
    __tablename__ = 'book_section'
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True)
    paragraph = Column(Text, comment="书本段落")
    index = Column(Integer, comment="书本索引")
    prompt = Column(Text, comment="正向提示词")
    negative = Column(Text, comment="负向提示词")


class BookVoice(Base):
    __tablename__ = 'book_voice'
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True)
    index = Column(Integer, comment="语音索引")
    path = Column(String, comment="语音路径")

    def __repr__(self):
        return '<BookVoice: %s>' % self.name


class BookPictures(Base):
    __tablename__ = 'book_pictures'
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True)
    index = Column(Integer, comment="图片索引")
    path = Column(String, comment="图片路径")

    def __repr__(self):
        return '<BookPictures: %s>' % self.name



# -----------------------------------------------------------------------------
#                    下面是优化图片效果和生成语音可调参数                      ------
# -----------------------------------------------------------------------------
