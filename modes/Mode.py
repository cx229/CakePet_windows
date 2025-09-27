from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer

from utils.log_util import logger

if TYPE_CHECKING:
    from main import FollowAndDragWidget


class Mode:
    NAME = "base"
    def __init__(self,widget:'FollowAndDragWidget',confs:dict):
        self.widget=widget

        self.confs = confs
        self.index = 1
        self.image_series_timer = QTimer(self.widget)  # 图片系列变化定时器
        self.image_series_timer.timeout.connect(self.update_image_series)

        self.update_image_series()

    def start(self):
        self.index = 1
        self.update_image_series()

    def stop(self):
        self.image_series_timer.stop()

    def update_image_series(self):
        conf = self.confs[self.index]
        self.update_widget_image(conf["img"])
        if conf["next"]: # 有下一张图片
            self.image_series_timer.start(conf["duration"])
            self.index = conf["next"]


    def update_widget_image(self,img):
        self.widget.set_image(img)

