import random
from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer
from blinker import Signal

# import signals
from modes.SitMode import SitMode
from modes.DragMode import DragMode
from modes.WalkMode import WalkMode
from utils.log_util import logger
from configs import config

if TYPE_CHECKING:
    from main import FollowAndDragWidget

modes = {}


def register_mode(widget: 'FollowAndDragWidget'):
    """注册模式"""
    modes_class = [SitMode,
                   DragMode,
                   # WalkMode,
                   ]
    modes.update({mode.NAME: mode(widget) for mode in modes_class})


class ChangeModeTimer:
    """切换模式定时器"""

    def __init__(self, widget: 'FollowAndDragWidget', change_interval=10000, change_prob=0.5):
        self.widget = widget
        self.timer = QTimer(self.widget)
        self.timer.timeout.connect(self._change_mode)
        self.timer.start(change_interval)  # 定时切换
        self.change_prob = change_prob

    def _change_mode(self):
        """切换模式"""
        if not self.widget.dragging and random.random() < self.change_prob:
            # 随机切换到其他模式
            available_modes = [name for name in modes.keys() if name != config.mode_name]
            if available_modes:
                new_mode = random.choice(available_modes)
                config.mode_name = new_mode


class ModeManager:
    """模式管理器"""

    def __init__(self, widget: 'FollowAndDragWidget'):
        self.widget = widget
        register_mode(widget)
        self.change_mode_timer = ChangeModeTimer(widget)
        # self.mode_dispatcher = ModeDispatcher(widget)

    @config.mode_name_changed.connect
    def _handle_switch(self, sender, mode_name):
        """处理模式切换信号"""
        cur_mode = modes.get(config.mode_name, None)
        if cur_mode:
            cur_mode.stop()
        if mode_name in modes:
            self._current_mode = modes[mode_name]
            self._current_mode.start()
            logger.info(f"切换到模式: {mode_name}")
        else:
            raise ValueError(f"未知模式: {mode_name}")

    # def get_current_mode(self):
    #     """获取当前模式"""
    #     if self.mode_dispatcher._current_mode:
    #         return self.mode_dispatcher._current_mode.NAME
    #     return None
