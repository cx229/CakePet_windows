from abc import ABC

from utils.log_util import logger


class ModuleController(ABC):
    """ 模块控制器 基类"""

    def start(self):
        """启动 控制器"""
        logger.info(f"模块控制器 {self.name} 启动")

    def restart(self):
        """重新开始 控制器"""
        logger.info(f"模块控制器 {self.name} 重新开始")

    def pause(self):
        """暂停 控制器"""
        logger.info(f"模块控制器 {self.name} 暂停")

    def resume(self):
        """恢复 控制器"""
        logger.info(f"模块控制器 {self.name} 恢复")

    def stop(self):
        """停止 控制器"""
        logger.info(f"模块控制器 {self.name} 停止")

    @property
    def name(self) -> str:
        return str(self.__class__.__name__)
