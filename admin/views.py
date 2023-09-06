#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/19 10:06
# @file:views.py
import json
import os
import shutil
import threading
import zipfile
from typing import List, Optional

import requests
from fastapi import Depends, UploadFile, File, Request
from pydantic import BaseModel
from sqlalchemy import text, func, delete, update, insert

from admin.databases import SessionLocal
from admin.models import Book, BookSection, BookVoice, BookPictures, StatusEnum, SystemConfig, SwitchType, \
    PromptTags, StableDiffusionConfig
from admin.type_annotation import Config, BookVoiceType, systemConfig, BookSectionType, BookPicturesType, BookClassType, \
    PromptTagsType, PromptTagsCreateType
from apps.GeneratePictures.app import Main as GPMain
from apps.GenerateVideo.app import Main as GVMain
from apps.PromptWords.app import Main as PMain
from apps.SpeechSynthesis.app import Main as SMain
from apps.TextSiice.app import Main as TMain
from config import file_path, project_path, client_id, client_secret, appId, apikey, ForwardKey, sd_url, openAPI_KEY
from fastapi import APIRouter

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 请求成功数据结构
def success_data(data: dict | list, message: str = None):
    return {"code": 200, "data": data, "message": message}


# 返回错误数据结涄
def error_data(message: str, code: int = 0):
    return {"code": code, "message": message}


class VoiceDownload(BaseModel):
    id_list: list


@router.get("/book")
async def book_list(db: SessionLocal = Depends(get_db)):
    query = text(
        "SELECT id, name, path, strftime('%Y-%m-%d %H:%M:%S', create_dt), video_path, status, fail_info FROM book")
    result = db.execute(query)
    res = []
    for i in result:
        data = {
            "id": i.t[0],
            "name": i.t[1],
            "path": i.t[2],
            "create_dt": i.t[3],
            # "video": query_v.first().path if is_video else is_video
            "video_path": i.t[4],
            "status": i.t[5],
            "fail_info": i.t[6],
            # "status_value": StatusEnum[i.t[5]],
        }
        res.append(data)
    return success_data(res)
    # return success_data(db.query(Book.name, func.strftime("%Y-%m-%d", Book.create_dt)).all())


@router.delete("/book")
async def book_delete(book_id_list: VoiceDownload, db: SessionLocal = Depends(get_db)):
    stmt = delete(Book).where(Book.id.in_(book_id_list.id_list))
    db.execute(stmt)
    stmt = delete(BookSection).where(BookSection.book_id.in_(book_id_list.id_list))
    db.execute(stmt)
    stmt = delete(BookVoice).where(BookVoice.book_id.in_(book_id_list.id_list))
    db.execute(stmt)
    stmt = delete(BookPictures).where(BookPictures.book_id.in_(book_id_list.id_list))
    db.execute(stmt)
    stmt = delete(PromptTags).where(PromptTags.book_id.in_(book_id_list.id_list))
    db.execute(stmt)

    db.commit()
    return success_data({}, "删除成功")


def save_file(file: bytes, filename: str, path: str):
    name = filename.rsplit(".", 1)[0]
    path = os.path.join(path, name)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, filename)
    with open(path, "wb") as f:
        f.write(file)
    return path.replace(str(project_path), '')


@router.post("/book")
async def create_book(file: UploadFile = File(...), db: SessionLocal = Depends(get_db)):
    book_ = db.query(Book).filter(Book.name == file.filename).first()
    if book_:
        return error_data("书已存在！")
    contents = await file.read()
    path = save_file(contents, file.filename, file_path)
    book = Book(name=file.filename, path=path)
    db.add(book)
    db.commit()
    db.refresh(book)
    return success_data(book)


@router.get("/book/create/{id}")
async def create_video(id, request: Request, db: SessionLocal = Depends(get_db)):
    book = db.query(Book).get(id)
    config = db.query(SystemConfig).first()
    scene_tag = db.query(PromptTags).filter(PromptTags.book_id == book.id).all()
    sd_config = db.query(StableDiffusionConfig).first()
    if sd_config:
        sd_config = sd_config.config_json
    else:
        sd_config = json.loads(open('stable-diffusion-default.json', 'r', encoding='utf-8').read())

    prompt = ''
    default_prompt = ''
    negative = ''
    for item in sd_config:
        if item['key'] == 'prompt':
            prompt = item['value']
        if item['key'] == 'default_prompt':
            default_prompt = item['value']
        if item['key'] == 'negative_prompt':
            negative = item['value']

    prompt_dict = {
        "prompt": prompt,
        "default_prompt": default_prompt,
        "negative": negative,
    }
    book = db.query(Book).get(id)
    if book:
        path = str(project_path) + book.path
        book.status = StatusEnum.underway
        db.commit()
        t = threading.Thread(target=CreateVideo().thread_func,
                             args=[book, path, db, config, scene_tag, sd_config, prompt_dict])
        t.daemon = True
        t.start()
        return success_data({}, message="视频生成任务启动成功！")
    return error_data("书不存在！")


