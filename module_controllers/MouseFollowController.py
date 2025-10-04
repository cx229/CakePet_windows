import datetime
from typing import TYPE_CHECKING

from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

if TYPE_CHECKING:
    from FollowAndDragWidget import FollowAndDragWidget
from monitors.ScreenMonitor import get_cur_work_bottom
from module_controllers.ModuleController import ModuleController

import image_modes
import math
import traceback
from PyQt5.QtCore import Qt, QPoint, QTimer, QPointF

from utils.log_util import logger
from configs import config


class MouseFollowController(ModuleController):
    """
    1. 拖拽： 可开关
        1.1 长按鼠标左键，开始拖拽跟随主体
        1.2 拖拽动画
    2. 抛掷： 可开关
        2.1 拖拽结束后，主体受初速度和重力影响，抛物线
        2.2 抛掷动画
    3. 跟随： 可开关
        4.1 跟随：
            4.1.1 降落稳定后，主体跟随鼠标移动，按住Ctrl时停止跟随
            4.1.2 非位移待机动作
        4.2 非跟随：
            4.2.1 全待机动作
    """

    def __init__(self, widget: 'FollowAndDragWidget'):
        super().__init__()
        self.widget = widget
        self.update_follow_timer = QTimer(widget)
        self.update_follow_timer.timeout.connect(self.follow_update)

        self.drag_cnt = 0  # 拖拽解释起，拖拽状态，但是未监听到拖拽事件，计数器减少，为0时，拖拽结束
        self.drag_cnt_init = 10  # 拖拽计数器初始值
        self.drag_img_offset = QPoint()  # 拖动偏移量,相对图片左上角的偏移量
        self.drag_move_offset = QPoint()  # 移动位移量
        self.drag_move_offset_last = QPoint()  # 上一次的移动位移量
        self.drag_follow_start_time = None  # 拖拽跟随开始时间
        self.throw_follow_start_time = None  # 抛掷跟随开始时间
        self.mouse_follow_start_time = None  # 跟随开始时间

        self.bind_events()

    def start(self):
        self.update_follow_timer.start(config.follow_update_interval)  # 每多少毫秒更新一次

    def throw_begin(self):
        def cal_throw_speed():
            move_offset = (self.drag_move_offset + self.drag_move_offset_last) / 2
            move_offset = QPointF(move_offset.x() * config.throw_follow_radio.x(), move_offset.y() * config.throw_follow_radio.y())
            offset = QPointF(move_offset)

            # X轴速度处理 - 使用平滑的中间集中函数
            def normalize_x(x):
                # 使用反正切函数使x值集中在中间范围
                return math.atan(x / 60) * 100 * 0.3

            # Y轴速度处理 - 小值放大，大值缩小
            def normalize_y(y):
                c = 50  # 饱和点，越小则大值缩小越明显
                abs_y = abs(y)
                sign = 1 if y >= 0 else -1
                return sign * (abs_y / (1 + abs_y / c))

            x_speed = normalize_x(offset.x())
            y_speed = normalize_y(offset.y())
            return QPointF(x_speed, y_speed)

        # 不论是否是重新抛掷，都需要删除上一次的余数
        if hasattr(self, '_remainder_throw'):  # 检查对象是否已有该属性
            del self._remainder_throw  # 删除对象变量
        # if  config.is_drag_follow:
        #     self.drag_move_offset = QPoint()  # 移动位移量
        #     self.drag_move_offset_last = QPoint()  # 上一次的移动位移量

        config.is_throw_follow = True
        config.throw_follow_speed = cal_throw_speed()
        self.throw_follow_start_time = datetime.datetime.now()
        logger.info(f"抛掷跟随开始，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f})")
        self.widget.mode_manager.set_mode(image_modes.ThrowFollowMode.name())  # 切换到抛掷模式

    def throw_end(self):
        config.is_throw_follow = False
        duration = (datetime.datetime.now() - self.throw_follow_start_time).total_seconds()
        logger.info(f"抛掷跟随结束，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f}),持续时间: {duration:.2f}秒")

        self.widget.mode_manager.change_next_mode()  # 切换到抛掷模式

    def func_throw(self):
        """ 抛掷动画函数 """

        def cal_new_pos_offset():
            if not hasattr(self, '_remainder_throw'):  # 检查对象是否已有该属性
                self._remainder_throw = QPointF(0, 0)  # 动态创建对象变量

            def cal_throw_speed_f(throw_speed_f):
                # 计算当前速度的绝对值
                throw_acceleration = config.throw_follow_acceleration * config.follow_update_interval  # 重力加速度
                throw_speed_f.setY(throw_speed_f.y() + throw_acceleration.y())
                return throw_speed_f

            config.throw_follow_speed = cal_throw_speed_f(config.throw_follow_speed)
            offset_f = config.throw_follow_speed + self._remainder_throw  # 计算新位置, 加上未移动的量
            self._remainder_throw = offset_f - QPointF(offset_f.toPoint())  # 转换回 QPointF 并取小数部分
            return QPoint(offset_f.toPoint())  # 转换回 QPoint

        cur_work_bottom = get_cur_work_bottom(config.anchor_pos, self.widget.screen_monitor)
        # print(f"config.anchor_pos.y():{config.anchor_pos.y()}, cur_work_bottom:{cur_work_bottom}")
        if config.anchor_pos.y() < cur_work_bottom:  # 未拖动
            offset = cal_new_pos_offset()  # 计算偏移量，根据锚点计算
            self.widget.img_move_by_offset(offset)  # 移动图片
        elif config.anchor_pos.y() > cur_work_bottom:  # 在任务栏下
            # 修正位置，防止超出工作区域
            cur_work_bottom = get_cur_work_bottom(config.anchor_pos, self.widget.screen_monitor)
            offset = QPoint(0, cur_work_bottom - config.anchor_pos.y())  # 计算偏移量，根据锚点计算
            self.widget.img_move_by_offset(offset)  # 移动图片
        else:
            self.throw_end()

    def check_mouse_begin(self):
        if not config.is_mouse_follow:
            self.mouse_follow_start_time = datetime.datetime.now()  # 记录跟随开始时间
            config.is_mouse_follow = True
            logger.info(f"开始跟随鼠标移动, 锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f})")

    def check_mouse_end(self):
        """ 跟随鼠标移动结束 """
        if config.is_mouse_follow:
            config.is_mouse_follow = False
            duration = (datetime.datetime.now() - self.mouse_follow_start_time).total_seconds()
            logger.info(f"跟随鼠标移动结束，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f}),持续时间: {duration:.2f}秒")
            self.widget.mode_manager.change_next_mode()

    def func_mouse(self):
        """
        跟随动画函数
        """

        def cal_new_pos_offset(now_pos, tar_pos):
            """计算新位置（逐步靠近鼠标）"""
            if not hasattr(self, '_remainder_mouse'):  # 检查对象是否已有该属性
                self._remainder_mouse = QPointF(0, 0)  # 动态创建对象变量

            cur_now_f, tar_pos_f = QPointF(now_pos) + self._remainder_mouse, QPointF(tar_pos)  # QPointF 加上未移动的量,目标位置
            distance_f = math.hypot(tar_pos_f.x() - cur_now_f.x(), tar_pos_f.y() - cur_now_f.y())  # 计算目标位置到当前位置的距离

            follow_speed = config.mouse_follow_speed * config.follow_update_interval / 8
            smoothing_factor = 50
            speed_factor = 1 - math.exp(-distance_f / smoothing_factor)
            new_pos_f = cur_now_f + (tar_pos_f - cur_now_f) * (follow_speed * speed_factor / distance_f)

            # 创建属于这个对象的，未移动的量。增加这一次的移动量，移动（整数部分）作为返回值，并且更新 未移动量（小数部分）
            self._remainder_mouse = new_pos_f - QPointF(new_pos_f.toPoint())  # 转换回 QPointF 并取小数部分
            new_pos = QPoint(new_pos_f.toPoint())  # 转换回 QPoint
            return new_pos - now_pos

        if not config.key_ctrl_l_only:
            mouse_pos = self.widget.mapFromGlobal(QCursor.pos())  # 相对图片左上角，鼠标坐标
            cur_pos = config.anchor_pos
            target_pos = config.standard_anchor_pos * config.size_ratio_base + QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)  # 目标位置是鼠标位置
            distance = math.hypot(target_pos.x() - cur_pos.x(), target_pos.y() - cur_pos.y())  # 计算目标位置到当前位置的距离

            threshold = 0 if config.is_mouse_follow else 80  # 跟随状态下，阈值为0，否则为10

            if round(distance) > threshold:
                self.check_mouse_begin()
                if distance > 300:
                    self.widget.mode_manager.set_mode(image_modes.MouseFollowMode.name())  # 切换到走模式
                offset = cal_new_pos_offset(cur_pos, target_pos)
                self.widget.img_move_by_offset(offset)
            else:
                self.check_mouse_end()
        else:
            self.check_mouse_end()

    def func_drag(self):
        """
        拖动跟随函数
        """
        # 如果当前窗口不是主窗口
        active_window = QApplication.activeWindow()

        if active_window != self.widget:
            config.is_drag_follow = False

    def check_fall(self):
        """
        检查是否掉落
        """
        if config.anchor_pos.y() != get_cur_work_bottom(config.anchor_pos, self.widget.screen_monitor):
            self.throw_begin()

    def follow_update(self):
        """
        定时器更新函数，用于更新宠物的位置
        """
        try:
            if config.is_drag_follow:  # 拖动时，且拖拽计数器大于0
                self.func_drag()
            elif config.throw_follow_enabled and config.is_throw_follow:  # is_throw_follow 为 True 时，执行抛掷跟随（拖动结束时开，拖拽结束关）
                self.func_throw()
            elif config.mouse_follow_enabled:  # is_throw_follow无论是否，都执行跟随鼠标
                self.func_mouse()
            elif config.throw_follow_enabled:
                self.check_fall()

        except Exception as e:
            logger.error(f"抛掷跟随更新事件异常: {e}")
            traceback.print_exc()

    def bind_events(self):
        self.widget.mousePressEvent = self.mousePressEvent  # 绑定鼠标按下事件
        self.widget.mouseReleaseEvent = self.mouseReleaseEvent  # 绑定鼠标松开事件
        self.widget.mouseMoveEvent = self.mouseMoveEvent  # 绑定鼠标移动事件

    def mousePressEvent(self, event):
        """处理鼠标按下事件，开始拖动图片"""
        try:
            if event.button() == Qt.LeftButton and config.drag_follow_enabled:  # 开始拖动
                self.widget.mode_manager.set_mode(image_modes.DragFollowMode.name())  # 切换到拖动模式
                config.is_drag_follow = True
                self.drag_img_offset = QPoint(QPoint(self.widget.image_label.width() // 2, 0))

                new_pos = event.pos() - self.drag_img_offset
                now_pos = self.widget.image_label.pos()
                # 记录上一次的移动位移量
                self.drag_move_offset_last = QPoint()
                self.drag_move_offset = new_pos - now_pos
                self.widget.img_move_by_offset(self.drag_move_offset)  # 拖动图片
                self.drag_follow_start_time = datetime.datetime.now()  # 记录跟随开始时间
                self.drag_cnt = self.drag_cnt_init  # 拖拽计数器重置
                logger.info(f"用户开始拖动图片，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f})")


        except Exception as e:
            logger.error(f"鼠标按下事件错误: {traceback.format_exc()}")

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，拖动图片"""
        try:
            if config.is_drag_follow and config.drag_follow_enabled:  # 拖动状态下移动窗口
                new_pos = event.pos() - self.drag_img_offset
                now_pos = self.widget.image_label.pos()
                # 记录上一次的移动位移量
                self.drag_move_offset_last = self.drag_move_offset
                self.drag_move_offset = new_pos - now_pos
                self.widget.img_move_by_offset(self.drag_move_offset)  # 拖动图片
                self.drag_cnt = self.drag_cnt_init  # 拖拽计数器重置
        except Exception as e:
            logger.error(f"鼠标移动事件错误: {traceback.format_exc()}")

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，结束拖动图片"""
        try:
            if event.button() == Qt.LeftButton and config.is_drag_follow:  # 结束拖动
                self.widget.mode_manager.change_next_mode()  # 切换到下一个模式
                config.is_drag_follow = False
                duration = datetime.datetime.now() - self.drag_follow_start_time  # 计算拖动时间
                logger.info(f"用户结束拖动图片，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f})， 拖动时间: {duration}")
                self.drag_cnt = 0  # 拖拽计数器归零
                if config.throw_follow_enabled:
                    self.throw_begin()  # 检查是否开始跟随,如果是,则开始跟随
        except Exception as e:
            logger.error(f"鼠标释放事件错误: {traceback.format_exc()}")
