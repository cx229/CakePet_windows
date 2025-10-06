import random
from typing import Optional

from PyQt5.QtWidgets import QWidget

from configs import config
from image_modes import NextChangeMode, modes_map, ImagesMode
from utils.log_util import logger


class ModeManager:
    """模式管理器"""

    def __init__(self, widget: QWidget):
        self.widget = widget
        self.cur_mode: Optional[ImagesMode] = ImagesMode(self.widget)  # 初始模式
        config.mode_name_changed.connect(self._handle_mode_change)

    def _handle_mode_change(self, sender, value: str):
        """处理模式切换"""
        if value not in modes_map:
            logger.error(f"未知模式: {value}")
            return
        next_mode = modes_map.get(value)(self.widget)
        if self.cur_mode:
            self.cur_mode.stop()
        self.cur_mode = next_mode
        self.cur_mode.start()

    def get_cur_mode(self) -> ImagesMode:
        """获取当前模式"""
        return self.cur_mode

    def get_current_mode_name(self) -> str:
        """获取当前模式名称"""
        return self.cur_mode.get_name()

    def get_current_mode(self) -> Optional[ImagesMode]:
        """获取当前模式"""
        return self.cur_mode

    def set_mode(self, mode_name: str):
        """设置当前模式"""
        if self.get_current_mode_name() != mode_name:
            if mode_name not in modes_map:
                logger.error(f"未知模式: {mode_name}")
                return
            config.mode_name = mode_name

    def change_next_mode(self):
        """切换到下一个模式"""
        if self.cur_mode:
            self.cur_mode.change_mode()

    def set_init_mode(self):
        from image_modes import init_mode_name
        self.set_mode(init_mode_name)
