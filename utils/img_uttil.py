import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from utils.log_util import logger


def load_img(path):
    """加载单个图片并处理异常"""
    try:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            raise FileNotFoundError(f"无法加载图片 {path}")
        return pixmap
    except Exception as e:
        logger.error(f"图片加载错误({path}): {traceback.format_exc()}")
        # 创建默认红色图片
        default_pixmap = QPixmap(100, 100)
        default_pixmap.fill(Qt.red)
        return default_pixmap
