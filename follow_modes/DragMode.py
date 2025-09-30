import image_modes
from follow_modes.FollowMode import FollowMode
from image_modes.ImageMode import ImageMode
import math
import traceback
import datetime
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize, QRect, QPointF
from PyQt5.QtGui import QPixmap, QIcon, QCursor

from utils.log_util import logger
from configs import Config, config

from KeyMonitor import keyboard, key_monitor


class DragMode(FollowMode):
    """跟随鼠标模式"""

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.timer = QTimer(widget)
        self.timer.timeout.connect(self.follow_mouse)
        self.timer.start(config.follow_update_interval)  # 每多少毫秒更新一次

        self.widget.mousePressEvent = self.mousePressEvent
        self.widget.mouseReleaseEvent = self.mouseReleaseEvent
        self.widget.mouseMoveEvent = self.mouseMoveEvent

    def follow_mouse(self):
        """
        处理跟随鼠标移动事件
        如果是 仅Ctrl按住，跟随终止
        否则，跟随鼠标移动，但是不靠近鼠标
        """
        try:
            def check_move_begin():
                if not config.is_following:
                    config.follow_start_time = datetime.datetime.now()  # 记录跟随开始时间
                    config.is_following = True
                    logger.info(f"开始跟随鼠标移动")

            def check_move_over():
                """ 跟随鼠标移动结束 """
                if config.is_following:
                    self.widget.mode_manager.change_next_mode()
                    duration = (datetime.datetime.now() - config.follow_start_time).total_seconds()
                    logger.info(f"跟随鼠标移动结束，持续时间: {duration:.2f}秒")
                    config.is_following = False

            def cal_new_pos(now_pos, tar_pos):
                """计算新位置（逐步靠近鼠标）"""
                if not hasattr(config, '_remainder'):  # 检查对象是否已有该属性
                    config._remainder = QPointF(0, 0)  # 动态创建对象变量

                cur_now_f, tar_pos_f = QPointF(now_pos) + config._remainder, QPointF(tar_pos)  # QPointF 加上未移动的量,目标位置
                distance_f = math.hypot(tar_pos_f.x() - cur_now_f.x(), tar_pos_f.y() - cur_now_f.y())  # 计算目标位置到当前位置的距离

                follow_speed = config.follow_speed * config.follow_update_interval / 8
                smoothing_factor = 50
                speed_factor = 1 - math.exp(-distance_f / smoothing_factor)
                new_pos_f = cur_now_f + (tar_pos_f - cur_now_f) * (follow_speed * speed_factor / distance_f)

                # 创建属于这个对象的，未移动的量。增加这一次的移动量，移动（整数部分）作为返回值，并且更新 未移动量（小数部分）
                config._remainder = new_pos_f - QPointF(new_pos_f.toPoint())  # 转换回 QPointF 并取小数部分
                return QPoint(new_pos_f.toPoint())  # 转换回 QPoint

            def func_move():
                """ 跟随鼠标移动，返回值为是否跟随 """
                if (not config.follow_enabled  # 跟随未启用
                        or config.is_dragging  # 拖动中，不跟随
                        or key_monitor.check_key(keyboard.Key.ctrl_l, is_only=True)):  # 仅Ctrl按下
                    return False  # 未跟随



                mouse_pos = self.widget.mapFromGlobal(QCursor.pos())  # 相对图片左上角，鼠标坐标
                cur_pos = self.widget.image_label.pos()
                target_pos = QPoint(mouse_pos.x() + 30, mouse_pos.y() + 50)  # 目标位置是鼠标位置
                distance = math.hypot(target_pos.x() - cur_pos.x(), target_pos.y() - cur_pos.y())  # 计算目标位置到当前位置的距离

                threshold = 0 if config.is_following else 80  # 跟随状态下，阈值为0，否则为10

                if distance > 300 and  self.widget.mode_manager.get_current_mode_name() != image_modes.WalkMode.name():
                    self.widget.mode_manager.set_mode(image_modes.WalkMode.name())  # 切换到走模式


                if round(distance) > threshold:
                    check_move_begin()
                    new_pos = cal_new_pos(cur_pos, target_pos)
                    self.widget.image_label.move(new_pos)
                    config.last_follow_time = datetime.datetime.now()
                    return True
                return False

            if not func_move():
                check_move_over()  # 未移动，结束跟随


        except Exception as e:
            logger.error(f"跟随鼠标错误: {traceback.format_exc()}")

    def mousePressEvent(self, event):
        """处理鼠标按下事件，开始拖动图片"""
        try:
            if event.button() == Qt.LeftButton and config.drag_enabled:
                self.widget.mode_manager.set_mode(image_modes.LiftUpMode.name())  # 切换到拖动模式
                # 开始拖动
                config.is_dragging = True
                self.widget.drag_offset = QPoint(QPoint(self.widget.image_label.width() // 2, 0))
                self.widget.image_label.move(event.pos() - self.widget.drag_offset)  # 拖动开始，就设置图片

        except Exception as e:
            logger.error(f"鼠标按下事件错误: {traceback.format_exc()}")

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，拖动图片"""
        try:
            if config.is_dragging and config.drag_enabled:
                # 拖动状态下移动窗口
                self.widget.image_label.move(event.pos() - self.widget.drag_offset)
        except Exception as e:
            logger.error(f"鼠标移动事件错误: {traceback.format_exc()}")

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，结束拖动图片"""
        try:
            if event.button() == Qt.LeftButton and config.is_dragging:
                self.widget.mode_manager.change_next_mode()

                # 结束拖动
                config.is_dragging = False
                logger.info("用户结束拖动图片")
        except Exception as e:
            logger.error(f"鼠标释放事件错误: {traceback.format_exc()}")
