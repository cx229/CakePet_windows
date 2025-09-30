import random
import sys
import math
import traceback
import datetime

from PIL.ImageChops import offset
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize, QRect, QPointF
from PyQt5.QtGui import QPixmap, QIcon, QCursor, QPainter

import image_modes
from configs import Config
from follow_modes.DragMode import DragMode
from image_modes.ModeManager import ModeManager
from tray import create_tray
from utils.log_util import logger
from utils.exce_util import handle_exception
from configs import Config, config

from KeyMonitor import keyboard, key_monitor


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
            # self.dragging = False  # 是否正在拖动
            self.drag_offset = QPoint()  # 拖动偏移量

            # 加载主图片
            self.size_r = 1
            self.pixmap = None
            self.anchor = None
            # self.cur_size_r = 1
            self.image = None
            self.image_label = QLabel(self)
            self.image_label.setAlignment(Qt.AlignCenter) # 内容据中
            self.image_label.setStyleSheet("background-color: red;")
            self.mode_manager = ModeManager(self)
            # modes.random_change_mode() # 随机切换模式
            # modes.set_mode(modes.SitMode.SitMode.NAME)
            self.mode_manager.set_mode(image_modes.PatHeadMode.name())

            # screen_geometry = QApplication.desktop().screenGeometry()
            # self.move(screen_geometry.center()
            #           - self.rect().center())  # 初始位置：屏幕中央

            # 设置定时器用于跟随鼠标
            # self.timer = QTimer(self)
            # self.timer.timeout.connect(self.follow_mouse)
            # self.timer.start(config.follow_update_interval)  # 每多少毫秒更新一次

            self.timer_size = QTimer(self)
            self.timer_size.timeout.connect(self.update_size)
            self.timer_size.start(50)  # 每多少毫秒更新一次

            self.fllow_mode = DragMode(self)
            self.tray, self.tray_menu = create_tray(self)  # 创建系统托盘图标

            logger.info("程序启动成功")

        except Exception as e:
            logger.error(f"FollowAndDragWidget初始化错误: {traceback.format_exc()}")
            raise

    def get_combined_screen_geometry(self):
        """获取所有显示器的联合矩形区域"""
        rect = QRect()
        for screen in QApplication.screens():
            rect = rect.united(screen.geometry())
        return rect

    def update_size(self):
        """更新窗口大小"""
        if self.size_r < 5:
            self.size_r += 0.01
            self.set_image()

    def set_image(self, pixmap=None, anchor=None):
        # """设置主图片"""
        if pixmap is not None:
            self.pixmap = pixmap
        else:
            pixmap = self.pixmap
        if pixmap is None:
            return

        cur_size_r = self.size_r

        last_image = self.image

        scaled_pixmap = pixmap.scaled(
            pixmap.size() * cur_size_r,
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation
        )
        self.image = scaled_pixmap.toImage()  # 转换为QImage以获取像素信息

        last_anchor = self.anchor
        if anchor is not None:
            cur_anchor = (anchor[0] * cur_size_r, anchor[1] * cur_size_r)
            self.anchor = cur_anchor
        elif last_anchor is not None and last_image is not None:
            cur_anchor= (last_anchor[0]*scaled_pixmap.width()/last_image.width(),last_anchor[1]*scaled_pixmap.height()/last_image.height())
        else:
            cur_anchor = None



        offset_x = 0
        offset_y = 0
        if last_image:
            print(f"last_anchor:{last_anchor[0]:.2f},{last_anchor[1]:.2f},cur_anchor:{cur_anchor[0]:.2f},{cur_anchor[1]:.2f},"
                  f"last_pixmap:{last_image.width():.2f},{last_image.height():.2f}, {scaled_pixmap.width():.2f},{scaled_pixmap.height():.2f}")
        if last_anchor is not None and cur_anchor is not None:
            # 计算锚点偏移量
            offset_x =   last_anchor[0]-cur_anchor[0]
            offset_y =   last_anchor[1]-cur_anchor[1]


        print(f"self.image_label.pos(): {self.image_label.pos()}, offset_x: {offset_x}, offset_y: {offset_y}")

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())  # 调整图片标签大小为缩放后的图片大小
        self.image_label.move(self.image_label.pos() + QPoint(round(offset_x), round(offset_y)))


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
