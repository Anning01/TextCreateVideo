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
from PIL import Image

import requests
from config import sd_url, file_path, project_path


class Main:
    sd_url = sd_url

    def draw_picture(self, obj_list, book_name: str | None):
        """
        :param obj_list:
        :return: 图片地址列表
        """
        picture_path_list = []
        for index, obj in enumerate(obj_list):
            novel_dict = {
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
                "steps": 50,
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
                html = requests.post(self.sd_url, data=json.dumps(novel_dict))
            except:
                raise ConnectionError("Stable Diffusion 连接失败，请查看ip+端口是否匹配，是否开启。")
            img_response = json.loads(html.text)
            image_bytes = base64.b64decode(img_response['images'][0])
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
