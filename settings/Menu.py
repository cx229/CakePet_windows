import traceback
from PyQt5.QtWidgets import (QMenu, QAction, QDialog, QVBoxLayout,
                             QSlider, QCheckBox, QPushButton, QMessageBox,
                             QHBoxLayout, QLabel, QApplication)
from configs import config
import image_modes
from settings.SettingsDialog import SettingsDialog
from utils.log_util import logger
from utils.widget_util import signal_blocker

# Windows API常量
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
GWL_EXSTYLE = -20


class Menu(QMenu):
    """系统托盘菜单（自动同步配置状态）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self._init_actions()
        self._init_img_mode_submenu()
        self._connect_signals()

    def _init_actions(self):
        """初始化菜单动作"""

        # 拖动功能开关
        self.drag_action = QAction("单击拖动", self.parent, checkable=True)
        self.drag_action.setChecked(config.drag_follow_enabled)
        self.addAction(self.drag_action)

        # 抛掷功能开关
        self.throw_action = QAction("重力抛掷", self.parent, checkable=True)
        self.throw_action.setChecked(config.throw_follow_enabled)
        self.addAction(self.throw_action)

        # 跟随功能开关
        self.follow_action = QAction("鼠标跟随", self.parent, checkable=True)
        self.follow_action.setChecked(config.mouse_follow_enabled)
        self.addAction(self.follow_action)

        # 点击穿透开关
        self.click_through_action = QAction("点击穿透", self.parent, checkable=True)
        self.click_through_action.setChecked(config.click_through_enabled)
        self.addAction(self.click_through_action)

        # 放大 开关
        self.bigger_action = QAction("放大", self.parent, checkable=True)
        self.bigger_action.setChecked(config.bigger_flag)
        self.addAction(self.bigger_action)

        # 创建静态子菜单
        self.img_mode_submenu = QMenu("触发行为", self)
        self.addMenu(self.img_mode_submenu)

        self.addSeparator()  # 分隔线

        # 设置菜单
        self.settings_action = QAction("设置", self.parent)
        self.addAction(self.settings_action)

        self.addSeparator()  # 分隔线

        # 退出菜单
        self.exit_action = QAction("退出", self.parent)
        self.addAction(self.exit_action)

    def _connect_signals(self):
        """连接信号与槽"""
        # 菜单动作信号
        self.drag_action.toggled.connect(self._on_drag_toggled)
        self.throw_action.toggled.connect(self._on_throw_toggled)
        self.follow_action.toggled.connect(self._on_follow_toggled)
        self.bigger_action.toggled.connect(self._on_bigger_toggled)
        self.click_through_action.toggled.connect(self._on_click_through_toggled)

        self.settings_action.triggered.connect(self._show_settings)  # 设置
        self.exit_action.triggered.connect(QApplication.instance().quit)  # 直接退出应用

        # # 配置变更信号
        config.drag_follow_enabled_changed.connect(self._update_drag_action)
        config.throw_follow_enabled_changed.connect(self._update_throw_action)
        config.mouse_follow_enabled_changed.connect(self._update_follow_action)
        config.bigger_flag_changed.connect(self._update_bigger_action)
        config.click_through_enabled_changed.connect(self._update_click_through_action)
        # config.click_through_enabled_changed.connect(self._handle_click_through_action)

    def _update_click_through_action(self, sender, value):
        """更新点击穿透菜单状态"""
        if self.click_through_action.isChecked() != value:
            with signal_blocker(self.click_through_action):
                self.click_through_action.setChecked(value)

    def _update_drag_action(self, sender, value):
        """更新拖动菜单状态"""
        if self.drag_action.isChecked() != value:
            with signal_blocker(self.drag_action):
                self.drag_action.setChecked(value)

    def _update_throw_action(self, sender, value):
        """更新抛掷菜单状态"""
        if self.throw_action.isChecked() != value:
            with signal_blocker(self.throw_action):
                self.throw_action.setChecked(value)

    def _update_follow_action(self, sender, value):
        """更新跟随菜单状态"""
        if self.follow_action.isChecked() != value:
            with signal_blocker(self.follow_action):
                self.follow_action.setChecked(value)

    def _update_bigger_action(self, sender, value):
        """更新放大菜单状态"""
        if self.bigger_action.isChecked() != value:
            with signal_blocker(self.bigger_action):
                self.bigger_action.setChecked(value)

    def _on_drag_toggled(self, checked):
        """处理菜单拖动切换"""
        try:
            config.drag_follow_enabled = checked
            logger.info(f"菜单，用户{'开启' if checked else '关闭'}拖动功能")
        except Exception as e:
            logger.error(f"菜单切换拖动错误: {traceback.format_exc()}")

    def _on_throw_toggled(self, checked):
        """处理菜单抛掷切换"""
        try:
            config.throw_follow_enabled = checked
            logger.info(f"菜单，用户{'开启' if checked else '关闭'}抛掷功能")
        except Exception as e:
            logger.error(f"菜单切换抛掷错误: {traceback.format_exc()}")

    def _on_follow_toggled(self, checked):
        """处理菜单跟随切换"""
        try:
            config.mouse_follow_enabled = checked
            logger.info(f"菜单，用户{'开启' if checked else '关闭'}鼠标跟随")
        except Exception as e:
            logger.error(f"菜单切换跟随错误: {traceback.format_exc()}")

    def _on_bigger_toggled(self, checked):
        """处理菜单放大切换"""
        try:
            config.bigger_flag = checked
            logger.info(f"菜单，用户{'开启' if checked else '关闭'}放大功能")
        except Exception as e:
            logger.error(f"菜单切换放大错误: {traceback.format_exc()}")

    def _on_click_through_toggled(self, checked):
        """处理菜单点击穿透切换"""
        try:
            config.click_through_enabled = checked
            logger.info(f"菜单，用户{'开启' if checked else '关闭'}点击穿透功能")
        except Exception as e:
            logger.error(f"菜单切换点击穿透错误: {traceback.format_exc()}")

    def _show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self.parent)
            dialog.show()  # 使用 show() 而不是 exec_()
            # dialog.exec_()
        except Exception as e:
            logger.error(f"显示设置对话框错误: {traceback.format_exc()}")
            QMessageBox.critical(self, "错误", f"无法打开设置窗口: {str(e)}")

    def _on_img_mode_clicked(self, img_mode: image_modes.ImagesMode):
        """处理子菜单项点击事件"""
        logger.info(f"触发指定图片模式: {img_mode.get_title_name()}")
        config.mode_name = img_mode.get_name()

    def _init_img_mode_submenu(self):
        """初始化图片模式子菜单"""

        def add_modes_to_submenu(modes):
            for item in modes:
                action = QAction(item.title, self.img_mode_submenu)
                action.triggered.connect(lambda _, x=item: self._on_img_mode_clicked(x))
                self.img_mode_submenu.addAction(action)

        add_modes_to_submenu(image_modes.modes_standby_fix)
        self.img_mode_submenu.addSeparator()  # 分隔线
        add_modes_to_submenu(image_modes.modes_standby_move)
