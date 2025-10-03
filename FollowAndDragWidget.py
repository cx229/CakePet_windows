import traceback
from typing import Optional

from PyQt5.QtWidgets import (QApplication, QLabel, QWidget)
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QTransform

from ScreenMonitor import ScreenMonitor
from image_modes.ModeManager import ModeManager
from module_controllers.MouseFollowController import MouseFollowController
from resmeta.imagemeta import ImageMeta
from tray import create_tray
from utils.log_util import logger
from configs import config
from module_controllers.SizeGrowingController import SizeGrowingController


class FollowAndDragWidget(QWidget):
    def __init__(self):
        """
        初始化跟随和拖动功能的主窗口
        配置信息位于configs.py"""
        try:
            super().__init__()

            # 设置窗口属性
            self.setWindowFlags(
                Qt.FramelessWindowHint  # 无边框
                | Qt.WindowStaysOnTopHint  # 始终在最前
                | Qt.Tool  # 不显示在任务栏
            )
            self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景

            # 获取所有显示器的虚拟大桌面区域
            self.desktop_rect = self.get_combined_screen_geometry()

            self.setGeometry(self.desktop_rect)  # 设置窗口覆盖所有显示器

            # 鼠标交互相关变量
            self.drag_offset = QPoint()  # 拖动偏移量

            # 加载主图片
            self.size_ratio = 1
            self.pixmap: Optional[QPixmap] = None  # 当前图片
            self.img_meta: Optional[ImageMeta] = None  # 当前图片的元数据
            self.transform_flag = False

            self.image_label = QLabel(self)
            self.image_label.setAlignment(Qt.AlignCenter)  # 内容据中
            # self.image_label.setStyleSheet("background-color: red;")  # 红色背景 # DEV

            self.screen_monitor = ScreenMonitor(self)  # 屏幕监控器
            self.mode_manager = ModeManager(self)
            self.follow_controller = MouseFollowController(self)

            self.size_growing_controller = SizeGrowingController(self)  # 大小增长控制器
            self.tray, self.tray_menu = create_tray(self)  # 创建系统托盘图标

            self.start()
            logger.info("程序启动成功")

        except Exception as e:
            logger.error(f"FollowAndDragWidget初始化错误: {traceback.format_exc()}")
            raise

    def start(self):
        self.mode_manager.set_init_mode()
        self.size_growing_controller.start()
        self.follow_controller.start()

    def get_combined_screen_geometry(self):
        """获取所有显示器的联合矩形区域"""
        rect = QRect()
        for screen in QApplication.screens():
            rect = rect.united(screen.geometry())
        print(f"所有显示器的联合矩形区域: {rect}")  # 所有显示器的联合矩形区域: PyQt5.QtCore.QRect(0, 0, 5120, 1773)
        return rect

    def set_size_ratio(self, size_ratio: float):
        self.size_ratio = size_ratio

    def set_image(self, pixmap=None, img_meta: ImageMeta = None, transform_flag: bool = None):
        """设置主图片"""
        pixmap = self.pixmap = pixmap or self.pixmap  # 如果没有提供新的pixmap，使用历史记录
        img_meta = self.img_meta = img_meta or self.img_meta  # 如果没有提供新的img_meta，使用历史记录
        transform_flag = self.transform_flag = transform_flag if transform_flag is not None else self.transform_flag  # 如果没有提供新的transform_flag，使用历史记录

        if not pixmap or not img_meta:
            return

        image_anchor = img_meta.anchor
        image_size_r = img_meta.size_r
        cur_size_r = self.size_ratio / image_size_r

        scaled_pixmap = pixmap.scaled(
            pixmap.size() * cur_size_r,
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation
        )
        scaled_anchor = QPoint(round(image_anchor.x() * cur_size_r), round(image_anchor.y() * cur_size_r))

        if transform_flag:
            scaled_pixmap = scaled_pixmap.transformed(QTransform().scale(-1, 1))  # 水平翻转
            scaled_anchor = QPoint(scaled_pixmap.width() - scaled_anchor.x(), scaled_anchor.y())

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())  # 调整图片标签大小为缩放后的图片大小


        new_pos = config.anchor_pos - scaled_anchor
        self.image_label.move(new_pos)

    def adjust_offset(self, offset: QPoint, cur_anchor_pos: QPoint):
        """调整偏移量，确保图片不会超出桌面范围"""
        target_anchor_pos = cur_anchor_pos + offset
        left_screen = self.screen_monitor.get_left_screen()
        if target_anchor_pos.x() < left_screen.screen_rect.left():
            offset.setX(left_screen.screen_rect.left() - config.anchor_pos.x())

        right_screen = self.screen_monitor.get_right_screen()
        if target_anchor_pos.x() > right_screen.screen_rect.right():
            offset.setX(right_screen.screen_rect.right() - config.anchor_pos.x())
        return offset

    # def adjust_offset_screen(self, offset: QPoint, cur_anchor_pos: QPoint):
    #     """调整偏移量，如果是超过左边界，则从右边出现，同理超过右边界则从左边出现"""
    def adjust_offset_screen(self, offset: QPoint, cur_anchor_pos: QPoint):
        """调整偏移量，实现循环屏幕效果"""
        target_anchor_pos = cur_anchor_pos + offset

        # 获取左右屏幕信息
        left_screen = self.screen_monitor.get_left_screen()
        right_screen = self.screen_monitor.get_right_screen()

        # 如果移出左边界，从右边界出现
        if target_anchor_pos.x() < left_screen.screen_rect.left():
            overflow = left_screen.screen_rect.left() - target_anchor_pos.x()
            new_x = right_screen.screen_rect.right() - overflow
            offset.setX(new_x - cur_anchor_pos.x())

        # 如果移出右边界，从左边界出现
        elif target_anchor_pos.x() > right_screen.screen_rect.right():
            overflow = target_anchor_pos.x() - right_screen.screen_rect.right()
            new_x = left_screen.screen_rect.left() + overflow
            offset.setX(new_x - cur_anchor_pos.x())

        return offset

    def img_move_by_offset(self, offset: QPoint):
        """根据偏移量移动图片,同时更新锚点坐标"""

        # offset=self.adjust_offset(offset, config.anchor_pos)
        offset = self.adjust_offset_screen(offset, config.anchor_pos)

        self.image_label.move(self.image_label.pos() + offset)
        config.anchor_pos += offset

    def contextMenuEvent(self, event):
        """重写右键菜单事件"""
        try:

            if self.tray_menu:
                self.tray_menu.exec_(event.globalPos())
                logger.info("用户右键点击窗口弹出菜单")
        except Exception as e:
            logger.error(f"显示右键菜单错误: {traceback.format_exc()}")

    def closeEvent(self, event):
        """处理关闭事件，清理资源"""
        try:
            # 清理资源
            self.timer.stop()
            self.tray.hide()
            logger.info("程序正常退出")
            event.accept()
        except Exception as e:
            logger.error(f"关闭事件错误: {traceback.format_exc()}")
            event.accept()
