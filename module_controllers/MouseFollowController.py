import datetime
from typing import TYPE_CHECKING

from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QApplication
from fontTools.ttLib.tables.otTables import splitPairPos

if TYPE_CHECKING:
    from FollowAndDragWidget import FollowAndDragWidget
from monitors.ScreenMonitor import get_cur_screen_work_bottom, get_cur_work_by_xy_f, get_cur_screen_work
from module_controllers.ModuleController import ModuleController

import image_modes
from resmeta.tray_msg_meta import TragMsgs, TrayMsgMeta
import math
import traceback
from PyQt5.QtCore import Qt, QPoint, QTimer, QPointF, QRect
from configs import config

from utils.log_util import logger

from utils import speed_util, pos_util


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
        # 拖拽跟随的未移动的量
        self.drag_cnt = 0  # 拖拽解释起，拖拽状态，但是未监听到拖拽事件，计数器减少，为0时，拖拽结束
        self.drag_cnt_init = 10  # 拖拽计数器初始值
        self.drag_img_offset = QPoint()  # 拖动偏移量,相对图片左上角的偏移量
        self.drag_move_offset = QPoint()  # 移动位移量
        self.drag_move_offset_last = QPoint()  # 上一次的移动位移量
        self.drag_follow_start_time = None  # 拖拽跟随开始时间
        # 抛掷跟随的未移动的量
        self._remainder_throw = QPointF(0, 0)  # 动态创建对象变量
        self.throw_follow_start_time = None  # 抛掷跟随开始时间
        self.throw_start_pos = QPoint()  # 抛掷开始位置,记录抛掷开始时的鼠标位置
        self.throw_highest_pos = QPoint()  # 抛掷最高位置
        self.throw_sum_offset = QPoint()  # 抛掷总位移量
        # 跟随鼠标的未移动的量
        self._remainder_mouse = QPointF(0, 0)  # 动态创建对象变量
        self.mouse_follow_start_time = None  # 跟随开始时间

        self.bind_events()

    def start(self):
        self.update_follow_timer.start(config.follow_update_interval)  # 每多少毫秒更新一次

    def drag_begin(self, event: QMouseEvent):
        try:
            # 开始拖动
            self.widget.mode_manager.set_mode(image_modes.DragFollowMode.get_name())  # 切换到拖动模式
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
            self.widget.tray_msg_controller.change_text(tray_msg=TragMsgs.Meow.MIAO1.value, duration=0)

        except Exception as e:
            logger.error(f"拖动开始异常: {traceback.format_exc()}")

    def drag_end(self, event: QMouseEvent):
        try:
            self.widget.mode_manager.change_next_mode()  # 切换到下一个模式
            config.is_drag_follow = False
            duration = datetime.datetime.now() - self.drag_follow_start_time  # 计算拖动时间
            logger.info(f"用户结束拖动图片，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f})， 拖动时间: {duration}")
            self.drag_cnt = 0  # 拖拽计数器归零
            if config.throw_follow_enabled:
                self.throw_begin()  # 检查是否开始跟随,如果是,则开始跟随
            else:
                self.widget.tray_msg_controller.change_text_discontinuous()

        except Exception as e:
            logger.error(f"拖动结束异常: {traceback.format_exc()}")

    def drag_func(self, event: QMouseEvent):
        try:
            new_pos = event.pos() - self.drag_img_offset
            now_pos = self.widget.image_label.pos()
            # 记录上一次的移动位移量
            self.drag_move_offset_last = self.drag_move_offset
            self.drag_move_offset = new_pos - now_pos
            # 根据移动量判断 drag的具体序号
            drag_offset = (self.drag_move_offset_last + self.drag_move_offset) / 2
            mode = self.widget.mode_manager.get_current_mode()
            if isinstance(mode, image_modes.DragFollowMode):
                index = None
                if drag_offset.x() <= -10:
                    index = 6
                elif drag_offset.x() <= -5:
                    index = 4
                elif drag_offset.x() >= 10:
                    index = 5
                elif drag_offset.x() >= 5:
                    index = 3
                if index is not None:
                    mode.update_image_series(index)
            self.widget.img_move_by_offset(self.drag_move_offset)  # 拖动图片
            self.drag_cnt = self.drag_cnt_init  # 拖拽计数器重置
        except Exception as e:
            logger.error(f"拖动过程异常: {traceback.format_exc()}")

    def throw_begin(self):
        # 不论是否是重新抛掷，都需要删除上一次的余数
        self._remainder_throw = QPointF(0, 0)  # 动态创建对象变量
        config.is_throw_follow = True
        move_offset = (self.drag_move_offset + self.drag_move_offset_last) / 2
        config.throw_follow_speed = speed_util.cal_throw_speed(move_offset)
        self.throw_start_pos = QPoint(config.anchor_pos)  # 抛掷开始位置,记录抛掷开始时的鼠标位置
        self.throw_highest_pos = QPoint(config.anchor_pos)  # 记录抛掷最高位置,初始化当前位置
        self.throw_sum_offset = QPoint()  # 抛掷总位移量
        self.throw_follow_start_time = datetime.datetime.now()
        logger.info(f"抛掷跟随开始，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f})")
        self.widget.mode_manager.set_mode(image_modes.ThrowFollowMode.get_name())  # 切换到抛掷模式
        self.widget.tray_msg_controller.change_text(tray_msg=TragMsgs.Meow.MIAO2.value, duration=0)

    def throw_end(self):
        config.is_throw_follow = False
        duration = (datetime.datetime.now() - self.throw_follow_start_time).total_seconds()
        logger.info(f"抛掷跟随结束，锚点坐标: ({config.anchor_pos.x():.2f},{config.anchor_pos.y():.2f}),持续时间: {duration:.2f}秒，"
                    f"开始位置: {pos_util.point_to_tuple(self.throw_start_pos)}, 最高位置: {pos_util.point_to_tuple(self.throw_highest_pos)}, 总位移量: {pos_util.point_to_tuple(self.throw_sum_offset)}")
        self.widget.mode_manager.change_next_mode()  # 切换到抛掷模式
        # 反弹模式，计算并显示抛掷距离
        if config.throw_follow_rebound_enabled:
            move_distance = int(math.hypot(self.throw_sum_offset.x(), self.throw_sum_offset.y()))
            self.widget.tray_msg_controller.change_text(tray_msg=TrayMsgMeta(key="throw_distance", text=f"弹弹弹: {move_distance:,} 像素", base_ms=5000))
        # 非反弹模式，计算并显示抛掷高度
        else:
            height = self.throw_start_pos.y() - self.throw_highest_pos.y()
            if height > 0:
                self.widget.tray_msg_controller.change_text(tray_msg=TrayMsgMeta(key="throw_highest", text=f"抛高高: {height:,} 像素", base_ms=5000))
            else:
                self.widget.tray_msg_controller.change_text_discontinuous()
        self.drag_move_offset = QPoint()  # 移动位移量
        self.drag_move_offset_last = QPoint()  # 上一次的移动位移量

    def throw_func(self):
        """ 抛掷动画函数 """
        anchor_pos = config.anchor_pos
        cur_work_bottom = get_cur_screen_work_bottom(anchor_pos, self.widget.screen_monitor)
        # print(f"anchor_pos.y():{anchor_pos.y()}, cur_work_bottom:{cur_work_bottom}")
        # 在工作区域内
        if anchor_pos.y() < cur_work_bottom:
            offset, self._remainder_throw = speed_util.cal_throw_offset(self._remainder_throw)  # 计算偏移量，根据锚点计算
            # 如果开启了反弹碰撞
            if config.throw_follow_rebound_enabled:
                offset, self._remainder_throw = speed_util.cal_throw_rebound_offset(anchor_pos, offset, self._remainder_throw, self.widget.screen_monitor)  # 计算反弹偏移量
            # 修正偏移量，防止超出工作区域底部
            if anchor_pos.y() + offset.y() > cur_work_bottom:
                offset.setY(cur_work_bottom - anchor_pos.y())  # 修正偏移量，防止超出工作区域
            self.widget.img_move_by_offset(offset)  # 移动图片
            self.throw_sum_offset += QPoint(abs(offset.x()), abs(offset.y()))  # 记录抛掷总位移量,需要修改为绝对值
            # print(f"当前位置: ({utils.pos_util.point_to_tuple(config.anchor_pos)}), 偏移量: ({utils.pos_util.point_to_tuple(offset)}), 抛掷最高位置: ({utils.pos_util.point_to_tuple(self.throw_highest_pos)}), 抛掷总位移量: ({utils.pos_util.point_to_tuple(self.throw_sum_offset)})")
            if anchor_pos.y() < self.throw_highest_pos.y():  # 记录抛掷最高位置，需要取y最小值时更新
                self.throw_highest_pos = QPoint(anchor_pos)  # 更新抛掷最高位置
        # 超出工作区域
        elif anchor_pos.y() > cur_work_bottom:
            config.throw_follow_speed = QPointF(0, 0)  # 速度重置为0
            offset = QPoint(0, cur_work_bottom - anchor_pos.y())  # 计算偏移量，根据锚点计算
            self.widget.img_move_by_offset(offset)  # 移动图片
        # 地面反弹
        elif config.throw_follow_rebound_enabled and config.throw_follow_speed != QPointF(0, 0):
            offset, self._remainder_throw = speed_util.cal_throw_offset(self._remainder_throw)  # 计算偏移量，根据锚点计算
            offset, self._remainder_throw = speed_util.cal_throw_rebound_offset(anchor_pos, offset, self._remainder_throw, self.widget.screen_monitor)  # 反弹，修正位移量，速度衰减
            speed = speed_util.adjust_speed_to_zero(config.throw_follow_speed)
            if offset == QPoint(0, 0) and speed == QPointF(0, 0):  # 反弹后速度为0，停止移动
                config.throw_follow_speed = QPointF(0, 0)  # 速度重置为0
                self.throw_end()  # 抛掷结束
            else:
                self.widget.img_move_by_offset(offset)  # 移动图片
        else:
            self.throw_end()  # 抛掷结束

    def check_mouse_begin(self):
        if not config.is_mouse_follow:  # 如果正在跟随，那么无需处理
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

    def mouse_func(self):
        """ 跟随动画函数 """
        if not config.key_ctrl_l_only:
            mouse_pos = self.widget.mapFromGlobal(QCursor.pos())  # 相对图片左上角，鼠标坐标
            cur_pos = config.anchor_pos
            target_pos = config.standard_anchor_pos * config.size_ratio_base + QPoint(mouse_pos.x() + 10, mouse_pos.y() + 10)  # 目标位置是鼠标位置
            distance = math.hypot(target_pos.x() - cur_pos.x(), target_pos.y() - cur_pos.y())  # 计算目标位置到当前位置的距离
            threshold = 0 if config.is_mouse_follow else 80  # 跟随状态下，阈值为0，否则为10

            # print(f"distance: {distance:.2f}, threshold: {threshold:.2f}")
            if round(distance) > threshold:
                self.check_mouse_begin()
                if distance > 300:
                    self.widget.mode_manager.set_mode(image_modes.MouseFollowMode.get_name())  # 切换到走模式
                offset, self._remainder_mouse = speed_util.cal_mouse_offset(cur_pos, target_pos, self._remainder_mouse)
                self.widget.img_move_by_offset(offset)
            else:
                self.check_mouse_end()
        else:
            self.check_mouse_end()

    def drag_check_need_end(self):
        """ 检查是否需要结束拖动跟随 """
        # 如果当前窗口不是主窗口
        active_window = QApplication.activeWindow()
        if active_window != self.widget:
            config.is_drag_follow = False

    def fall_check_need_begin(self):
        """ 检查是否需要开始跟随 """
        cur_work_bottom = get_cur_screen_work_bottom(config.anchor_pos, self.widget.screen_monitor)
        # print(f"config.anchor_pos.y():{config.anchor_pos.y()},cur_work_bottom:{cur_work_bottom},{config.anchor_pos.y() != cur_work_bottom}")
        if config.anchor_pos.y() != cur_work_bottom and config.gravity_enable:
            self.throw_begin()

    def adjust_bottom_check(self):
        """ 检查是否需要调整底部位置 """
        anchor_pos = config.anchor_pos
        cur_work_bottom = get_cur_screen_work_bottom(anchor_pos, self.widget.screen_monitor)
        if anchor_pos.y() > cur_work_bottom:  # 在任务栏下，修正位置，防止超出工作区域
            offset = QPoint(0, cur_work_bottom - config.anchor_pos.y())  # 计算偏移量，根据锚点计算
            self.widget.img_move_by_offset(offset)  # 移动图片

    def follow_update(self):
        """ 定时器更新函数，用于更新宠物的位置 """
        try:
            if config.is_drag_follow:  # 拖动时，且拖拽计数器大于0
                self.drag_check_need_end()  # 检查是否需要结束拖动跟随
            # 处理 抛掷跟随（因为抛掷 是 外部启动）
            elif  config.is_throw_follow:
                if config.throw_follow_enabled:
                    self.throw_func()    # 处理 抛掷跟随
                else: # 抛掷功能关闭，但是正在抛掷，那么结束抛掷
                    self.throw_end()
            # 处理 跟随鼠标（因为跟随鼠标 是 内部启动）
            elif config.mouse_follow_enabled:
                self.mouse_func()  # 处理 跟随鼠标
            elif config.is_mouse_follow: # 鼠标跟随关闭，但是正在跟随鼠标，那么结束跟随
                self.check_mouse_end()
            # 默认 处理 重力抛掷
            elif config.throw_follow_enabled:
                self.fall_check_need_begin()  # 检查是否需要开始跟随


        except Exception as e:
            logger.error(f"抛掷跟随更新事件异常: {e}")
            traceback.print_exc()

    def bind_events(self):
        self.widget.mousePressEvent = self.mousePressEvent  # 绑定鼠标按下事件
        self.widget.mouseReleaseEvent = self.mouseReleaseEvent  # 绑定鼠标松开事件
        self.widget.mouseMoveEvent = self.mouseMoveEvent  # 绑定鼠标移动事件

    def mousePressEvent(self, event: QMouseEvent):
        """处理鼠标按下事件，开始拖动图片"""
        if event.button() == Qt.LeftButton and config.drag_follow_enabled:
            self.drag_begin(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """处理鼠标移动事件，拖动图片"""
        if config.is_drag_follow and config.drag_follow_enabled:  # 拖动状态下移动窗口
            self.drag_func(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """处理鼠标释放事件，结束拖动图片"""
        if event.button() == Qt.LeftButton and config.is_drag_follow:  # 结束拖动
            self.drag_end(event)
