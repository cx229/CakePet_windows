import datetime
import math
import time

import numpy as np
from PyQt5.QtCore import QPointF, QPoint, QRect

from configs import config
from monitors.ScreenMonitor import ScreenMonitor
from utils import pos_util
from utils.log_util import logger
from utils.pos_util import pointf_to_tuple


def adjust_speed_to_zero(speed: QPointF, min_speed: QPointF = QPointF(1, 2)):
    # 调整速度为零
    if abs(speed.x()) < min_speed.x():
        speed.setX(0)
    if abs(speed.y()) < min_speed.y():
        speed.setY(0)
    return speed


def cal_throw_speed(init_move_speed:QPointF):
    """计算抛掷速度"""
    move_speed = QPointF(init_move_speed)

    # X轴速度处理 - 使用平滑的中间集中函数
    def normalize_x(x):
        # 使用反正切函数使x值集中在中间范围
        return math.atan(x / 60) * 100 * 0.3

    # Y轴速度处理 - 小值放大，大值缩小
    # def normalize_y(y):
    #     c = 50  # 饱和点，越小则大值缩小越明显
    #     abs_y = abs(y)
    #     sign = 1 if y >= 0 else -1
    #     return sign * (abs_y / (1 + abs_y / c))
    def normalize_y(x, a=3, b=1.5, c=2):
        """
        自定义分段函数
        参数：
        x: 输入值
        a: 转折点（默认5）
        b: 控制x<a时的弯曲程度（>0）
        c: 控制x>a时的弯曲程度（>0）
        """
        if abs(x)< 0.5:
            return 0
        if x >= 0:
            if x <= a:
                return a * (x / a) ** (1 / b)
            else:
                return a + c * np.log(x / a)
        else:
            return -normalize_y(-x, a, b, c)


    x_speed = normalize_x(move_speed.x())
    y_speed = normalize_y(move_speed.y())
    # print(f"y修正前后: {move_speed.y()} -> {y_speed}")
    return QPointF(x_speed, y_speed)


def cal_throw_offset(_remainder_throw: QPointF):
    """计算抛掷新位置偏移量"""

    def cal_throw_speed_f(throw_speed_f):
        # 计算当前速度的绝对值
        throw_gravity = config.throw_follow_gravity * config.follow_update_interval  # 重力加速度
        throw_speed_f.setY(throw_speed_f.y() + throw_gravity)
        return throw_speed_f

    config.throw_follow_speed = cal_throw_speed_f(config.throw_follow_speed)
    offset_f = config.throw_follow_speed * config.follow_update_interval + _remainder_throw  # 计算新位置, 加上未移动的量
    _remainder_throw = offset_f - QPointF(offset_f.toPoint())  # 转换回 QPointF 并取小数部分
    return QPoint(offset_f.toPoint()), _remainder_throw  # 转换回 QPoint, 并返回未移动的量


