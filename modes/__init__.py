import random
from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer
from blinker import Signal

# import signals
from modes import SitMode, DragMode, WalkMode, PatHeadMode
from utils.log_util import logger
from configs import config

if TYPE_CHECKING:
    from main import FollowAndDragWidget


mode_list = {}


def register_mode(widget: 'FollowAndDragWidget'):
    """注册模式"""
    modes_class = [SitMode.SitMode,
                   DragMode.DragMode,
                   WalkMode.WalkMode,
                   PatHeadMode.PatHeadMode,
                   ]
    mode_list.update({mode.NAME: mode(widget) for mode in modes_class})

def random_change_mode():
        """随机切换模式"""
        available_modes = [name for name in mode_list.keys() if name != config.mode_name]
        if available_modes:
            new_mode = random.choice(available_modes)
            config.mode_name = new_mode

def set_mode(name: str):
    """设置当前模式"""
    if name in mode_list:
        config.mode_name = name
    else:
        raise ValueError(f"未知模式: {name}")

class ChangeModeTimer:
    def __init__(self, widget: 'FollowAndDragWidget', change_interval=10000, change_prob=0.5):
        self.widget = widget
        self.change_interval = change_interval
        self.change_prob = change_prob
        self._is_internal_change = False  # 新增标记位

        self.timer = QTimer(self.widget)
        self.timer.timeout.connect(self._change_mode)
        self.timer.start(self.change_interval)

        config.mode_name_changed.connect(self._reset_timer_on_external_change)

    def _change_mode(self):
        """定时触发的模式切换"""
        if not self.widget.dragging and random.random() < self.change_prob:
            self._is_internal_change = True  # 标记为内部触发
            print(f"定时切换模式: {config.mode_name}")
            random_change_mode()
            self._is_internal_change = False  # 重置标记

    def _reset_timer_on_external_change(self, sender, value):
        """仅响应外部触发的模式切换"""
        if not self._is_internal_change:  # 忽略内部触发
            self.timer.stop()
            self.timer.start(self.change_interval)

class ModeManager:
    """模式管理器"""
    def __init__(self, widget: 'FollowAndDragWidget'):
        self.widget = widget
        register_mode(widget)
        self.change_mode_timer = ChangeModeTimer(widget)

        self.cur_mode = mode_list.get(config.mode_name, None)
        config.mode_name_changed.connect(self._handle_switch)

    def _handle_switch(self, sender, value):
        """处理模式切换信号"""
        if self.cur_mode:
            self.cur_mode.stop()
        if value in mode_list:
            logger.info(f"切换到模式: {value}")
            self.cur_mode = mode_list[value]
            self.cur_mode.start()
        else:
            raise ValueError(f"未知模式: {value}")


