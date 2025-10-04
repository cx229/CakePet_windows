from PyQt5.QtWidgets import QWidget

from configs import config
from module_controllers.ModuleController import ModuleController

import traceback

from configs import config
from utils.log_util import logger
import ctypes

# Windows API常量
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
GWL_EXSTYLE = -20


class ClickThroughController(ModuleController):
    def __init__(self, widget: QWidget):
        super().__init__()
        self.widget = widget
        self.last_enable = None

        config.click_through_enabled_changed.connect(self._handle_click_through_action)
        config.key_ctrl_l_only_changed.connect(self._handle_key_ctrl_l_only_action)

    def start(self):
        self._func_click_through()

    def _func_click_through(self):
        """
        处理使用WinAPI设置穿透模式
        如果Ctrl按下，强制退出穿透模式
        """
        try:
            # 如果Ctrl按下，强制退出穿透模式
            if config.key_ctrl_l_only:
                enabled = False
            else:
                enabled = config.click_through_enabled
            # print(f"ctrl_{config.key_ctrl_l_only} enabled={enabled},"
            #       f"click_through_enabled={config.click_through_enabled},"
            #       f"enable={enabled},"
            #       f"last_enable={self.last_enable}")
            if enabled == self.last_enable:
                return

            logger.info(f"处理，设置窗口点击穿透: {enabled}")
            self.last_enable = enabled
            hwnd = self.widget.winId().__int__()

            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)  # 获取当前窗口样式
            if enabled:  # 开启穿透
                new_style = current_style | WS_EX_LAYERED | WS_EX_TRANSPARENT
            else:  # 关闭穿透
                new_style = current_style & ~WS_EX_TRANSPARENT

            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)  # 应用新样式
            # 刷新窗口
            ctypes.windll.user32.SetWindowPos(
                hwnd, -1, 0, 0, 0, 0,
                0x0001 | 0x0002 | 0x0020  # SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
            )
            self.widget.update()
        except Exception as e:
            logger.error(f"菜单切换点击穿透错误: {traceback.format_exc()}")

    def _handle_click_through_action(self, sender, value):
        """处理点击穿透开关变化"""
        self._func_click_through()

    def _handle_key_ctrl_l_only_action(self, sender, value):
        """处理Ctrl+L键仅开启点击穿透开关变化"""
        self._func_click_through()
