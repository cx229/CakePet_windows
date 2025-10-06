from abc import ABC

from PyQt5.QtWidgets import QWidget

from utils.log_util import logger


class ImageMode(ABC):
    title: str = "图片类"

    def __init__(self, widget: QWidget):
        self.widget = widget

    def start(self):
        """启动模式"""
        logger.info(f"模式 {self.get_name()} 启动")

    def restart(self):
        """重新开始模式"""
        logger.info(f"模式 {self.get_name()} 重新开始")

    def pause(self):
        """暂停模式"""
        logger.info(f"模式 {self.get_name()} 暂停")

    def resume(self):
        """恢复模式"""
        logger.info(f"模式 {self.get_name()} 恢复")

    def stop(self):
        """停止模式"""

        logger.info(f"模式 {self.get_name()} 停止")

    @classmethod
    def get_name(cls) -> str:
        return str(cls.__name__)

    @classmethod
    def get_title_name(cls) -> str:
        """获取模式对应的按键名称"""
        return f"{cls.title}({cls.get_name()})"

# x = ImageMode(None)
# 
# print(type(x.get_name()()))
# 
# 
# 
# print(ImageMode.get_name()(),type(ImageMode.get_name()()))
