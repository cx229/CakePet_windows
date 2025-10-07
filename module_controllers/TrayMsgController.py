import random
from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer, QSize, QPoint
from PyQt5.QtWidgets import QLabel

from configs import config
from module_controllers.ModuleController import ModuleController
import sys
import win32gui
import win32con
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QSize

from resmeta.tray_msg_meta import TrayMsgMeta
from utils.log_util import logger
from resmeta.tray_msg_meta import TragMsgs, TrayMsgMeta, tray_msgs_cls_standard

"""
托盘消息控制器:
1. 在托盘左侧显示消息
"""

if TYPE_CHECKING:
    from FollowAndDragWidget import FollowAndDragWidget


class TrayMsgController(ModuleController):
    def __init__(self, widget: 'FollowAndDragWidget'):
        super().__init__()
        self.widget = widget
        self.trag_msg: TrayMsgMeta = TragMsgs.Default.DEFAULT.value
        self.label_size = QSize(1000, 24)
        self.text_label = self.get_init_label()

        self.update_pos_timer = QTimer(self.widget)  # 更新位置定时器，用于定时更新标签位置
        self.update_pos_interval = 250
        self.update_pos_timer.timeout.connect(self.update_position)

        self.change_text_timer = QTimer(self.widget)  # 改变文本定时器，用于定时改变标签文本
        self.change_text_interval_fun = lambda: random.randint(1000, 3000)
        self.change_text_timer.timeout.connect(self.change_text_discontinuous)

        config.tray_msg_enabled_changed.connect(self._on_tray_msg_enabled_changed)  # 监听托盘消息功能切换
        config.tray_msg_mode_tray_changed.connect(self._on_tray_msg_mode_tray_changed)  # 监听托盘消息显示模式切换
        config.tray_msg_color_white_changed.connect(self._on_tray_msg_color_white_changed)  # 监听托盘消息颜色切换
        config.tray_msg_margin_changed.connect(self._on_tray_msg_margin_changed)  # 监听托盘消息边距切换

        if config.tray_msg_enabled:
            self.start()

    def start(self):
        self.update_pos_timer.start(self.update_pos_interval)
        self.change_text_timer.start(self.change_text_interval_fun())
        self.text_label.show()

    def stop(self):
        self.update_pos_timer.stop()
        self.change_text_timer.stop()
        self.text_label.hide()

    def get_style(self,color= "white",margin_left= "0px",margin_right= "0px"):
        """获取托盘消息样式"""
        return f"""
                    QLabel {{
                        font-size: 20px;
                        padding: 2px 8px;
                        font-family: "Microsoft YaHei";
                        color: {color};
                        margin-left: {margin_left};
                        margin-right: {margin_right};
                    }}
                """
    def _on_tray_msg_enabled_changed(self, sender, value):
        """处理托盘消息功能切换"""
        if value:
            self.start()
        else:
            self.stop()

    def _on_tray_msg_mode_tray_changed(self, sender, value):
        """处理托盘消息显示模式切换"""
        self.update_position()

    def _on_tray_msg_color_white_changed(self, sender, value):
        """处理托盘消息颜色切换"""
        if value:
            color = "white"
        else:
            color = "black"
        # self.text_label.setStyleSheet(f"QLabel {{ color: {color}; }}")
        # self.text_label.setProperty("color", color)
        # self.text_label.style().unpolish(self.text_label)  # 强制刷新样式
        # self.text_label.style().polish(self.text_label)
        # current_style = self.text_label.styleSheet()
        style= self.get_style(color=color)

        # # 移除旧的 color 设置（如果有）
        # import re
        # current_style = re.sub(r"color:\s*[^;]+;", "", current_style)
        #
        # # 添加新的 color
        # new_style = f"QLabel {{ {current_style} color: {color}; }}"
        # print(new_style)
        self.text_label.setStyleSheet(style)
        self.text_label.style().unpolish(self.text_label)  # 强制刷新样式
        self.text_label.style().polish(self.text_label)


    def _on_tray_msg_margin_changed(self, sender, value):
        """处理托盘消息外边距切换（仅修改左右边距）"""
        # self.text_label.setProperty("margin-left", f"{value}px")
        # self.text_label.setProperty("margin-right", f"{value}px")
        # self.text_label.style().unpolish(self.text_label)  # 强制刷新样式
        # self.text_label.style().polish(self.text_label)

        # self.text_label.setStyleSheet(f"QLabel {{ padding-left: {value}px; padding-right: {value}px; }}")
        style = self.get_style(margin_left=f"{value}px", margin_right=f"{value}px")
        self.text_label.setStyleSheet(style)
        self.text_label.style().unpolish(self.text_label)  # 强制刷新样式
        self.text_label.style().polish(self.text_label)

    def get_init_label(self) -> QLabel:
        """获取初始化的标签"""
        label = QLabel(self.widget)
        label.lower()
        label.setMinimumSize(self.label_size)
        label.setStyleSheet(self.get_style())
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setText("芝麻酥")

        return label

    def get_taskbar_info(self):
        """获取任务栏和托盘区域信息"""
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if not taskbar_hwnd:
            return None, None, None

        tray_hwnd = win32gui.FindWindowEx(taskbar_hwnd, 0, "TrayNotifyWnd", None)
        if not tray_hwnd:
            return taskbar_hwnd, None, None

        taskbar_rect = win32gui.GetWindowRect(taskbar_hwnd)  # 任务栏矩形区域,[left, top, right, bottom]
        tray_rect = win32gui.GetWindowRect(tray_hwnd)  # 托盘矩形区域,[left, top, right, bottom]

        return taskbar_hwnd, taskbar_rect, tray_rect

    def calculate_position(self, taskbar_rect, tray_rect):
        """计算窗口应该放置的位置"""
        if config.tray_msg_mode_tray:
            x = tray_rect[0] - self.text_label.width() - 5  # 左侧预留5像素
            self.text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            taskbar_height = taskbar_rect[3] - taskbar_rect[1]  # 任务栏高度
            y = taskbar_rect[1] + (taskbar_height - self.text_label.height()) // 2  # 垂直居中
        else: # 非托盘模式,在任务栏左侧显示
            x = taskbar_rect[0] + 5  # 左侧预留5像素
            self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            taskbar_height = taskbar_rect[3] - taskbar_rect[1]  # 任务栏高度
            y = taskbar_rect[1] + (taskbar_height - self.text_label.height()) // 2  # 垂直居中
        # print(f"calculate_position, x: {x}, y: {y}")
        return x, y

    def get_target_position(self):
        """获取托盘消息窗口的目标位置"""
        taskbar_hwnd, taskbar_rect, tray_rect = self.get_taskbar_info()
        # print(f"get_target_position, taskbar_hwnd: {taskbar_hwnd}, taskbar_rect: {taskbar_rect}, tray_rect: {tray_rect}")

        if taskbar_hwnd and tray_rect:
            return self.calculate_position(taskbar_rect, tray_rect)
        return None

    def update_position(self):
        """更新托盘消息窗口的位置"""
        target_pos = self.get_target_position()
        if target_pos:
            combined_pos = QPoint(*target_pos) - self.widget.geometry().topLeft()  # 计算标签的位置, 托盘消息窗口的位置 = 目标位置 - 托盘消息窗口的左上角位置
            self.text_label.move(combined_pos)
            # self.widget.move(*target_pos)

    def change_text_discontinuous(self, force: bool = False):
        """
        间断性的改变文本，期间会显示默认文本
        一般用于：1.定时切换，2.消息的退出
        """
        if self.trag_msg.key == TragMsgs.Default.DEFAULT.value.key:
            self.change_text(force=force)
        else:
            self.change_text(tray_msg=TragMsgs.Default.DEFAULT.value, force=force)

    def change_text(self, tray_msg: TrayMsgMeta = None,
                    tray_msgs: list[TrayMsgMeta] = None,
                    tray_msgs_cls: list[TrayMsgMeta] = None,
                    duration: int = None, force: bool = False):
        """改变托盘消息窗口的文本"""
        if not tray_msg:  # 如果没有指定消息，从列表中随机选择一个
            if not tray_msgs:  # 如果没有指定消息列表，从类中获取
                if not tray_msgs_cls:  # 如果没有指定消息类列表，使用标准类
                    tray_msgs_cls = tray_msgs_cls_standard
                tray_msgs = [i.value for i in tray_msgs_cls]
            tray_msg = random.choice(tray_msgs)

        if force or tray_msg.priority >= self.trag_msg.priority:  # 强制改变或优先级更高或相等
            self.trag_msg = tray_msg
            self.text_label.setText(self.trag_msg.text)
            if duration is None:  # 没有指定持续时间时，使用消息的持续时间
                duration = self.trag_msg.duration
            if duration == 0:  # 持续时间为0时，停止定时器
                self.change_text_timer.stop()
            else:
                self.change_text_timer.start(duration)
            logger.info(f"托盘消息, text: {self.trag_msg.text}, duration: {duration}")

    @property
    def rect(self):
        """获取托盘消息窗口的矩形区域"""
        return self.text_label.geometry()
