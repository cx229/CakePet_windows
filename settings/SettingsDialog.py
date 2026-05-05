import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QApplication, )
from PyQt5.QtCore import Qt, QTimer

from settings.AboutWidget import AboutWidget
from settings.InfoWidget import InfoWidget
from settings.SettingsWidget import SettingsWidget
from settings.TabWidget import TabWidget


class SettingsDialog(QDialog):
    """设置对话框：设置页 + 实时信息监控页"""
    _instance = None  # 单例实例

    def __new__(cls, parent):
        """单例模式的核心实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, parent):
        if not hasattr(self, '_initialized') or not self._initialized:
            super().__init__(None)
            self.setModal(False)  # 改为非模态对话框
            self.parent = parent

            self._init_ui()
            self._initialized = True  # 标记为已初始化

    def _init_ui(self):
        """初始化UI界面"""
        self.setWindowFlags(
            self.windowFlags() |
            Qt.Window |  # 作为独立窗口
            Qt.WindowTitleHint |  # 显示标题栏
            Qt.WindowSystemMenuHint |  # 显示系统菜单
            Qt.WindowMinMaxButtonsHint  # 显示最小化/最大化按钮（可选）
        )

        # 设置窗口图标
        icon_path = "img/icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("设置 - 小小芝麻酥")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(900, 800)  # 设置最小尺寸（防止窗口过小）
        self.resize(1200, 1200)  # 设置初始默认大小（可选）

        main_layout = QVBoxLayout()
        # 替换原来的 tab_widget
        self.tab_widget = TabWidget()
        self.tab_widget.addTab("设置", SettingsWidget(self.parent))
        self.tab_widget.addTab("监控", InfoWidget(self.parent))
        self.tab_widget.addTab("关于", AboutWidget(self.parent))

        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def move_center(self):
        """窗口显示时移动到屏幕中央"""
        screen = QApplication.desktop().screenGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    @classmethod
    def show_or_focus(cls, parent):
        """显示或激活现有窗口"""
        if cls._instance is None:
            cls._instance = cls(parent)
        cls._instance.move_center()
        cls._instance.show()
        cls._instance.activateWindow()

    def showEvent(self, event):
        if hasattr(self, 'tab_widget'):
            self.tab_widget.start()

    def closeEvent(self, event):
        """关闭窗口时停止定时器"""
        if hasattr(self, 'tab_widget'):
            self.tab_widget.stop()
        super().closeEvent(event)
