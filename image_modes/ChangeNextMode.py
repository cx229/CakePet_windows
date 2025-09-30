import random

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

from configs import config
from image_modes.ImageMode import ImageMode
from utils.log_util import logger


def get_random_next_mode_name(current_mode: str, available_modes_name: list = None):
    """获取随机下一个模式名称"""
    from image_modes import modes_name_standby
    if available_modes_name is None:  # 没有指定模式列表时，使用所有待机模式
        available_modes_name = [name for name in modes_name_standby if name != current_mode]  # 排除当前模式
    next_mode_name = random.choice(available_modes_name)  # 随机选择下一个模式
    return next_mode_name


class NextChangeMode(ImageMode):
    """切换下一个模式"""

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.next_mode_name = get_random_next_mode_name(self.name())

    def change_mode(self):
        if config.mode_change_enable:
            config.mode_name = self.next_mode_name  # 切换到下一个模式
        else:
            logger.info(f"模式切换已禁用，当前模式 {self.name} 保持不变")


class TimerNextChange(NextChangeMode):
    """定时器下一个行为"""

    def __init__(self, widget: QWidget, interval_min=3000, interval_max=10000, prob=0.5):
        super().__init__(widget)
        self.change_interval_min = interval_min  # 随机间隔时间（毫秒）
        self.change_interval_max = interval_max  # 随机间隔时间（毫秒）
        self.change_prob = prob  # 随机概率（0-1之间）
        self.timer = QTimer(self.widget)  # 定时器
        self.timer.timeout.connect(self.time_next)  # 连接超时信号到下一个方法

    def time_next(self):
        """随机下一个"""
        if random.random() < self.change_prob and not config.is_dragging and not config.is_following:
            logger.info(f"随机概率 {self.change_prob} 触发，当前模式 {self.name} 切换到 {self.next_mode_name}")
            self.change_mode()
        else:
            logger.info(f"随机概率 {self.change_prob} 未触发，当前模式 {self.name} 保持不变")
            self.timer.setInterval(random.randint(self.change_interval_min, self.change_interval_max))

    def restart(self):
        """重新开始随机下一个"""
        super().restart()
        self.timer.setInterval(random.randint(self.change_interval_min, self.change_interval_max))

    def start(self):
        """开始随机下一个"""
        super().start()
        self.timer.start(random.randint(self.change_interval_min, self.change_interval_max))

    def stop(self):
        """停止随机下一个"""
        super().stop()
        self.timer.stop()