class CreateVideo:

    def thread_func(self, book, path, db, config, scene_tag, sd_config, prompt_dict):
        status = StatusEnum.complete
        fail_info = ''
        try:
            self.main(book, path, db, config, scene_tag, sd_config, prompt_dict)
        except Exception as error:
            status = StatusEnum.failure
            fail_info = str(error)
        stmt = update(Book).where(Book.id == book.id).values(fail_info=fail_info, status=status)
        # 执行更新操作
        db.execute(stmt)
        db.commit()
        return

    def main(self, book, path, db, config, scene_tag, sd_config, prompt_dict):
        """
        启动此方法，异步生成图片，语音，提示词
        :return:
        """
        # try:
        # 创建分割任务
        text_list = self.txt_handle(path)
        book = db.merge(book)
        count = db.query(BookSection).filter(BookSection.book_id == book.id).with_entities(
            func.count(BookSection.id)).scalar()
        if count > 0 and count == len(text_list):
            book_section = db.query(BookSection).filter(BookSection.book_id == book.id).all()
            object_list = [{"prompt": i.prompt, "negative": i.negative, "index": i.index} for i in book_section]
        else:
            if count > 0 and count != len(text_list):
                # 构建查询对象
                stmt = delete(BookSection).where(BookSection.book_id == book.id)
                # 执行更新操作
                db.execute(stmt)
                db.commit()
            # 生成提示词任务
            # scene_tag = db.merge(scene_tag)
            object_list = self.create_prompt_words(text_list, scene_tag, prompt_dict)
            print(object_list)
            data_list = []
            for i in object_list:
                data_list.append(BookSection(
                    book_id=book.id,
                    paragraph=i['text'],
                    index=i['index'],
                    prompt=i['prompt'],
                    negative=i['negative'],
                ))
            db.add_all(data_list)
            db.commit()
        count = db.query(BookVoice).filter(BookVoice.book_id == book.id).with_entities(
            func.count(BookVoice.id)).scalar()
        if count > 0 and count == len(text_list):
            book_voice = db.query(BookVoice).filter(BookVoice.book_id == book.id).all()
            audio_list = [i.path for i in book_voice]
        else:
            if count > 0 and count != len(text_list):
                # 构建查询对象
                stmt = delete(BookVoice).where(BookVoice.book_id == book.id)
                # 执行更新操作
                db.execute(stmt)
                db.commit()
            config = db.merge(config)
            # 生成音频任务
            audio_list = self.text_to_audio(text_list, book.name, config)
            audio_model_list = []
            for index, value in enumerate(audio_list):
                audio_model_list.append(BookVoice(
                    book_id=book.id,
                    index=index,
                    path=value
                ))
            db.add_all(audio_model_list)
            db.commit()
        count = db.query(BookPictures).filter(BookPictures.book_id == book.id).with_entities(
            func.count(BookPictures.id)).scalar()
        if count > 0 and count == len(text_list):
            book_pictures = db.query(BookPictures).filter(BookPictures.book_id == book.id).all()
            picture_path_list = [i.path for i in book_pictures]
        else:
            if count > 0 and count != len(text_list):
                # 构建查询对象
                stmt = delete(BookPictures).where(BookPictures.book_id == book.id)
                # 执行更新操作
                db.execute(stmt)
                db.commit()
            # 生成图片任务
            picture_path_list = self.create_picture(object_list, book.name, sd_config)
            picture_model_list = []
            for index, value in enumerate(picture_path_list):
                picture_model_list.append(BookPictures(
                    book_id=book.id,
                    index=index,
                    path=value
                ))
            db.add_all(picture_model_list)
            db.commit()
        config = db.merge(config)
        # 视频任务
        video_path = self.create_video(picture_path_list, audio_list, book.name, config)
        print(video_path)
        book = db.merge(book)
        book.video_path = video_path
        book.status = StatusEnum.complete
        db.commit()

    def txt_handle(self, path):
        """
        分隔提示符
        :return:
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在，根路名为{path}")
        file = open(path, 'r', encoding='utf-8')
        content = file.read().replace('\n', '')
        t = TMain()
        text_list = t.txt_long(content.split('。'))
        return t.txt_short(text_list)

    def text_to_audio(self, text_list, bookname, config):
        """
        生成音频
        :return:
        """
        s = SMain()
        audio_list = s.text_to_audio(text_list, bookname=bookname, config=config)
        return audio_list

    def create_prompt_words(self, text_list, tags=None, prompt_dict=None):
        """
        生成提示词
        :return:
        """
        p = PMain()
        object_list = p.create_prompt_words(text_list, tags, prompt_dict)
        # object_list = await p.create_prompt_words2(text_list, tags)

        return object_list

    def create_picture(self, obj_list, book_name, sd_config):
        """
        生成图片
        :return:
        """
        gp = GPMain()
        return gp.create_picture(obj_list, book_name, sd_config)

    def create_video(self, picture_path_list, audio_list, book_name, config):
        """
        生成视频
        :return:
        """
        gv = GVMain()
        gv_path = gv.merge_video(picture_path_list, audio_list, book_name, config, is_web=True)
        return gv_path


@router.get("/config")
async def config(db: SessionLocal = Depends(get_db)):
    baidu_config = db.query(SystemConfig).first()

    if not baidu_config:
        baidu_config = {
            "spd": 5,
            "pit": 5,
            "vol": 5,
            "per": 1,
        }
    else:
        baidu_config = baidu_config.as_dict()

    config = Config(
        baidu_api_key=client_id,
        baidu_secret_key=client_secret,
        fastgpt_appid=appId,
        fastgpt_api_key=apikey,
        api2d_forward_key=ForwardKey,
        openAPI_KEY=openAPI_KEY,
        sd_url=sd_url.replace("/sdapi/v1/txt2img", ""),
        baidu_config=baidu_config
    )
    return success_data(config.model_dump())


@router.post("/config")
async def update_config(config: Config, db: SessionLocal = Depends(get_db)):
    env = os.path.join(project_path, '.env')
    env_text = f"client_id='{config.baidu_api_key}'\nclient_secret='{config.baidu_secret_key}'\napikey='{config.fastgpt_api_key}'\nappId='{config.fastgpt_appid}'\nForwardKey='{config.api2d_forward_key}'\nopenAPI_KEY='{config.openAPI_KEY}'\nsd_url='{config.sd_url}/sdapi/v1/txt2img'"
    with open(env, 'w') as f:
        f.write(env_text)
    baidu_config = db.query(SystemConfig).first()
    if baidu_config:
        stmt = update(SystemConfig).where(SystemConfig.id == baidu_config.id).values(**config.baidu_config.model_dump())
    else:
        stmt = insert(SystemConfig).values(**config.baidu_config.model_dump())
    db.execute(stmt)
    db.commit()
    return success_data(config.model_dump(), "更新配置必须重新启动后台！")


@router.get("/config/system")
async def config(db: SessionLocal = Depends(get_db)):
    baidu_config = db.query(SystemConfig).first()
    if not baidu_config:
        baidu_config = {
            "video_type": SwitchType.default
        }
    else:
        baidu_config = {
            "video_type": baidu_config.video_type
        }
    return success_data(baidu_config)


@router.post("/config/system")
async def update_config(config: systemConfig, db: SessionLocal = Depends(get_db)):
    baidu_config = db.query(SystemConfig).first()
    if baidu_config:
        stmt = update(SystemConfig).where(SystemConfig.id == baidu_config.id).values(**config.model_dump())
    else:
        stmt = insert(SystemConfig).values(**config.model_dump())
    db.execute(stmt)
    db.commit()
    return success_data(config.model_dump(), "修改成功")


@router.get("/book/section", response_model=List[BookSectionType])
async def section_list(book_id: Optional[int] = None, db: SessionLocal = Depends(get_db)):
    if book_id:
        sections = db.query(
            BookSection.id,
            BookSection.book_id,
            BookSection.paragraph,
            BookSection.index,
            BookSection.prompt,
            BookSection.negative,
            Book.name,
        ).outerjoin(Book, BookSection.book_id == Book.id).filter(BookSection.book_id == book_id).order_by(
            BookSection.id.desc()).all()
    else:
        sections = db.query(
            BookSection.id,
            BookSection.book_id,
            BookSection.paragraph,
            BookSection.index,
            BookSection.prompt,
            BookSection.negative,
            Book.name,
        ).outerjoin(Book, BookSection.book_id == Book.id).order_by(BookSection.id.desc()).all()
    return sections


@router.put("/book/section/{id}")
async def update_section(id, book_section: BookSectionType, db: SessionLocal = Depends(get_db)):
    model = book_section.model_dump()
    del model['name']
    stmt = update(BookSection).where(BookSection.id == id).values(**model)
    db.execute(stmt)
    db.commit()
    return book_section.model_dump()


@router.delete("/book/section")
async def delete_section(book_id_list: VoiceDownload, db: SessionLocal = Depends(get_db)):
    stmt = delete(BookSection).where(BookSection.id.in_(book_id_list.id_list))
    db.execute(stmt)

    db.commit()
    return success_data({}, "删除成功")


@router.get("/book/voice", response_model=List[BookVoiceType])
async def voice_list(book_id: Optional[int] = None, db: SessionLocal = Depends(get_db)):
    if book_id:
        voices = db.query(
            BookVoice.id,
            BookVoice.book_id,
            BookVoice.index,
            BookVoice.path,
            Book.name,
        ).outerjoin(Book, BookVoice.book_id == Book.id).filter(BookVoice.book_id == book_id).order_by(
            BookVoice.id.desc()).all()
    else:
        voices = db.query(
            BookVoice.id,
            BookVoice.book_id,
            BookVoice.index,
            BookVoice.path,
            Book.name,
        ).outerjoin(Book, BookVoice.book_id == Book.id).order_by(BookVoice.id.desc()).all()

    return voices


@router.post("/book/voice/download")
async def voice_download(id_list: VoiceDownload, db: SessionLocal = Depends(get_db)):
    voices = db.query(BookVoice).filter(BookVoice.id.in_(id_list.id_list)).all()
    voice_path_list = ['.' + i.path for i in voices]
    zip_file = os.path.join(project_path, 'media')
    zip_file = os.path.join(zip_file, 'zip')
    if os.path.exists(zip_file):
        # 删除里面所有的压缩包
        shutil.rmtree(zip_file)
    os.makedirs(zip_file)
    zip_file = os.path.join(zip_file, 'voice.zip')
    with zipfile.ZipFile(zip_file, 'w') as zipObj:
        for i in voice_path_list:
            zipObj.write(i)
        zipObj.close()
    return {"url": zip_file.replace(str(project_path), '')}


@router.get("/book/pictures", response_model=List[BookPicturesType])
async def pictures_list(book_id: Optional[int] = None, db: SessionLocal = Depends(get_db)):
    if book_id:
        pictures = db.query(
            BookPictures.id,
            BookPictures.book_id,
            BookPictures.index,
            BookPictures.path,
            Book.name,
        ).outerjoin(Book, BookPictures.book_id == Book.id).filter(BookPictures.book_id == book_id).order_by(
            BookPictures.id.desc()).all()
    else:
        pictures = db.query(
            BookPictures.id,
            BookPictures.book_id,
            BookPictures.index,
            BookPictures.path,
            Book.name,
        ).outerjoin(Book, BookPictures.book_id == Book.id).order_by(BookPictures.id.desc()).all()
    return pictures


@router.post("/book/pictures/download")
async def pictures_download(id_list: VoiceDownload, db: SessionLocal = Depends(get_db)):
    pictures = db.query(BookPictures).filter(BookPictures.id.in_(id_list.id_list)).all()
    pictures_path_list = ['.' + i.path for i in pictures]
    zip_file = os.path.join(project_path, 'media')
    zip_file = os.path.join(zip_file, 'zip')
    if os.path.exists(zip_file):
        # 删除里面所有的压缩包
        shutil.rmtree(zip_file)
    os.makedirs(zip_file)
    zip_file = os.path.join(zip_file, 'pictures.zip')
    with zipfile.ZipFile(zip_file, 'w') as zipObj:
        for i in pictures_path_list:
            zipObj.write(i)
        zipObj.close()
    return {"url": zip_file.replace(str(project_path), '')}


@router.delete("/book/pictures")
async def pictures_delete(book_id_list: VoiceDownload, db: SessionLocal = Depends(get_db)):
    stmt = delete(BookPictures).where(BookPictures.id.in_(book_id_list.id_list))
    db.execute(stmt)
    db.commit()
    return success_data({}, "删除成功")


def redraw_photo(object_list, book_name, sd_config):
    print("------------开始重绘------------")
    CreateVideo().create_picture(object_list, book_name, sd_config)
    print("------------重绘完成------------")


@router.get("/book/pictures/redraw")
async def pictures_delete(pictures_id: int, db: SessionLocal = Depends(get_db)):
    pictures = db.query(BookPictures, Book.name).outerjoin(Book, BookPictures.book_id == Book.id).filter(
        BookPictures.id == pictures_id).first()
    pictures, book_name = pictures[0], pictures[1]
    book_section = db.query(BookSection).filter(BookSection.book_id == pictures.book_id,
                                                BookSection.index == pictures.index).first()
    if not book_section:
        return error_data("提示词已被删除")
    object_list = [{"prompt": book_section.prompt, "negative": book_section.negative, "index": book_section.index}]
    sd_config = db.query(StableDiffusionConfig).first()
    if sd_config:
        sd_config = sd_config.config_json
    else:
        sd_config = json.loads(open('stable-diffusion-default.json', 'r', encoding='utf-8').read())
    t = threading.Thread(target=redraw_photo, args=[object_list, book_name, sd_config])
    t.daemon = True
    t.start()
    return success_data({}, "开始重绘，请稍后")


@router.get("/book/class", response_model=List[BookClassType])
async def book_class(db: SessionLocal = Depends(get_db)):
    book_class = db.query(
        Book.id,
        Book.name,
    ).all()
    return book_class


@router.get("/book/prompt_tags", response_model=List[PromptTagsType])
async def prompt_tags_list(book_id: Optional[int] = None, db: SessionLocal = Depends(get_db)):
    if book_id:
        prompt_tags_list = db.query(
            PromptTags.id,
            PromptTags.book_id,
            PromptTags.content,
            PromptTags.prompt,
            PromptTags.negative,
            Book.name,
        ).outerjoin(Book, PromptTags.book_id == Book.id).filter(PromptTags.book_id == book_id).all()
    else:
        prompt_tags_list = db.query(
            PromptTags.id,
            PromptTags.book_id,
            PromptTags.content,
            PromptTags.prompt,
            PromptTags.negative,
            Book.name,
        ).outerjoin(Book, PromptTags.book_id == Book.id).all()
    return prompt_tags_list


@router.post("/book/prompt_tags")
async def prompt_tags_create(prompt_tags: PromptTagsCreateType, db: SessionLocal = Depends(get_db)):
    model = prompt_tags.model_dump()
    model["prompt"] = model["prompt"].replace("，", ',')
    model["negative"] = model["negative"].replace("，", ',')

    stmt = insert(PromptTags).values(**model)
    db.execute(stmt)
    db.commit()
    return success_data({}, "创建成功")


@router.put("/book/prompt_tags/{id}")
async def prompt_tags_update(id, prompt_tags: PromptTagsType, db: SessionLocal = Depends(get_db)):
    model = prompt_tags.model_dump()
    del model['name']
    stmt = update(PromptTags).where(PromptTags.id == id).values(**model)
    db.execute(stmt)
    db.commit()
    return success_data({}, "修改成功")


@router.delete("/book/prompt_tags")
async def prompt_tags_delete(prompt_tags: VoiceDownload, db: SessionLocal = Depends(get_db)):
    stmt = delete(PromptTags).where(PromptTags.id.in_(prompt_tags.id_list))
    db.execute(stmt)
    db.commit()
    return success_data({}, "删除成功")


@router.get("/stable-diffusion")
async def stable_diffusion_list(db: SessionLocal = Depends(get_db)):
    stable_diffusion = db.query(StableDiffusionConfig).first()
    if stable_diffusion:
        stable_diffusion = stable_diffusion.config_json
    else:
        stable_diffusion = json.loads(open('stable-diffusion-default.json', 'r', encoding='utf-8').read())
    return success_data(stable_diffusion, "获取成功")


@router.post("/stable-diffusion")
async def stable_diffusion_reset(db: SessionLocal = Depends(get_db)):
    stable_diffusion = db.query(StableDiffusionConfig).first()
    if stable_diffusion:
        stable_diffusion.config_json = json.loads(open('stable-diffusion-default.json', 'r', encoding='utf-8').read())
        db.commit()
    return success_data({}, "重置成功")


@router.put("/stable-diffusion")
async def stable_diffusion_update(request: Request, db: SessionLocal = Depends(get_db)):
    data = await request.body()
    text = data.decode('utf-8')
    obj = json.loads(text)
    stable_diffusion = db.query(StableDiffusionConfig).first()
    if stable_diffusion:
        stmt = update(StableDiffusionConfig).where(StableDiffusionConfig.id == stable_diffusion.id).values(
            config_json=obj)
    else:
        stmt = insert(StableDiffusionConfig).values(config_json=obj)
    db.execute(stmt)
    db.commit()
    return success_data({}, "修改成功")
