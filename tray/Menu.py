import traceback
from contextlib import contextmanager
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMenu, QAction, QDialog, QVBoxLayout,
                            QSlider, QCheckBox, QPushButton, QMessageBox,
                            QHBoxLayout, QLabel)
from configs import config
from tray.SettingsDialog import SettingsDialog
from utils.log_util import logger
from utils.widget_util import signal_blocker


class Menu(QMenu):
    """系统托盘菜单（自动同步配置状态）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_actions()
        self._connect_signals()

    def _init_actions(self):
        """初始化菜单动作"""
        # 跟随功能开关
        self.follow_action = QAction("鼠标跟随", self.parent, checkable=True)
        self.follow_action.setChecked(config.follow_enabled)
        self.addAction(self.follow_action)

        # 拖动功能开关
        self.drag_action = QAction("拖动功能", self.parent, checkable=True)
        self.drag_action.setChecked(config.drag_enabled)
        self.addAction(self.drag_action)

        self.addSeparator()

        # 设置菜单
        self.settings_action = QAction("设置", self.parent)
        self.addAction(self.settings_action)

        self.addSeparator()

        # 退出菜单
        self.exit_action = QAction("退出", self.parent)
        self.addAction(self.exit_action)

    def _connect_signals(self):
        """连接信号与槽"""
        # 菜单动作信号
        self.follow_action.toggled.connect(self._on_follow_toggled)
        self.drag_action.toggled.connect(self._on_drag_toggled)
        self.settings_action.triggered.connect(self._show_settings)  # 设置
        self.exit_action.triggered.connect(self.parent.close)    # 退出

        # # 配置变更信号
        # config.follow_enabled_changed.connect(self._update_follow_action)
        # config.drag_enabled_changed.connect(self._update_drag_action)

    @config.follow_enabled_changed.connect
    def _update_follow_action(self, sender, value):
        """更新跟随菜单状态"""
        if self.follow_action.isChecked() != value:
            with signal_blocker(self.follow_action):
                self.follow_action.setChecked(value)

    @config.drag_enabled_changed.connect
    def _update_drag_action(self, sender, value):
        """更新拖动菜单状态"""
        if self.drag_action.isChecked() != value:
            with signal_blocker(self.drag_action):
                self.drag_action.setChecked(value)

    def _on_follow_toggled(self, checked):
        """处理菜单跟随切换"""
        try:
            config.follow_enabled = checked
            logger.info(f"用户{'开启' if checked else '关闭'}鼠标跟随")
        except Exception as e:
            logger.error(f"菜单切换跟随错误: {traceback.format_exc()}")

    def _on_drag_toggled(self, checked):
        """处理菜单拖动切换"""
        try:
            config.drag_enabled = checked
            logger.info(f"用户{'开启' if checked else '关闭'}拖动功能")
        except Exception as e:
            logger.error(f"菜单切换拖动错误: {traceback.format_exc()}")

    def _show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self.parent)
            dialog.exec_()
        except Exception as e:
            logger.error(f"显示设置对话框错误: {traceback.format_exc()}")
            QMessageBox.critical(self, "错误", f"无法打开设置窗口: {str(e)}")