#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/04 20:03
# @file:models.py
import enum
from datetime import datetime
from admin.databases import Base
from sqlalchemy import String, Column, Integer, Text, DateTime, Enum, SmallInteger, DECIMAL, Boolean, ForeignKey, JSON


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


class BookPictures(Base):
    __tablename__ = 'book_pictures'
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True)
    index = Column(Integer, comment="图片索引")
    path = Column(String, comment="图片路径")


# -----------------------------------------------------------------------------
#                    下面是优化图片效果和生成语音可调参数                      ------
# -----------------------------------------------------------------------------


class SwitchType(enum.Enum):
    default = '默认样式'
    up = "向上移动"
    fades_and_out = "渐入渐出"


class SystemConfig(Base):
    __tablename__ = 'system_config'
    id = Column(Integer, primary_key=True, index=True)
    video_type = Column(Enum(SwitchType), default=SwitchType.default, comment="视频切换类型")
    spd = Column(SmallInteger, default=5, comment="语音语速控制")
    pit = Column(SmallInteger, default=5, comment="语音音调控制")
    vol = Column(SmallInteger, default=5, comment="语音音量控制")
    per = Column(SmallInteger, default=5003, comment="语音音库控制")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PromptTags(Base):
    __tablename__ = 'prompt_tags'
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, index=True)
    content = Column(String, comment="内容")
    prompt = Column(String, comment="替换的正向提示词")
    negative = Column(String, comment="替换的反向提示词")


"""
{
    "//": "高分辨率放大，true=启用，false=关闭",
    "enable_hr": true,
    "//": "重绘幅度",
    "denoising_strength": 0.4,
    "//": "图片宽度",
    "firstphase_width": 960,
    "//": "图片高度",
    "firstphase_height": 540,
    "//": "图片高分辨率放大倍数",
    "hr_scale": 2,
    "//": "高分辨率放大渲染器",
    "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
    "//": "高分辨率放大迭代次数",
    "hr_second_pass_steps": 10,
    "//": "绘图渲染器",
    "sampler_name": "DPM adaptive",
    "//": "绘图数量",
    "batch_size": 1,
    "//": "绘图迭代次数",
    "steps": 150,
    "//": "引导词关联性",
    "cfg_scale": 7,
    "//": "面部修复，true=启用，false=关闭",
    "restore_faces": false,
    "//": "负面提示词",
    "negative_prompt": "badhandv4,ng_deepnegative_v1_64t,worst quality,low quality,normal quality,lowers,monochrome,grayscales,skin spots,acnes,skin blemishes,age spot,6 more fingers on one hand,deformity,bad legs,error legs,bad feet,malformed limbs,extra limbs,ugly,poorly drawn hands,poorly drawn feet,poorly drawn face,text,mutilated,extra fingers,mutated hands,mutation,bad anatomy,cloned face,disfigured,fused fingers"
  }
"""


class StableDiffusionConfig(Base):
    __tablename__ = 'stable_diffusion_config'
    id = Column(Integer, primary_key=True, index=True)
    config_json = Column(JSON, comment="json配置")
