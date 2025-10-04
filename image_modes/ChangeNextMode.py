import random

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

from configs import config
from image_modes.ImageMode import ImageMode
from utils.log_util import logger


def get_random_next_mode_name(current_mode_name: str, available_modes_name: list = None):
    """获取随机下一个模式名称"""
    if available_modes_name is None:  # 没有指定模式列表时，使用所有待机模式
        from image_modes import modes_standby_fix, modes_standby_move
        modes = modes_standby_fix  # 固定待机模式
        if not config.mouse_follow_enabled:  # 如果不是鼠标跟随模式，则添加移动模式
            modes += modes_standby_move
        modes_name = [str(m.name()) for m in modes]
        available_modes_name = [name for name in modes_name if name != current_mode_name]  # 排除当前模式
    if available_modes_name:
        next_mode_name = random.choice(available_modes_name)  # 随机选择下一个模式
    else:
        next_mode_name = current_mode_name
    return next_mode_name


class NextChangeMode(ImageMode):
    """切换下一个模式"""

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.next_mode_name = get_random_next_mode_name(self.name())

    def change_mode(self):
        if self.next_mode_name is not None:
            config.mode_name = self.next_mode_name  # 切换到下一个模式
        else:
            logger.info(f"没有指定下一个模式，当前模式 {self.name()} 保持不变")


class TimerNextChange(NextChangeMode):
    """定时器下一个行为"""

    def __init__(self, widget: QWidget, time_next_enabled: bool = True, interval_min=3000, interval_max=10000, prob=0.5):
        super().__init__(widget)
        self.time_next_enabled = time_next_enabled  # 是否使用随机间隔时间
        self.change_interval_min = interval_min  # 随机间隔时间（毫秒）
        self.change_interval_max = interval_max  # 随机间隔时间（毫秒）
        self.change_prob = prob  # 随机概率（0-1之间）
        self.timer = QTimer(self.widget)  # 定时器
        if self.time_next_enabled:
            self.timer.timeout.connect(self.time_next)  # 连接超时信号到下一个方法

    def get_interval(self):
        """获取随机间隔时间"""
        mn_interval = min(self.change_interval_min, self.change_interval_max)
        mx_interval = max(self.change_interval_min, self.change_interval_max)
        return random.randint(mn_interval, mx_interval)

    def time_next(self):
        """概率下一个"""
        if random.random() < self.change_prob and not config.is_drag_follow and not config.is_mouse_follow:
            logger.info(f"随机概率 {self.change_prob} 触发，当前模式 {self.name()} 切换到 {self.next_mode_name}")
            self.change_mode()
        else:
            logger.info(f"随机概率 {self.change_prob} 未触发，当前模式 {self.name()} 保持不变")
            self.timer.start(self.get_interval())  # 启动定时器

    def restart(self):
        """重新开始随机下一个"""
        super().restart()
        self.timer.start(self.get_interval())  # 启动定时器

    def start(self):
        """开始随机下一个"""
        super().start()
        self.timer.start(self.get_interval())  # 启动定时器

    def pause(self):
        """暂停随机下一个"""
        super().pause()
        self.timer.stop()

    def resume(self):
        """恢复随机下一个"""
        super().resume()
        self.timer.start()  # 继续启动计算器，但是不重置

    def stop(self):
        """停止随机下一个"""
        super().stop()
        self.timer.stop()
