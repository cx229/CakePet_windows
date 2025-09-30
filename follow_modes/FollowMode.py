from abc import ABC

from PyQt5.QtWidgets import QWidget

from utils.log_util import logger


class FollowMode(ABC):
    def __init__(self, widget: QWidget):
        self.widget = widget
    def start(self):
        """启动模式"""
        logger.info(f"跟随模式 {self.name()} 启动")

    def stop(self):
        """停止模式"""
        logger.info(f"跟随模式 {self.name()} 停止")



    @classmethod
    def name(cls) -> str:
        return str(cls.__name__)