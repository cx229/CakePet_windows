from typing import Dict, Optional, TYPE_CHECKING

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QWidget

from configs import config

if TYPE_CHECKING:
    from FollowAndDragWidget import FollowAndDragWidget
from image_modes.ChangeNextMode import  TimerNextChange
from resmeta.imagemeta import ImageMeta
from utils.img_uttil import load_img
from utils.log_util import logger



class ImagesMode(TimerNextChange):
    """
    多图片模式
    图片循环播放
    定时切换下一个模式
    """

    class ImageConf:
        def __init__(self, img_meta: ImageMeta, next, duration):
            self.img: QPixmap = load_img(img_meta.path)
            self.img_meta = img_meta
            self.next = next
            self.duration = duration

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.widget: 'FollowAndDragWidget' = widget
        self.confs: Dict[int, ImagesMode.ImageConf] = {}
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
                duration = conf.duration() if callable(conf.duration) else conf.duration
                self.image_series_timer.start(duration)
            else:  # 没有设置时间间隔，停止定时器
                self.image_series_timer.stop()
        else:
            logger.error(f"索引 {self.index} 不在配置中")

    def update_widget_image(self, next_conf):
        if next_conf.img_meta:
            self.widget.set_image(next_conf.img, next_conf.img_meta)


class FollowTransImagesMode(ImagesMode):
    """多图片模式，跟随鼠标是否需要镜像"""

    def update_widget_image(self, next_conf):
        """运动的情况，根据鼠标位置判断是否需要镜像"""
        transform_flag = False
        img = next_conf.img
        if config.is_mouse_follow:
            mouse_img_pos = self.widget.image_label.mapFromGlobal(QCursor.pos())
            if mouse_img_pos.x() > self.widget.image_label.width() // 2:
                transform_flag = True
        self.widget.set_image(img, next_conf.img_meta, transform_flag)



