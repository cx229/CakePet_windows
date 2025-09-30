from typing import Dict, Optional

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from image_modes.ChangeNextMode import NextChangeMode, TimerNextChange
from image_modes.ImageMode import ImageMode
from resmeta.imagemeta import ImageMeta
from utils.img_uttil import load_img
from utils.log_util import logger


class MultiImageMode(TimerNextChange):
    """多图片模式"""

    class ImageConf:
        def __init__(self, img_meta: ImageMeta, next, duration):
            self.img: QPixmap = load_img(img_meta.path)
            self.anchor = img_meta.anchor_pixel
            self.next = next
            self.duration = duration

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs: Dict[int, MultiImageMode.ImageConf] = {}
        self.index = 1
        self.image_series_timer = QTimer(self.widget)  # 图片系列变化定时器
        self.image_series_timer.timeout.connect(self.update_image_series)

    def start(self):
        super().start()
        self.index = 1
        self.update_image_series()

    def restart(self):
        super().restart()
        self.index = 1
        self.update_image_series()

    def stop(self):
        super().stop()
        self.image_series_timer.stop()

    def update_image_series(self):
        if self.index in self.confs:
            conf = self.confs[self.index]
            self.update_widget_image(conf)
            if conf.next:
                self.index = conf.next
            else:  # 没有下一张图片，切换到下一个模式
                self.change_mode()
            if conf.duration:
                self.image_series_timer.start(conf.duration)
            else:  # 没有设置时间间隔，停止定时器
                self.image_series_timer.stop()
        else:
            logger.error(f"索引 {self.index} 不在配置中")

    def update_widget_image(self, next_conf):

        # self.widget.set_image(next_conf.img)
        if next_conf:
            self.widget.set_image(next_conf.img,next_conf.anchor)
    # def next_mode(self):
    #     """返回下一个模式"""
    #     current_mode = self.__class__
    #     import random
    #     from image_modes import modes_standby
    #     available_modes = [name for name in modes_standby if name != current_mode]  # 排除当前模式
    #     return random.choice(available_modes)  # 随机选择下一个模式
