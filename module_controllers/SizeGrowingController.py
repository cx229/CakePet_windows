from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:
    from FollowAndDragWidget import FollowAndDragWidget
from module_controllers.ModuleController import ModuleController
from configs import config
from utils.log_util import logger


class SizeGrowingController(ModuleController):
    """ 大小增长 控制器"""

    def __init__(self, widget: QWidget, wait_time=15 * 60 * 1000, change_time=10, next_time=10 * 1000):
        self.widget: 'FollowAndDragWidget' = widget

        self.size_ratio = 1  # 初始大小比例
        self.wait_time = wait_time  # 等待时间
        self.change_time = change_time  # 改变时间
        self.change_max_size_ratio = 1.5  # 最大大小比例
        self.change_step = 0.01  # 改变大小步长
        self.next_time = next_time  # 下一次等待时间

        self.wait_timer = QTimer(self.widget)
        self.wait_timer.timeout.connect(self.wait_end)

        self.change_timer = QTimer(self.widget)
        self.change_timer.timeout.connect(self.change)

        config.bigger_flag_changed.connect(self._handle_rest_value)  # 绑定关闭

    def start(self):
        super().start()
        self.wait_start()

    def stop(self):
        super().stop()
        self.wait_timer.stop()
        self.change_timer.stop()

    def wait_start(self):
        self.re_size()
        self.wait_timer.start(self.wait_time)  # 重新开始等待时间
        logger.info(f"开始等待放大时间，等待时间{self.wait_time / 1000}秒")

    def wait_end(self):
        logger.info(f"放大时间到，开始改变大小, 放大间隔{self.change_time / 1000}秒")
        self.wait_timer.stop()
        self.change_timer.start(self.change_time)
        config.bigger_flag = True

    def change(self):
        self.update_size()

    def _handle_rest_value(self, sender, value):
        if not value:
            self.change_timer.stop()
            self.wait_start()

    def re_size(self):
        if self.size_ratio != 1:
            self.size_ratio = 1
            self.widget.set_size_ratio(self.size_ratio)
            self.widget.set_image()

    def update_size(self):
        """更新窗口大小"""
        if self.size_ratio < self.change_max_size_ratio:
            self.size_ratio += self.change_step
            self.widget.set_size_ratio(self.size_ratio)
            self.widget.set_image()
