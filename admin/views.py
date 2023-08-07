#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/04 20:52
# @file:views.py
import asyncio
import os
import _thread
import queue
import threading

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import text, func, delete, update

from admin.databases import SessionLocal
from admin.models import Book, BookSection, BookVoice, BookPictures, StatusEnum
from admin.type_annotation import Config
from config import file_path, project_path, client_id, client_secret, appId, apikey, ForwardKey, sd_url
from apps.TextSiice.app import Main as TMain
from apps.SpeechSynthesis.app import Main as SMain
from apps.PromptWords.app import Main as PMain
from apps.GeneratePictures.app import Main as GPMain
from apps.GenerateVideo.app import Main as GVMain

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


@router.get("/book")
async def book_list(db: SessionLocal = Depends(get_db)):
    query = text("SELECT id, name, path, strftime('%Y-%m-%d %H:%M:%S', create_dt), video_path, status, fail_info FROM book")
    result = db.execute(query)
    res = []
    for i in result:
        # query_v = db.query(BookVideos).filter(BookVideos.book_id == i.t[0])
        # is_video = db.query(query_v.exists()).scalar()
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
async def create_video(id, db: SessionLocal = Depends(get_db)):
    book = db.query(Book).get(id)
    if book:
        path = str(project_path) + book.path
        book.status = StatusEnum.underway
        db.commit()
        t = threading.Thread(target=CreateVideo().thread_func, args=[book, path, db])
        t.start()
        return success_data({}, message="视频生成任务启动成功！")
    return error_data("书不存在！")


class CreateVideo:

    def thread_func(self, book, path, db):
        print("开启队列")
        q = queue.Queue()
        t = threading.Thread(target=my_thread, args=[book, path, db, q])
        print("开始子线程")
        t.start()
        t.join()
        # 修改状态
        if not q.empty():
            error = q.get()
            if error:
                status = StatusEnum.failure
                fail_info = str(error)
            else:
                status = StatusEnum.complete
                fail_info = ''
            book = db.merge(book)
            stmt = update(Book).where(Book.id == book.id).values(fail_info=fail_info, status=status)
            # 执行更新操作
            db.execute(stmt)
            db.commit()

    async def main(self, book, path, db, q):
        """
        启动此方法，异步生成图片，语音，提示词
        :return:
        """
        try:
            # 创建分割任务
            text_list = await self.txt_handle(path)
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
                object_list = await self.create_prompt_words(text_list)
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
                # 生成音频任务
                audio_list = await self.text_to_audio(text_list, book.name)
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
                picture_path_list = await self.create_picture(object_list, book.name)
                picture_model_list = []
                for index, value in enumerate(picture_path_list):
                    picture_model_list.append(BookPictures(
                        book_id=book.id,
                        index=index,
                        path=value
                    ))
                db.add_all(picture_model_list)
                db.commit()
            # 视频任务
            video_path = await self.create_video(picture_path_list, audio_list, book.name)
            book.video_path = video_path
            book.status = StatusEnum.complete
            db.commit()
        except Exception as e:
            q.put(e)

    async def txt_handle(self, path):
        """
        分隔提示符
        :return:
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在，根路名为{path}")
        file = open(path, 'r', encoding='utf-8')
        content = file.read().replace('\n', '')
        t = TMain()
        text_list = await t.txt_long(content.split('。'))
        return await t.txt_short(text_list)

    async def text_to_audio(self, text_list, bookname):
        """
        生成音频
        :return:
        """
        s = SMain()
        audio_list = await s.text_to_audio(text_list, bookname=bookname)
        return audio_list

    async def create_prompt_words(self, text_list, tags=None):
        """
        生成提示词
        :return:
        """
        p = PMain()
        object_list = await p.create_prompt_words(text_list, tags)

        return object_list

    async def create_picture(self, obj_list, book_name):
        """
        生成图片
        :return:
        """
        gp = GPMain()
        return gp.create_picture(obj_list, book_name)

    async def create_video(self, picture_path_list, audio_list, book_name):
        """
        生成视频
        :return:
        """
        gv = GVMain()
        gv_path = gv.merge_video(picture_path_list, audio_list, book_name, is_web=True)
        return gv_path


def my_thread(book, path, db, q):
    asyncio.run(CreateVideo().main(book, path, db, q))


@router.get("/config")
async def config():
    config = Config(
        baidu_api_key=client_id,
        baidu_secret_key=client_secret,
        fastgpt_appid=appId,
        fastgpt_api_key=apikey,
        api2d_forward_key=ForwardKey,
        sd_url=sd_url.replace("http://", "").replace("/sdapi/v1/txt2img", "")
    )
    return success_data(config.model_dump())


@router.post("/config")
async def update_config(config: Config):
    env = os.path.join(project_path, '.env')
    env_text = f"client_id='{config.baidu_api_key}'\nclient_secret='{config.baidu_secret_key}'\napikey='{config.fastgpt_api_key}'\nappId='{config.fastgpt_appid}'\nForwardKey='{config.api2d_forward_key}'\nsd_url='http://{config.sd_url}/sdapi/v1/txt2img'"
    with open(env, 'w') as f:
        f.write(env_text)
    return success_data(config.model_dump(), "更新配置必须重新启动后台！")


# @router.get("/book/section")
# async def section_list(db: SessionLocal = Depends(get_db)):
#     db.query(Book).filter(Book.name == file.filename).first()
#
#     return success_data(config.model_dump(), "更新配置必须重新启动后台！")


@router.get('/test')
async def test(db: SessionLocal = Depends(get_db)):
    book = db.query(Book).get(2)
    path = str(project_path) + book.path
    book.status = StatusEnum.underway
    db.commit()
    t = threading.Thread(target=CreateVideo().thread_func, args=[book, path, db])
    t.start()
    return {"code": 200}
