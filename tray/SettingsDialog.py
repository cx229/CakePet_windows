import traceback

from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt

from configs import config
from utils.log_util import logger
from utils.widget_util import signal_blocker


class SettingsDialog(QDialog):
    """设置对话框（自动同步配置状态）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("鼠标跟随工具 - 设置")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint |
                          Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(300, 250)

        layout = QVBoxLayout()

        # 跟随功能开关
        self.follow_check = QCheckBox("启用鼠标跟随", self)
        self.follow_check.setChecked(config.follow_enabled)
        layout.addWidget(self.follow_check)

        # 跟随速度设置
        self.speed_label = QLabel(f"跟随速度: {config.follow_speed:.1f}", self)
        layout.addWidget(self.speed_label)

        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(int(config.follow_speed) * 10)
        layout.addWidget(self.speed_slider)

        # 拖动功能开关
        self.drag_check = QCheckBox("启用拖动功能", self)
        self.drag_check.setChecked(config.drag_enabled)
        layout.addWidget(self.drag_check)

        self.setLayout(layout)

    def _connect_signals(self):
        """连接信号与槽"""
        self.follow_check.stateChanged.connect(self._on_follow_changed)
        self.drag_check.stateChanged.connect(self._on_drag_changed)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)

    def _on_follow_changed(self, state):
        """处理跟随功能切换"""
        try:
            with signal_blocker(self.follow_check):
                config.follow_enabled = bool(state)
                logger.info(f"用户{'开启' if state else '关闭'}鼠标跟随")
        except Exception as e:
            logger.error(f"切换跟随状态错误: {traceback.format_exc()}")

    def _on_drag_changed(self, state):
        """处理拖动功能切换"""
        try:
            with signal_blocker(self.drag_check):
                config.drag_enabled = bool(state)
                logger.info(f"用户{'开启' if state else '关闭'}拖动功能")
        except Exception as e:
            logger.error(f"切换拖动状态错误: {traceback.format_exc()}")

    def _on_speed_changed(self, value):
        """处理速度设置变化"""
        try:
            speed = value / 10
            config.follow_speed = speed
            self.speed_label.setText(f"跟随速度: {speed:.1f}")
            logger.info(f"用户设置跟随速度为: {speed}")
        except Exception as e:
            logger.error(f"更新速度设置错误: {traceback.format_exc()}")