def cal_throw_rebound_offset(anchor_pos: QPoint, offset: QPoint, _remainder_throw: QPointF, screen_monitor: ScreenMonitor):
    # 计算反弹偏移量
    offset_f: QPointF = QPointF(offset) + _remainder_throw  # 加上未移动的量
    # screens:list[WorkAreaInfo] = self.widget.screen_monitor.get_screens() # 获取所有工作区域信息
    rebound_ratio: float = config.throw_follow_rebound_ratio
    speed: QPointF = QPointF(config.throw_follow_speed)

    now_pos: QPoint = anchor_pos
    new_pos_f: QPointF = now_pos + offset_f  # 计算新位置
    new_work_rect: QRect = screen_monitor.get_cur_work_by_xy_f(new_pos_f)  # 获取新位置所在的工作区域

    # print(f"new_pos_f: {pointf_to_tuple(new_pos_f)}, new_work_rect: {new_work_rect}")
    if not new_work_rect:  # 检查是否超过了当前屏幕的可见范围
        cur_work_rect: QRect = screen_monitor.get_cur_screen_work(anchor_pos)  # 获取当前位置所在的工作区域

        # 顶部,碰撞一次
        if new_pos_f.y() < cur_work_rect.top():
            if config.throw_follow_rebound_up_enabled:
                new_pos_f.setY(cur_work_rect.top() + (cur_work_rect.top() - new_pos_f.y()))
                speed = QPointF(speed.x() * rebound_ratio, -speed.y() * rebound_ratio)
        # 底部,碰撞一次
        elif new_pos_f.y() > cur_work_rect.bottom():
            if config.throw_follow_rebound_down_enabled:
                new_pos_f.setY(cur_work_rect.bottom() - (new_pos_f.y() - cur_work_rect.bottom()))
                speed = QPointF(speed.x() * rebound_ratio, -speed.y() * rebound_ratio)
                # 如果触发地面反弹，且速度较小，则直接停止移动
                # print(f"地面反弹, 速度: {pointf_to_tuple(speed)}")
                if abs(speed.y()) < 1:
                    new_pos_f = QPointF(new_pos_f.x(), cur_work_rect.bottom())  # 避免与底部碰撞
                    new_offset = new_pos_f - anchor_pos
                    config.throw_follow_speed = QPointF(0, 0)  # 速度重置为0pr
                    # print(f"地面反弹, 速度重置为0, 新位置: {pointf_to_tuple(new_pos_f)}")
                    return QPoint(new_offset.toPoint()), QPointF(0, 0)
                # speed = adjust_speed_to_zero(speed)
                # if
                # if offset == QPoint(0, 0) and speed == QPointF(0, 0):  # 反弹后速度为0，停止移动
                #     config.throw_follow_speed = QPointF(0, 0)  # 速度重置为0
                #     self.throw_end()  # 抛掷结束
                # else:

        # 即使屏幕连接，目标位置在全局可见，但工作区不可见
        new_pos_connect_f = screen_monitor.adjust_pos_connect_f(new_pos_f)
        is_connect_in_global_not_work = screen_monitor.in_global_screen_rect_f(new_pos_connect_f) and screen_monitor.get_cur_work_by_xy_f(new_pos_connect_f) is None

        # 左侧,碰撞一次
        if new_pos_f.x() < cur_work_rect.left():
            if config.throw_follow_rebound_left_right_enabled or is_connect_in_global_not_work:  # 如果开启左右反弹，或者（目标位置循环后 不在本窗口，但在其他窗口不可见区域）
                new_pos_f.setX(cur_work_rect.left() + (cur_work_rect.left() - new_pos_f.x()))
                speed = QPointF(-speed.x() * rebound_ratio, speed.y() * rebound_ratio)
                # 右侧,碰撞一次
        elif new_pos_f.x() > cur_work_rect.right():
            if config.throw_follow_rebound_left_right_enabled or is_connect_in_global_not_work:
                new_pos_f.setX(cur_work_rect.right() - (new_pos_f.x() - cur_work_rect.right()))
                speed = QPointF(-speed.x() * rebound_ratio, speed.y() * rebound_ratio)

        new_pos_f = pos_util.adjust_pos_to_work_f(new_pos_f, cur_work_rect)

    max_speed = config.throw_follow_max_speed_ms  # 在3ms，的最大速度

    # print(f"时间戳：{datetime.datetime.now().timestamp()}:speed={pos_util.pointf_to_tuple(speed)}")
    if abs(speed.x()) > max_speed:  # 反弹的限速
        speed.setX(max_speed if speed.x() > 0 else -max_speed)
    if abs(speed.y()) > max_speed:
        speed.setY(max_speed if speed.y() > 0 else -max_speed)
    config.throw_follow_speed = speed
    # print(f"new_pos_f: {pos_util.pointf_to_tuple(new_pos_f)}，_speed: {pos_util.pointf_to_tuple(speed)}")
    new_offset = new_pos_f - anchor_pos  # 计算反弹偏移量
    # print(f"new_pos_f: {pointf_to_tuple(new_pos_f)}, new_offset: {pointf_to_tuple(new_offset)}，_speed: {pointf_to_tuple(speed)}")
    _remainder_throw = new_offset - QPointF(new_offset.toPoint())  # 转换回 QPointF 并取小数部分
    return QPoint(new_offset.toPoint()), _remainder_throw  # 转换回 QPoint, 并返回未移动的量


def cal_mouse_offset(cur_pos: QPoint, tar_pos: QPoint, _remainder_mouse: QPointF):
    """计算新位置（逐步靠近鼠标）"""
    # print(f"now_pos: {pos_util.point_to_tuple(cur_pos)}, tar_pos: {pos_util.point_to_tuple(tar_pos)}, _remainder_mouse: {pos_util.pointf_to_tuple(_remainder_mouse)}")
    cur_now_f, tar_pos_f = QPointF(cur_pos) + _remainder_mouse, QPointF(tar_pos)  # QPointF 加上未移动的量,目标位置
    # print(f"now_pos_f: {pos_util.pointf_to_tuple(cur_now_f)}, tar_pos_f: {pos_util.pointf_to_tuple(tar_pos_f)}, _remainder_mouse: {pos_util.pointf_to_tuple(_remainder_mouse)}")

    distance_f = math.hypot(tar_pos_f.x() - cur_now_f.x(), tar_pos_f.y() - cur_now_f.y())  # 计算目标位置到当前位置的距离

    follow_speed = config.mouse_follow_speed * config.follow_update_interval / 8
    smoothing_factor = 50
    speed_factor = 1 - math.exp(-distance_f / smoothing_factor)
    new_offset_f = _remainder_mouse + (tar_pos_f - cur_now_f) * (follow_speed * speed_factor / distance_f)

    _remainder_mouse = new_offset_f - QPointF(new_offset_f.toPoint())  # 转换回 QPointF 并取小数部分
    # print(f"new_pos_f: {pos_util.pointf_to_tuple(new_offset_f)}, new_offset: {pos_util.point_to_tuple(new_offset_f.toPoint())}，_remainder_mouse: {pos_util.pointf_to_tuple(_remainder_mouse)}")
    return QPoint(new_offset_f.toPoint()), _remainder_mouse  # 返回新位置偏移量, 未移动的量
