import time
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

    def __init__(self, widget: QWidget, change_time=10, next_time=10 * 1000):
        self.widget: 'FollowAndDragWidget' = widget

        self.size_ratio = 1  # 放大初始大小比例
        self.change_time = change_time  # 改变时间
        self.change_step = 0.01  # 改变大小步长
        self.next_time = next_time  # 下一次等待时间

        self.wait_timer = QTimer(self.widget)
        self.wait_start_time = None
        self.wait_timer.timeout.connect(self._bigger_start)

        self.change_timer = QTimer(self.widget)
        self.change_timer.timeout.connect(self._bigger_change)

        config.bigger_flag_changed.connect(self._handle_bigger_flag_value)  # 绑定关闭
        config.bigger_enabled_changed.connect(self._handle_bigger_flag_value)  # 绑定开启
        # config.standard_size_ratio_changed.connect(self.re_size)  # 绑定标准大小比例改变

    def start(self):
        super().start()
        self._wait_start()

    def stop(self):
        super().stop()
        self.wait_timer.stop()
        self.change_timer.stop()

    # 获取已经等待的时间
    def get_wait_elapsed_time(self):
        if self.wait_start_time is None:
            return 0
        return (time.time() - self.wait_start_time) * 1000  # 转换为毫秒

    def _wait_start(self):
        self._re_size()
        self.wait_start_time = time.time()  # 记录当前时间戳
        self.wait_timer.start(config.bigger_wait_time)  # 重新开始等待时间
        logger.info(f"开始等待放大时间，等待时间{config.bigger_wait_time / 1000}秒")

    def _bigger_start(self):
        config.bigger_flag = True
        logger.info(f"放大时间到，开始改变大小, 放大间隔{self.change_time / 1000}秒")

    def _bigger_change(self):
        self._update_size()

    def _handle_bigger_enable_value(self, sender, value):
        if value:
            self.wait_timer.start(config.bigger_wait_time)  # 重新开始等待时间
        else:
            self.wait_timer.stop()  # 关闭等待时间
            self.change_timer.stop()  # 关闭改变时间
            self._set_img_size_ratio(self.size_ratio)  # 恢复标准大小比例

    def _handle_bigger_flag_value(self, sender, value):
        if value:
            self.wait_timer.stop()  # 关闭等待时间
            self.change_timer.start(self.change_time)  # 开启改变时间
        else:
            self.change_timer.stop()  # 关闭改变时间
            self._wait_start()  # 开启等待时间，等待下一次放大

    def _re_size(self):
        if self.size_ratio != 1:
            self.size_ratio = 1
            self._set_img_size_ratio(self.size_ratio)
            self.widget.set_image()

    def _update_size(self):
        """更新窗口大小"""
        if self.size_ratio < config.bigger_max_size_ratio:
            self.size_ratio += self.change_step
            self._set_img_size_ratio(self.size_ratio)
            self.widget.set_image()

    def _set_img_size_ratio(self, size_ratio: float):
        config.size_ratio = size_ratio
