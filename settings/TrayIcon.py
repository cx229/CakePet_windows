from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import traceback

from utils.log_util import logger


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 加载托盘图标
        try:
            tray_icon = QPixmap("img/icon.png")  # 任务栏图标
            if tray_icon.isNull():
                raise FileNotFoundError("无法加载托盘图标 image.png")
            logger.info("托盘图标加载成功")
        except Exception as e:
            logger.error(f"托盘图标加载错误: {traceback.format_exc()}")
            tray_icon = QPixmap(32, 32)
            tray_icon.fill(Qt.blue)

        # 设置托盘图标
        self.setIcon(QIcon(tray_icon))
        # 双击托盘图标显示/隐藏窗口
        self.activated.connect(self.toggle_window_visibility)

    def toggle_window_visibility(self, reason):
        """双击托盘图标切换窗口可见性"""
        try:
            if reason == QSystemTrayIcon.DoubleClick:
                if self.isVisible():
                    self.hide()
                    logger.info("用户双击托盘图标隐藏窗口")
                else:
                    self.show()
                    logger.info("用户双击托盘图标显示窗口")
        except Exception as e:
            logger.error(f"切换窗口可见性错误: {traceback.format_exc()}")