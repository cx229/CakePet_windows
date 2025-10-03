from abc import ABC

from PyQt5.QtWidgets import QWidget

from utils.log_util import logger


class ImageMode(ABC):
    def __init__(self, widget: QWidget):
        self.widget = widget


    def start(self):
        """启动模式"""
        logger.info(f"模式 {self.name()} 启动")

    def restart(self):
        """重新开始模式"""
        logger.info(f"模式 {self.name()} 重新开始")

    def pause(self):
        """暂停模式"""
        logger.info(f"模式 {self.name()} 暂停")

    def resume(self):
        """恢复模式"""
        logger.info(f"模式 {self.name()} 恢复")

    def stop(self):
        """停止模式"""
        logger.info(f"模式 {self.name()} 停止")

    @classmethod
    def name(cls) -> str:
        return str(cls.__name__)



print(ImageMode.name())
