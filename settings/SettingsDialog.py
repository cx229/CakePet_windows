import traceback

from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox, QHBoxLayout, QTabWidget)
from PyQt5.QtCore import Qt, QTimer

from configs import config
from utils.log_util import logger
from utils.pos_util import point_to_tuple


class SettingsDialog(QDialog):
    """设置对话框：设置页 + 实时信息监控页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(False)  # 关键设置：改为非模态对话框
        self.parent = parent
        self._init_ui()
        self._connect_signals()

        # 信息页更新定时器
        self.info_timer = QTimer(self)
        self.info_timer.timeout.connect(self.update_info_page)
        self.info_timer.start(100)  # 每100ms更新一次信息页

    def _init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("设置页 ")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(800, 900)

        # 创建选项卡
        self.tab_widget = QTabWidget(self)

        # 第一页 - 纯设置页（无实时信息）
        self.settings_tab = QWidget()
        self._init_settings_tab()

        # 第二页 - 纯信息监控页（无设置控件）
        self.info_tab = QWidget()
        self._init_info_tab()

        self.tab_widget.addTab(self.settings_tab, "设置")
        self.tab_widget.addTab(self.info_tab, "监控")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def _init_settings_tab(self):
        """初始化纯设置页"""
        layout = QVBoxLayout()

        # 屏幕循环连接功能开关
        self.screen_connect_check = QCheckBox("启用屏幕循环连接功能", self)
        self.screen_connect_check.setChecked(config.screen_connect_enabled)
        layout.addWidget(self.screen_connect_check)

        #

        # 跟随速度设置
        self.speed_label = QLabel(f"跟随速度: {config.mouse_follow_speed:.1f}(默认5)", self)
        layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(int(config.mouse_follow_speed) * 10)
        layout.addWidget(self.speed_slider)

        # 变大功能开关
        self.bigger_check = QCheckBox("启用变大功能", self)
        self.bigger_check.setChecked(config.bigger_enabled)
        layout.addWidget(self.bigger_check)

        # 标准大小比例设置
        self.standard_size_ratio_label = QLabel(f"大小比例基数: {config.size_ratio_base:.1f} (默认1.0)", self)
        layout.addWidget(self.standard_size_ratio_label)
        self.size_ratio_base_slider = QSlider(Qt.Horizontal, self)
        self.size_ratio_base_slider.setRange(1, 100)
        self.size_ratio_base_slider.setValue(int(config.size_ratio_base) * 10)
        layout.addWidget(self.size_ratio_base_slider)

        # 变大最大比例设置
        self.bigger_max_size_ratio_label = QLabel(f"变大最大比例: {config.bigger_max_size_ratio:.1f} (默认10.0)", self)
        layout.addWidget(self.bigger_max_size_ratio_label)
        self.bigger_max_ratio_slider = QSlider(Qt.Horizontal, self)
        self.bigger_max_ratio_slider.setRange(10, 200)
        self.bigger_max_ratio_slider.setValue(int(config.bigger_max_size_ratio) * 10)
        layout.addWidget(self.bigger_max_ratio_slider)

        # 变大等待时间设置
        self.wait_label = QLabel(f"变大等待时间: {config.bigger_wait_time / 60 / 1000:.1f}分钟(默认45分钟)", self)
        layout.addWidget(self.wait_label)
        self.wait_slider = QSlider(Qt.Horizontal, self)
        self.wait_slider.setRange(1, 240)
        self.wait_slider.setValue(int(config.bigger_wait_time / 60 / 1000))
        layout.addWidget(self.wait_slider)

        layout.addStretch()  # 添加弹簧使控件靠上
        self.settings_tab.setLayout(layout)

    def _connect_signals(self):
        """连接设置页的信号与槽"""
        self.screen_connect_check.stateChanged.connect(self._on_screen_connect_changed)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.bigger_check.stateChanged.connect(self._on_bigger_changed)
        self.size_ratio_base_slider.valueChanged.connect(self._on_size_ratio_base_changed)
        self.bigger_max_ratio_slider.valueChanged.connect(self._on_bigger_max_size_ratio_changed)
        self.wait_slider.valueChanged.connect(self._on_wait_changed)

    def _init_info_tab(self):
        """初始化纯信息监控页"""
        layout = QVBoxLayout()
        # 添加坐标系说明
        coordinate_info = QLabel("坐标说明：@=全局坐标，无@=窗口相对坐标", self)
        coordinate_info.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(coordinate_info)

        layout.addSpacing(10)  # 添加一点间距
        # 窗口信息
        self.widget_rect_label = QLabel("@窗口位置尺寸: --", self)
        layout.addWidget(self.widget_rect_label)

        # 按键信息
        self.keyboard_info_label = QLabel("按键信息: --", self)
        layout.addWidget(self.keyboard_info_label)

        # 图片模式
        self.img_mode_label = QLabel("图片模式: --", self)
        layout.addWidget(self.img_mode_label)

        layout.addSpacing(10)  # 添加一点间距
        # 屏幕信息
        self.screen_rect_label = QLabel("屏幕位置尺寸: --", self)
        layout.addWidget(self.screen_rect_label)

        layout.addSpacing(10)  # 添加一点间距
        # 鼠标位置
        self.mouse_pos_label = QLabel("鼠标位置: --", self)
        layout.addWidget(self.mouse_pos_label)

        layout.addSpacing(10)  # 添加一点间距
        # 图片信息
        self.img_rect_label = QLabel("图片位置尺寸: --", self)
        layout.addWidget(self.img_rect_label)

        # 图片锚点信息
        self.img_anchor_label = QLabel("图片锚点位置: --", self)
        layout.addWidget(self.img_anchor_label)

        # 图片缩放比例
        self.img_size_ratio_label = QLabel("图片缩放比例(base,ratio): --", self)
        layout.addWidget(self.img_size_ratio_label)

        layout.addSpacing(10)  # 添加一点间距
        # 放大功能的等待时间
        self.bigger_wait_label = QLabel(f"变大等待时间: --", self)
        layout.addWidget(self.bigger_wait_label)

        # 托盘消息
        self.tray_msg_label = QLabel("托盘消息: --", self)
        layout.addWidget(self.tray_msg_label)


        layout.addStretch()  # 添加弹簧使控件靠上
        self.info_tab.setLayout(layout)

    def update_info_page(self):
        """专门用于更新信息页的实时数据"""
        if not self.isVisible() or self.tab_widget.currentIndex() != 1:  # 仅当信息页激活时更新
            return
        try:
            # 只在信息页激活时更新（可选优化）
            if self.tab_widget.currentWidget() != self.info_tab:
                return

            if self.parent:
                self.widget_rect_label.setText(
                    f"@窗口位置尺寸: {self.parent.geometry().getRect()}"
                )
                from FollowAndDragWidget import FollowAndDragWidget
                if isinstance(self.parent, FollowAndDragWidget):
                    # 按键信息
                    self.keyboard_info_label.setText(
                        f"按键信息: {self.parent.key_monitor.get_pressed_keys()}"
                    )

                    screens_workarea_str = "\n".join(self.parent.screen_monitor.get_screens_workarea_tuple_list())
                    self.screen_rect_label.setText(
                        f"屏幕位置尺寸: \n{screens_workarea_str}"
                    )
                    # 图片模式
                    self.img_mode_label.setText(
                        f"图片模式: {self.parent.mode_manager.get_current_mode_name()}"
                    )

                    self.mouse_pos_label.setText(
                        f"鼠标位置: {point_to_tuple(self.parent.get_cursor_pos())}"
                    )
                    self.img_rect_label.setText(
                        f"图片位置尺寸: {self.parent.get_img_rect().getRect()}"
                    )
                    bigger_time = self.parent.size_growing_controller.get_wait_elapsed_time()  # 毫秒
                    self.bigger_wait_label.setText(
                        f"变大等待时间: {int(bigger_time / (1000))}秒/{int(config.bigger_wait_time / (1000))}秒，"
                        f"{int(bigger_time / (60 * 1000))}分钟/{int(config.bigger_wait_time / (60 * 1000))}分钟"
                    )
                    # 托盘消息
                    self.tray_msg_label.setText(
                        f"托盘消息: {self.parent.tray_msg_controller.rect.getRect()}"
                    )



            self.img_anchor_label.setText(
                f"图片锚点位置: {point_to_tuple(config.anchor_pos)}"
            )
            self.img_size_ratio_label.setText(
                f"图片缩放比例(base,ratio): ({config.size_ratio_base:.1f}, {config.size_ratio:.1f})"
            )

        except Exception as e:
            logger.error(f"更新监控页错误: {traceback.format_exc()}")

    def _on_screen_connect_changed(self, state):
        """处理屏幕循环连接功能切换"""
        config.screen_connect_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}屏幕循环连接功能")

    def _on_speed_changed(self, value):
        """处理速度设置变化"""
        speed = value / 10
        config.mouse_follow_speed = speed
        self.speed_label.setText(f"跟随速度: {speed:.1f}（默认5）")
        logger.info(f"设置，用户设置跟随速度为: {speed}")

    def _on_bigger_changed(self, state):
        """处理变大功能切换"""
        config.bigger_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}变大功能")

    def _on_size_ratio_base_changed(self, value):
        """处理标准大小比例设置变化"""
        config.size_ratio_base = value / 10
        self.standard_size_ratio_label.setText(f"大小比例基数: {config.size_ratio_base:.1f} (默认1.0)")
        logger.info(f"设置，用户设置标准大小比例为: {config.size_ratio_base}")

    def _on_bigger_max_size_ratio_changed(self, value):
        """处理变大最大比例设置变化"""
        config.bigger_max_size_ratio = value / 10
        self.bigger_max_size_ratio_label.setText(f"变大最大比例: {config.bigger_max_size_ratio:.1f} (默认10.0)")
        logger.info(f"设置，用户设置变大最大比例为: {config.bigger_max_size_ratio}")

    def _on_wait_changed(self, value):
        """处理变大等待时间设置变化"""
        config.bigger_wait_time = value * 60 * 1000
        self.wait_label.setText(f"变大等待时间: {value:.1f}分钟(默认45分钟)")
        logger.info(f"设置，用户设置变大等待时间为: {value}分钟")

    def closeEvent(self, event):
        """关闭窗口时停止定时器"""
        self.info_timer.stop()
        super().closeEvent(event)
