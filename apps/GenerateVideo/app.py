#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2023/08/01 14:45
# @file:app.py
import os
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips
import numpy as np

from admin.models import SwitchType
from config import file_path, project_path


class Main:
    def merge_video(self, picture_path_list: list, audio_path_list: list, name: str, config=None, is_web=False):
        """
        :param picture_path_list: 图片路径列表
        :param audio_path_list: 音频路径列表
        :return:
        """
        if is_web:
            picture_path_list = [str(project_path) + i for i in picture_path_list]
            audio_path_list = [str(project_path) + i for i in audio_path_list]
        clips = []
        for index, value in enumerate(picture_path_list):
            audio_clip = AudioFileClip(audio_path_list[index])
            img_clip = ImageSequenceClip([picture_path_list[index]], audio_clip.duration)
            if config:
                if config.video_type == SwitchType.fades_and_out:
                    if index != 0 and index != len(picture_path_list):
                        img_clip = img_clip.set_position(('center', 'center')).set_duration(audio_clip.duration).fadeout(
                            0.1).fadein(0.1)
                    else:
                        img_clip = img_clip.set_position(('center', 'center')).set_duration(audio_clip.duration)
                elif config.video_type == SwitchType.up:
                    img_clip = img_clip.set_position(('center', 'center')).fl(self.fl_up, apply_to=['mask']).set_duration(
                        audio_clip.duration)
                else:
                    img_clip = img_clip.set_position(('center', 'center')).set_duration(audio_clip.duration)
            else:
                img_clip = img_clip.set_position(('center', 'center')).set_duration(audio_clip.duration)
            clip = img_clip.set_audio(audio_clip)
            clips.append(clip)
            print(f"-----------生成第{index}段视频-----------")
        print(f"-----------开始合成视频-----------")
        final_clip = concatenate_videoclips(clips)
        if is_web:
            name = name.rsplit(".", 1)[0]
            path = os.path.join(file_path, name)
            video_path = os.path.join(path, "video")
            if not os.path.isdir(video_path):
                os.mkdir(video_path)
            video_path = os.path.join(video_path, name + ".mp4")
        else:
            new_parent = os.path.join(file_path, "video")
            if not os.path.exists(new_parent):
                os.makedirs(new_parent)
            video_path = os.path.join(new_parent, name + ".mp4")
        final_clip.write_videofile(video_path, fps=24, audio_codec="aac")
        return video_path.replace(str(project_path), '')

    def fl_up(self, gf, t):
        # 获取原始图像帧
        frame = gf(t)

        # 进行滚动效果，将图像向下滚动50像素
        height, width = frame.shape[:2]
        scroll_y = int(t * 10)  # 根据时间t计算滚动的像素数
        new_frame = np.zeros_like(frame)

        # 控制滚动的范围，避免滚动超出图像的边界
        if scroll_y < height:
            new_frame[:height - scroll_y, :] = frame[scroll_y:, :]

        return new_frame


if __name__ == '__main__':
    m = Main()
    picture_path_list = [
        "/Users/anning/PycharmProjects/fastApiProject/media/picture/0.png",
        "/Users/anning/PycharmProjects/fastApiProject/media/picture/1.png",
        "/Users/anning/PycharmProjects/fastApiProject/media/picture/2.png",
        "/Users/anning/PycharmProjects/fastApiProject/media/picture/3.png"]
    audio_path_list = [
        "/Users/anning/PycharmProjects/fastApiProject/SDK/Baidu/Voice/audio/0.wav",
        "/Users/anning/PycharmProjects/fastApiProject/SDK/Baidu/Voice/audio/1.wav",
        "/Users/anning/PycharmProjects/fastApiProject/SDK/Baidu/Voice/audio/2.wav"]
    name = "可乐"
    m.merge_video(picture_path_list, audio_path_list, name)
