import random
import sys
import math
import traceback
import datetime
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon, QCursor

import modes
from configs import Config
from modes import ModeManager
from tray import create_tray
from utils.log_util import logger
from utils.exce_util import handle_exception
from configs import Config, config

from KeyMonitor import keyboard, key_monitor


def xx(yy, xxx):
    res = yy * xxx
    print(f"xx({yy},{xxx})={res}")
    return res


class FollowAndDragWidget(QWidget):
    def __init__(self):
        """
        初始化跟随和拖动功能的主窗口
        配置信息位于configs.py"""
        try:
            super().__init__()

            # 跟随状态跟踪
            self.follow_start_time = None  # 跟随开始时间
            self.last_follow_time = None  # 上一次跟随时间
            self.is_following = False  # 是否正在跟随鼠标

            # 设置窗口属性
            self.setWindowFlags(
                Qt.FramelessWindowHint  # 无边框
                | Qt.WindowStaysOnTopHint  # 始终在最前
                | Qt.Tool  # 不显示在任务栏
            )
            self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景

            # 鼠标交互相关变量
            self.dragging = False  # 是否正在拖动
            self.drag_offset = QPoint()  # 拖动偏移量

            # 加载主图片
            self.size_r=1
            self.pixmap=None
            self.image=None
            self.init_image_mode()
            screen_geometry = QApplication.desktop().screenGeometry()
            self.move(screen_geometry.center()
                      - self.rect().center())  # 初始位置：屏幕中央

            # 设置定时器用于跟随鼠标
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.follow_mouse)
            self.timer.start(config.follow_update_interval)  # 每多少毫秒更新一次

            # self.timer_size = QTimer(self)
            # self.timer_size.timeout.connect(self.update_size)
            # self.timer_size.start(10)  # 每多少毫秒更新一次


            self.tray, self.tray_menu = create_tray(self)  # 创建系统托盘图标

            logger.info("程序启动成功")

        except Exception as e:
            logger.error(f"FollowAndDragWidget初始化错误: {traceback.format_exc()}")
            raise



    def init_image_mode(self):
        """初始化主图片标签"""
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.mode_manager = ModeManager(self)
        # modes.random_change_mode() # 随机切换模式
        # modes.set_mode(modes.SitMode.SitMode.NAME)
        modes.set_mode(modes.PatHeadMode.PatHeadMode.NAME)

    def update_size(self):
        """更新窗口大小"""
        if self.size_r<15:
            self.size_r+=0.01
            self.set_image()

    def set_image(self, pixmap=None):
        # """设置主图片"""
        if pixmap is not None:
            self.pixmap = pixmap
        else:
            pixmap = self.pixmap
        if pixmap is None:
            return
        self.image = pixmap.toImage()  # 转换为QImage以获取像素信息
        # self.image_label.setPixmap(pixmap)  # 设置图片到标签
        # self.resize(pixmap.size())  # 调整窗口大小为图片大小

        scaled_pixmap = pixmap.scaled(
            pixmap.size() * self.size_r,
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())  # 调整图片标签大小为缩放后的图片大小
        self.resize(scaled_pixmap.size())  # 调整窗口大小为缩放后的图片大小

    def contextMenuEvent(self, event):
        """重写右键菜单事件"""
        try:

            if self.tray_menu:
                self.tray_menu.exec_(event.globalPos())
                logger.info("用户右键点击窗口弹出菜单")
        except Exception as e:
            logger.error(f"显示右键菜单错误: {traceback.format_exc()}")

    def is_mouse_on_content(self, pos):
        """
        检查鼠标是否在图片的非透明区域
        pos: 鼠标位置，相对于窗口左上角坐标
        """
        # 将坐标转换为图片坐标系
        img_pos = self.image_label.mapFromParent(pos)

        # 检查坐标是否在图片范围内
        if 0 <= img_pos.x() < self.image.width() and 0 <= img_pos.y() < self.image.height():
            # 获取像素的alpha值
            alpha = self.image.pixelColor(img_pos).alpha()
            return alpha > 0  # alpha>0表示有内容

        return False

    def is_mouse_nearby_content(self, pos, threshold=10):
        """
        检查鼠标是否在图片内容区域附近
        pos: 鼠标位置，相对于窗口左上角坐标
        threshold: 阈值，单位为像素，距离图片中心区域的距离
        """
        # 将坐标转换为图片坐标系
        img_pos = self.image_label.mapFromParent(pos)
        # 半径是是图片的半斜对角线+threshold
        target_radius = math.hypot(self.image.width(), self.image.height()) / 2 + threshold
        distance = math.hypot(img_pos.x() - self.image.width() / 2, img_pos.y() - self.image.height() / 2)
        return distance <= target_radius  # 检查距离是否在半径内

    def follow_mouse(self):
        """
        处理跟随鼠标移动事件
        如果是 仅Ctrl按住，跟随终止
        否则，跟随鼠标移动，但是不靠近鼠标
        """
        try:
            current_time = datetime.datetime.now()  # 当前时间，用于计算持续时间

            def move_over():
                """ 跟随鼠标移动结束 """
                if self.is_following:
                    duration = (current_time - self.follow_start_time).total_seconds()
                    logger.info(f"跟随鼠标移动结束，持续时间: {duration:.2f}秒")
                    self.is_following = False

            if config.follow_enabled and not self.dragging:
                # 检查是否只有 左Ctrl 键被按下,如果是，跟随终止
                is_ctrl = key_monitor.check_key(
                    keyboard.Key.ctrl_l, is_only=True)
                if not is_ctrl:
                    global_mouse_pos = QCursor.pos()  # 获取鼠标在屏幕上的位置
                    mouse_pos = self.mapFromGlobal(global_mouse_pos)  # 将全局坐标转换为相对于窗口左上角的坐标
                    mouse_img_pos = self.image_label.mapFromParent(mouse_pos)

                    threshold = 10
                    target_radius = math.hypot(self.image.width(), self.image.height()) / 2 + threshold  # 目标半径，是图片的半斜对角线+threshold
                    distance = math.hypot(mouse_img_pos.x() - self.image.width() / 2, mouse_img_pos.y() - self.image.height() / 2)  # 计算鼠标到图片中心的距离

                    if distance > target_radius:
                        if not self.is_following:
                            self.follow_start_time = current_time  # 记录跟随开始时间
                            self.is_following = True
                            logger.info("开始跟随鼠标移动")

                        # 计算新位置（逐步靠近鼠标）
                        def cal_new_pos():
                            follow_speed=config.follow_speed*config.follow_update_interval / 8
                            smoothing_factor = 50
                            speed_factor = 1 - math.exp(-distance / smoothing_factor)
                            return self.pos() + mouse_img_pos * ( follow_speed * speed_factor / distance)
                        new_pos = cal_new_pos()

                        self.move(new_pos)

                        self.last_follow_time = current_time
                        return 
            
            move_over() # 未移动，结束跟随


        except Exception as e:
            logger.error(f"跟随鼠标错误: {traceback.format_exc()}")

    def mousePressEvent(self, event):
        """处理鼠标按下事件，开始拖动图片"""
        try:
            if event.button() == Qt.LeftButton and config.drag_enabled:
                # 切换到拖动模式
                modes.set_mode(modes.DragMode.DragMode.NAME)

                # 开始拖动
                self.dragging = True
                # self.drag_offset = event.pos()
                self.drag_offset = QPoint(QPoint(self.width() // 2, 0))
                self.move(event.globalPos() - self.drag_offset)  # 拖动开始，就设置图片

                # logger.info(f"用户开始拖动图片, event.pos={event.pos()}, drag_offset={self.drag_offset}")
        except Exception as e:
            logger.error(f"鼠标按下事件错误: {traceback.format_exc()}")

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，拖动图片"""
        try:
            if self.dragging and config.drag_enabled:
                # 拖动状态下移动窗口
                self.move(event.globalPos() - self.drag_offset)
                # logger.info(f"用户拖动图片, event.globalPos()={event.globalPos()}, drag_offset={self.drag_offset}")
        except Exception as e:
            logger.error(f"鼠标移动事件错误: {traceback.format_exc()}")

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，结束拖动图片"""
        try:
            if event.button() == Qt.LeftButton and self.dragging:
                modes.random_change_mode()  # 随机切换模式

                # 结束拖动
                self.dragging = False
                logger.info("用户结束拖动图片")
        except Exception as e:
            logger.error(f"鼠标释放事件错误: {traceback.format_exc()}")

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


if __name__ == "__main__":
    try:
        # 设置全局异常处理
        sys.excepthook = handle_exception

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # 防止关闭窗口时退出程序

        widget = FollowAndDragWidget()
        widget.show()

        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"程序启动错误: {traceback.format_exc()}")
        sys.exit(1)
