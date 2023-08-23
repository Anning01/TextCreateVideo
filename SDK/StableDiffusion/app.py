#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 14:30
# @file:app.py
import base64
import json
import os
import io

import aiohttp
from PIL import Image
from tqdm import tqdm

from config import sd_url, file_path, project_path


class Main:
    sd_url = sd_url

    async def draw_picture(self, obj_list, book_name: str | None, sd_config=None):
        """
        :param obj_list:
        :return: 图片地址列表
        """
        picture_path_list = []
        for index, obj in enumerate(tqdm(obj_list, desc='生成图片中', bar_format='{l_bar}{bar}: {n_fmt}/{total_fmt}')):
            if book_name:
                if sd_config:
                    novel_dict = {}
                    for item in sd_config:
                        novel_dict[item['key']] = item['value']
                    novel_dict['prompt'] = f"{obj['prompt']}"
                    del novel_dict['default_prompt']
                else:
                    novel_dict = {
                        # 高分辨率放大，true=启用，false=关闭
                        "enable_hr": "false",
                        # 重绘幅度 0.4
                        "denoising_strength": 0,
                        # 图片宽度
                        "firstphase_width": 960,
                        # 图片高度
                        "firstphase_height": 540,
                        # 图片高分辨率放大倍数
                        "hr_scale": 2,
                        # 高分辨率放大渲染器 R-ESRGAN 4x+ Anime6B
                        "hr_upscaler": "string",
                        # 高分辨率放大迭代次数
                        "hr_second_pass_steps": 0,  # 10
                        # 绘图渲染器
                        "sampler_name": "DPM adaptive",
                        # 绘图数量
                        "batch_size": 1,
                        # 绘图迭代次数
                        "steps": 10,
                        # 引导词关联性
                        "cfg_scale": 7,
                        # 面部修复，true=启用，false=关闭
                        "restore_faces": "false",
                        # 负面提示词
                        "negative_prompt": "badhandv4,ng_deepnegative_v1_64t,worst quality,low quality,normal quality,lowers,monochrome,grayscales,skin spots,acnes,skin blemishes,age spot,6 more fingers on one hand,deformity,bad legs,error legs,bad feet,malformed limbs,extra limbs,ugly,poorly drawn hands,poorly drawn feet,poorly drawn face,text,mutilated,extra fingers,mutated hands,mutation,bad anatomy,cloned face,disfigured,fused fingers",
                        # 正面提示词
                        "prompt": "{}".format(obj["prompt"]),
                }
            else:
                novel_dict = {
                    # 缩写hr代表的就是webui中的"高分辨率修复 (Hires. fix)"，相关的参数对应的是webui中的这些选项：
                    "enable_hr": "false",
                    "denoising_strength": 0,
                    "firstphase_width": 0,
                    "firstphase_height": 0,
                    "hr_scale": 2,
                    "hr_upscaler": "string",
                    "hr_second_pass_steps": 0,
                    "hr_resize_x": 0,
                    "hr_resize_y": 0,
                    "prompt": "{}".format(obj["prompt"]),
                    "styles": [
                        "string"
                    ],
                    "seed": -1,
                    "subseed": -1,
                    "subseed_strength": 0,
                    "seed_resize_from_h": -1,
                    "seed_resize_from_w": -1,
                    "sampler_name": "DPM++ SDE Karras",
                    "batch_size": 1,
                    "n_iter": 1,
                    "steps": 10,
                    "cfg_scale": 7,
                    "width": 1024,
                    "height": 768,
                    "restore_faces": "false",
                    "tiling": "false",
                    "do_not_save_samples": "false",
                    "do_not_save_grid": "false",
                    "negative_prompt": obj["negative"],
                    "eta": 0,
                    "s_churn": 0,
                    "s_tmax": 0,
                    "s_tmin": 0,
                    "s_noise": 1,
                    "override_settings": {},
                    "override_settings_restore_afterwards": "true",
                    "script_args": [],
                    "sampler_index": "DPM++ SDE Karras",
                    "script_name": "",
                    "send_images": "true",
                    "save_images": "true",
                    "alwayson_scripts": {}
                }
            try:
                # 生成图片任务
                # html = requests.post(self.sd_url, data=json.dumps(novel_dict))
                # 替换成异步协程
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.sd_url, json=novel_dict) as response:
                        html = await response.read()
                # html = httpx.post(self.sd_url, json=json.dumps(novel_dict))
            except Exception as e:
                print(e)
                raise ConnectionError("Stable Diffusion 连接失败，请查看ip+端口是否匹配，是否开启。")
            img_response = json.loads(html)
            images = img_response.get("images", None)
            if not images:
                raise Exception(img_response.get("errors", "Stable Diffusion 返回数据异常，请查看ip+端口是否匹配，是否开启。"))
            image_bytes = base64.b64decode(images[0])
            image = Image.open(io.BytesIO(image_bytes))
            # 图片存放
            picture_name = str(obj['index']) + ".png"
            if book_name:
                name = book_name.rsplit(".", 1)[0]
                path = os.path.join(file_path, name)
                picture = os.path.join(path, "picture")
                if not os.path.isdir(picture):
                    os.mkdir(picture)
                picture_path = os.path.join(picture, picture_name)
                image.save(picture_path)
                picture_path_list.append(picture_path.replace(str(project_path), ''))
            else:
                new_path = os.path.join(file_path, 'picture')
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                image_path = os.path.join(new_path, picture_name)
                image.save(image_path)
                picture_path_list.append(image_path)
            print(f"-----------生成第{index}张图片-----------")
        return picture_path_list
