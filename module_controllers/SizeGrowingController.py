import time
from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

from resmeta.tray_msg_meta import TragMsgs

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
        self.wait_timer.timeout.connect(self._wait_end)

        self.change_timer = QTimer(self.widget)
        self.change_timer.timeout.connect(self._bigger_change)

        config.bigger_flag_changed.connect(self._handle_bigger_flag_value)  # 绑定 放大标志改变
        config.bigger_enabled_changed.connect(self._handle_bigger_enable_value)  # 绑定 放大开启改变

        # 监听放大等待时间改变
        config.bigger_wait_time_changed.connect(self._handle_bigger_wait_time_value)  # 绑定放大等待时间改变

    def start(self):
        super().start()
        self._wait_start()

    def stop(self):
        super().stop()
        self.wait_timer.stop()
        self.change_timer.stop()

    # 获取已经等待的时间
    def get_wait_elapsed_time(self) -> int:
        if self.wait_start_time is None:
            return 0
        return int((time.time() - self.wait_start_time) * 1000)  # 转换为毫秒

    def _wait_start(self):
        self._re_size()
        if not config.bigger_enabled:  # 关闭放大，不处理
            return
        self.wait_start_time = time.time()  # 记录当前时间戳
        self.wait_timer.start(config.bigger_wait_time)  # 重新开始等待时间
        logger.info(f"开始等待放大时间，等待时间{config.bigger_wait_time / 1000}秒")

    def _wait_end(self):
        config.bigger_flag = True  # 开启放大标志,会通过信号触发长处理变大
        logger.info(f"放大时间到，开始改变大小, 放大间隔{self.change_time / 1000}秒, 步长{self.change_step}")

    def _bigger_start(self):
        """ 开启放大（无视放大功能开关） """
        self.wait_timer.stop()  # 关闭等待时间
        self.change_timer.start(self.change_time)  # 开启改变时间
        self.widget.tray_msg_controller.change_text(tray_msg=TragMsgs.Event.REST.value)

    def _bigger_end(self):
        self.change_timer.stop()  # 关闭改变时间
        self._wait_start()  # 开启等待时间，等待下一次放大
        # 退出放大通知
        self.widget.tray_msg_controller.close_text(TragMsgs.Event.REST.value.key)

    def _bigger_change(self):
        self._update_size()

    def _handle_bigger_enable_value(self, sender, value):
        if not value:  # 关闭放大
            self.wait_timer.stop()  # 关闭等待时间
            self.change_timer.stop()  # 关闭改变时间
            self._set_img_size_ratio(1)  # 恢复标准大小比例
            if config.bigger_flag:  # 如果正在放大，
                config.bigger_flag = False  # 关闭放大标志，触发处理

    def _handle_bigger_flag_value(self, sender, value):
        """ 放大标志改变，开启放大或结束放大 """
        if value:  # 开启放大
            self._bigger_start()
        else:  # 放大结束
            self._bigger_end()

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

    def _handle_bigger_wait_time_value(self, sender, value):
        """ 放大等待时间改变，已经到新放大时间，则开始放大。否则修改当前剩余时间，下次等待时间为新时间 """
        if not config.bigger_enabled or config.bigger_flag:  # 关闭放大, 或者正在放大，不处理
            return
        if self.get_wait_elapsed_time() >= value:  # 已经到新放大时间，则开始放大
            self._wait_end()
            logger.info(f"放大等待时间改变，直接开始放大，等待时间{value / 1000}秒, 已经等待时间{self.get_wait_elapsed_time() / 1000}秒")
        else:  # 修改当前剩余时间，下次等待时间为新时间
            self.wait_timer.stop()  # 关闭等待时间
            self.wait_timer.start(value - self.get_wait_elapsed_time())  # 重新开始等待时间
            logger.info(f"放大等待时间改变，修改剩余等待时间，等待时间{value / 1000}秒, 已经等待时间{self.get_wait_elapsed_time() / 1000}秒")
