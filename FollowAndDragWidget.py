import traceback
from typing import Optional

from PyQt5.QtWidgets import (QLabel, QWidget)
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
from PyQt5.QtGui import QPixmap, QTransform, QCursor

from module_controllers.ClickThroughController import ClickThroughController
from module_controllers.TrayMsgController import TrayMsgController
from monitors.KeyMonitor import KeyMonitor
from monitors.ScreenMonitor import ScreenMonitor
from image_modes.ModeManager import ModeManager
from module_controllers.MouseFollowController import MouseFollowController
from resmeta.image_meta import ImageMeta
from settings import create_tray
from utils.log_util import logger, on_logger_only_error_changed
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
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 鼠标穿透

            # # 鼠标交互相关变量
            # self.drag_offset = QPoint()  # 拖动偏移量

            # 加载主图片
            # self.size_ratio = 1
            self.pixmap: Optional[QPixmap] = None  # 当前图片
            self.img_meta: Optional[ImageMeta] = None  # 当前图片的元数据
            self.transform_flag = False

            self.image_label = QLabel(self)
            self.image_label.setAlignment(Qt.AlignCenter)  # 内容据中
            self.image_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 鼠标穿透

            # self.image_label.setStyleSheet("background-color: red;")  # 红色背景 # DEV

            self.screen_monitor = ScreenMonitor(self)  # 屏幕监控器
            self.setGeometry(self.screen_monitor.combined_rect)  # 获取所有显示器的虚拟大桌面区域, 设置窗口覆盖所有显示器
            self.screen_monitor.workarea_changed.connect(self._on_workarea_changed)

            self.mode_manager = ModeManager(self)
            self.key_monitor = KeyMonitor()

            self.follow_controller = MouseFollowController(self)
            self.click_through_controller = ClickThroughController(self)  # 点击穿透控制器
            self.size_growing_controller = SizeGrowingController(self)  # 大小增长控制器
            self.tray, self.tray_menu = create_tray(self)  # 创建系统托盘图标
            self.tray_msg_controller = TrayMsgController(self)  # 托盘消息控制器

            self.start()
            logger.info("程序启动成功")

        except Exception as e:
            logger.error(f"FollowAndDragWidget初始化错误: {traceback.format_exc()}")
            raise

    def start(self):
        self.key_monitor.start()  # 启动键盘监听线程
        self.mode_manager.set_init_mode()  # 设置初始模式
        self.size_growing_controller.start()  # 启动大小增长控制器，开始计时
        self.follow_controller.start()  # 启动鼠标跟随控制器，开始跟随鼠标
        self.click_through_controller.start()  # 启动点击穿透控制器，开始设置窗口点击穿透
        # self.tray_msg_controller.start()  # 启动托盘消息控制器，开始显示消息
        self.key_monitor.connect_tray_msg_controller(self, self.tray_msg_controller)  # 连接托盘消息控制器

    def get_cursor_pos(self) -> QPointF:
        """获取当前鼠标位置，相对窗口坐标"""
        return QPointF(QCursor.pos() - self.pos())

    def get_img_rect(self) -> QRect:
        """获取当前图片位置，相对窗口坐标"""
        return QRect(self.image_label.pos(), self.image_label.size())

    def _on_workarea_changed(self):
        """处理工作区域变化"""
        self.setGeometry(self.screen_monitor.combined_rect)  # 更新窗口位置和大小
        logger.info(f"工作区域变化, 新联合窗口位置和大小: {self.geometry()}")

    def set_image(self, pixmap=None, img_meta: ImageMeta = None, transform_flag: bool = None, offset: QPoint = None):
        """设置主图片"""
        pixmap = self.pixmap = pixmap or self.pixmap  # 如果没有提供新的pixmap，使用历史记录
        # print(f"anchor,{img_meta.anchor if img_meta else None}.{self.img_meta.anchor if self.img_meta else None}")

        img_meta = self.img_meta = img_meta or self.img_meta  # 如果没有提供新的img_meta，使用历史记录
        transform_flag = self.transform_flag = transform_flag if transform_flag is not None else self.transform_flag  # 如果没有提供新的transform_flag，使用历史记录
        offset = QPoint(offset) if offset else QPoint(0, 0)
        if not pixmap or not img_meta:
            return

        image_anchor = img_meta.anchor
        image_size_r = img_meta.size_r  # 图片大小比例,有的图片是1：128*128，有的是10：1280*1280, 等比例缩放
        cur_size_r = config.size_ratio * config.size_ratio_base / image_size_r  # 表示当前的 最终比列

        scaled_pixmap = pixmap.scaled(
            pixmap.size() * cur_size_r,
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation
        )
        scaled_anchor = QPoint(round(image_anchor.x() * cur_size_r), round(image_anchor.y() * cur_size_r))

        if transform_flag:
            scaled_pixmap = scaled_pixmap.transformed(QTransform().scale(-1, 1))  # 水平翻转
            scaled_anchor = QPoint(scaled_pixmap.width() - scaled_anchor.x(), scaled_anchor.y())
            offset.setX(-offset.x())  # 水平翻转后，x轴偏移量取相反数

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())  # 调整图片标签大小为缩放后的图片大小

        # print(f"offset:{offset},offset*2.526:{offset*2.526}")
        origin_offset = offset * cur_size_r
        new_offset = self.screen_monitor.adjust_offset_screen(origin_offset, config.anchor_pos) \
            if (config.is_drag_follow or config.is_throw_follow or  not config.mouse_follow_enabled) else origin_offset
        # print(f"new_offset4: {new_offset},origin_offset: {origin_offset}")

        config.anchor_pos += new_offset

        new_pos = config.anchor_pos - scaled_anchor
        # print(f"设置图片: {img_meta.path}, 大小比例: {self.size_ratio}, 锚点: {scaled_anchor}, 偏移量: {new_offset}, offset: {offset}")

        self.image_label.move(new_pos)

    def img_move_by_offset(self, offset: QPoint):
        """根据偏移量移动图片,同时更新锚点坐标"""
        new_offset = self.screen_monitor.adjust_offset_screen(offset, config.anchor_pos) \
            if (config.is_drag_follow or config.is_throw_follow or  not config.mouse_follow_enabled) else offset
        self.image_label.move(self.image_label.pos() + new_offset)
        config.anchor_pos += new_offset

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
