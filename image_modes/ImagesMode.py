from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING, Union, Callable

from Demos.mmapfile_demo import offset
from PyQt5.QtCore import QTimer, QPointF, QPoint
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QWidget

from configs import config

if TYPE_CHECKING:
    from FollowAndDragWidget import FollowAndDragWidget
from image_modes.ChangeNextMode import TimerNextChange
from resmeta.imagemeta import ImageMeta
from utils.img_uttil import load_img
from utils.log_util import logger


class ImagesMode(TimerNextChange):
    """
    多图片模式
    图片循环播放
    定时切换下一个模式
    """

    @dataclass
    class ImageConf:
        img_meta: ImageMeta
        next: Optional['ImageConf'] = None
        duration: Union[int, Callable[[], int]] = 0  # 可以是 int 或返回 int 的 callable
        offset: QPoint = field(default_factory=lambda: QPoint(0, 0))

        def __post_init__(self):
            self.img: QPixmap = load_img(self.img_meta.path)

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.widget: 'FollowAndDragWidget' = widget
        self.confs: Dict[int, ImagesMode.ImageConf] = {}
        self.transform_flag: bool = False

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
        if self.index is None: # 没有下一张图片，切换到下一个模式
            self.change_mode()
        elif self.index in self.confs:
            conf = self.confs[self.index]
            self.update_widget_image(conf)
            self.index = conf.next

            if conf.duration:
                duration = conf.duration() if callable(conf.duration) else conf.duration
                self.image_series_timer.start(duration)
            else:  # 没有设置时间间隔，停止定时器
                self.image_series_timer.stop()
        else:
            logger.error(f"索引 {self.index} 不在配置中")

    def update_widget_image(self, next_conf):
        if next_conf.img_meta:
            if config.is_mouse_follow:
                offset = QPoint(0, 0)
            else:
                offset = next_conf.offset
            self.widget.set_image(next_conf.img, next_conf.img_meta, self.transform_flag, offset)
