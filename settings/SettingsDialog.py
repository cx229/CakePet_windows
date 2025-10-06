import os
import traceback

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox, QHBoxLayout, QTabWidget, QGroupBox, QScrollArea, QSizePolicy)
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

        # 设置窗口图标
        icon_path = "img/icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 信息页更新定时器
        self.info_timer = QTimer(self)
        self.info_timer.timeout.connect(self.update_info_page)
        self.info_timer.start(100)  # 每100ms更新一次信息页

    def _init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("设置页 ")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(1200, 1200)

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
        """初始化纯设置页（淡蓝色主题+修复布局）"""
        # 创建主容器和滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        # 主布局
        main_layout = QVBoxLayout(self.settings_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 淡蓝色主题样式表
        self.setStyleSheet("""
            /* 全局样式 */
            QWidget {
                font-family: "Microsoft YaHei";
                font-size: 18px;
                background-color: #f8fbff;
                color: #333333;
            }

            QScrollArea {
                background-color: #f8fbff;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #e6f0ff;
                width: 10px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #4a90e2;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #3a80d2;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            /* 设置项容器 */
            .setting-item {
                background-color: #ffffff;
                border-bottom: 1px solid #e6f0ff;
                min-height: 70px;
            }

            .setting-item:last-child {
                border-bottom: none;
            }

            /* 分组标题 */
            .group-title {
                font-size: 18px;
                font-weight: bold;
                color: #2c6bb0;
                background-color: #e6f0ff;
                padding: 20px 25px;
                border-bottom: 1px solid #d0e0ff;
                margin: 0px;
            }

            /* 主标题样式 */
            .setting-title {
                font-size: 22px;
                color: #333333;
                font-weight: normal;
                margin: 0px;
                padding: 0px;
                min-height: 25px;
            }

            /* 说明文字样式 */
            .setting-description {
                font-size: 18px;
                color: #666666;
                margin: 0px 0px 0px 0px;  /* 减小标题和说明的间距 */
                padding: 0px;
                line-height: 1.5;
                font-weight: normal;
                min-height: 22px;
            }

            /* 状态文字 */
            .status-text {
                font-size: 16px;
                color: #ff6b6b;
                margin: 5px 0px 0px 0px;
                padding: 0px;
                font-style: italic;
            }

            /* 开关样式 */
            QCheckBox {
                spacing: 0px;
                padding: 0px;
                margin: 0px;
            }

            QCheckBox::indicator {
                width: 50px;
                height: 20px;
                border-radius: 16px;
                background-color: #cccccc;
                border: 5px solid #cccccc;
            }

            QCheckBox::indicator:checked {
                background-color: #4a90e2;
                border-color: #4a90e2;
            }

            QCheckBox::indicator:unchecked {
                background-color: #cccccc;
                border-color: #cccccc;
            }

            /* 开关滑块 */
            QCheckBox::indicator:checked::after {
                content: "";
                position: absolute;
                left: 32px;
                width: 28px;
                height: 28px;
                border-radius: 14px;
                background-color: white;
                margin: 2px;
            }

            QCheckBox::indicator:unchecked::after {
                content: "";
                position: absolute;
                left: 2px;
                width: 28px;
                height: 28px;
                border-radius: 14px;
                background-color: white;
                margin: 2px;
            }

            /* 滑块样式 */
            QSlider::groove:horizontal {
                height: 6px;
                background: #e0e0e0;
                border-radius: 6px;
                margin: 0px;
            }

            QSlider::handle:horizontal {
                width: 24px;
                height: 24px;
                margin: -9px 0;
                background: #ffffff;
                border: 5px solid #4a90e2;
                border-radius: 12px;
            }

            QSlider::sub-page:horizontal {
                background: #4a90e2;
                border-radius: 5px;
            }

            /* 数值标签 */
            .value-label {
                font-size: 18px;
                color: #4a90e2;
                min-width: 80px;
                text-align: center;
                margin: 0px;
                padding: 0px;
                font-weight: bold;
            }

            /* 滑块容器 */
            .slider-container {
                background-color: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)

        def create_setting_item(title, switch, description=None, status=None, has_border=True):
            """创建单个设置项"""
            item_widget = QWidget()
            item_widget.setProperty("class", "setting-item")
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(25, 20, 25, 20)

            # 左侧文字区域 - 使用QWidget作为容器，设置尺寸策略
            text_widget = QWidget()
            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_widget.setLayout(text_layout)

            # 设置尺寸策略，允许水平扩展
            text_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            # 标题
            title_label = QLabel(title)
            title_label.setProperty("class", "setting-title")
            title_label.setWordWrap(True)
            title_label.setMinimumHeight(30)
            text_layout.addWidget(title_label)

            # 说明文字
            if description:
                desc_label = QLabel(description)
                desc_label.setProperty("class", "setting-description")
                desc_label.setWordWrap(True)
                desc_label.setMinimumHeight(40)
                text_layout.addWidget(desc_label)

            # 状态文字
            if status:
                status_label = QLabel(status)
                status_label.setProperty("class", "status-text")
                status_label.setMinimumHeight(25)
                text_layout.addWidget(status_label)

            text_layout.addStretch()

            # 右侧开关 - 固定宽度
            switch.setFixedWidth(80)  # 开关固定宽度

            # 添加控件到主布局
            item_layout.addWidget(text_widget, stretch=1)  # 文字区域可扩展
            item_layout.addWidget(switch, stretch=0, alignment=Qt.AlignRight)  # 开关固定宽度

            item_widget.setLayout(item_layout)
            return item_widget

        def create_slider_item(title, slider, value_label, description=None, has_border=True):
            """创建滑块设置项"""
            item_widget = QWidget()
            item_widget.setProperty("class", "setting-item")
            item_layout = QVBoxLayout()
            item_layout.setContentsMargins(25, 20, 25, 20)
            item_layout.setSpacing(2)

            # 顶部标题行 - 使用水平布局
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)

            # 标题标签 - 允许扩展
            title_label = QLabel(title)
            title_label.setProperty("class", "setting-title")
            title_label.setWordWrap(True)
            title_label.setMinimumHeight(30)
            top_layout.addWidget(title_label, stretch=1)  # 标题可扩展

            # 数值标签 - 固定宽度
            value_label.setProperty("class", "value-label")
            value_label.setMinimumHeight(30)
            value_label.setFixedWidth(80)  # 固定宽度
            top_layout.addWidget(value_label, stretch=0)

            item_layout.addLayout(top_layout)

            # 说明文字（如果有）
            if description:
                desc_label = QLabel(description)
                desc_label.setProperty("class", "setting-description")
                desc_label.setWordWrap(True)
                desc_label.setMinimumHeight(25)
                item_layout.addWidget(desc_label)
                item_layout.setSpacing(2)

            # 滑块 - 设置尺寸策略
            slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            slider.setMinimumHeight(35)
            item_layout.addWidget(slider)

            item_widget.setLayout(item_layout)
            return item_widget

        def create_group_title(title):
            """创建分组标题"""
            title_label = QLabel(title)
            title_label.setProperty("class", "group-title")
            title_label.setMinimumHeight(50)
            return title_label

            # 创建控件
            # 大小基数滑块

        self.size_ratio_base_label = QLabel(f"{config.size_ratio_base:.1f}")
        self.size_ratio_base_slider = QSlider(Qt.Horizontal, self)
        self.size_ratio_base_slider.setRange(1, 100)
        self.size_ratio_base_slider.setValue(int(config.size_ratio_base * 10))
        self.size_ratio_base_slider.valueChanged.connect(self._on_size_ratio_base_changed)

        # 屏幕循环连接功能开关
        self.screen_connect_check = QCheckBox(self)
        self.screen_connect_check.setChecked(config.screen_connect_enabled)
        self.screen_connect_check.stateChanged.connect(self._on_screen_connect_changed)

        # 拖拽跟随功能开关
        self.drag_follow_check = QCheckBox(self)
        self.drag_follow_check.setChecked(config.drag_follow_enabled)
        self.drag_follow_check.stateChanged.connect(self._on_drag_follow_changed)

        # 点击穿透开关
        self.click_through_check = QCheckBox(self)
        self.click_through_check.setChecked(config.click_through_enabled)
        self.click_through_check.stateChanged.connect(self._on_click_through_changed)

        # 抛掷功能开关
        self.throw_follow_check = QCheckBox(self)
        self.throw_follow_check.setChecked(config.throw_follow_enabled)
        self.throw_follow_check.stateChanged.connect(self._on_throw_follow_changed)

        # 反弹抛掷功能开关
        self.throw_bounce_check = QCheckBox(self)
        self.throw_bounce_check.setChecked(config.throw_follow_rebound_enabled)
        self.throw_bounce_check.stateChanged.connect(self._on_throw_bounce_changed)

        # 反弹损失因数滑块
        self.throw_follow_rebound_ratio_label = QLabel(f"{config.throw_follow_rebound_ratio:.2f}")
        self.throw_follow_rebound_ratio_slider = QSlider(Qt.Horizontal, self)
        self.throw_follow_rebound_ratio_slider.setRange(1, 100)
        self.throw_follow_rebound_ratio_slider.setValue(int(config.throw_follow_rebound_ratio * 100))
        self.throw_follow_rebound_ratio_slider.valueChanged.connect(self._on_throw_follow_rebound_ratio_changed)

        # 鼠标跟随开关
        self.mouse_follow_check = QCheckBox(self)
        self.mouse_follow_check.setChecked(config.mouse_follow_enabled)
        self.mouse_follow_check.stateChanged.connect(self._on_mouse_follow_changed)

        # 跟随速度滑块
        self.mouse_follow_speed_label = QLabel(f"{config.mouse_follow_speed:.1f}")
        self.mouse_follow_speed_slider = QSlider(Qt.Horizontal, self)
        self.mouse_follow_speed_slider.setRange(1, 100)
        self.mouse_follow_speed_slider.setValue(int(config.mouse_follow_speed * 10))
        self.mouse_follow_speed_slider.valueChanged.connect(self._on_mouse_follow_speed_changed)

        # 变大功能开关
        self.bigger_check = QCheckBox(self)
        self.bigger_check.setChecked(config.bigger_enabled)
        self.bigger_check.stateChanged.connect(self._on_bigger_changed)

        # 变大比例滑块
        self.bigger_max_size_ratio_label = QLabel(f"{config.bigger_max_size_ratio:.1f}")
        self.bigger_max_ratio_slider = QSlider(Qt.Horizontal, self)
        self.bigger_max_ratio_slider.setRange(10, 200)
        self.bigger_max_ratio_slider.setValue(int(config.bigger_max_size_ratio * 10))
        self.bigger_max_ratio_slider.valueChanged.connect(self._on_bigger_max_size_ratio_changed)

        # 等待时间滑块
        self.wait_label = QLabel(f"{config.bigger_wait_time / 60 / 1000:.1f}分钟")
        self.wait_slider = QSlider(Qt.Horizontal, self)
        self.wait_slider.setRange(1, 240)
        self.wait_slider.setValue(int(config.bigger_wait_time / 60 / 1000))
        self.wait_slider.valueChanged.connect(self._on_wait_changed)


        # 托盘消息开关
        self.tray_message_check = QCheckBox(self)
        self.tray_message_check.setChecked(config.tray_msg_enabled)
        self.tray_message_check.stateChanged.connect(self._on_tray_message_changed)

        # 创建布局
        layout.addWidget(create_group_title("基本功能"))
        layout.addWidget(create_slider_item("大小基数", self.size_ratio_base_slider, self.size_ratio_base_label,
                                            "调整窗口的基准大小比例（默认1.0）"))
        layout.addWidget(create_setting_item("屏幕循环连接", self.screen_connect_check,
                                             "左边消失，右边出现；右边消失，左边出现..."))

        layout.addWidget(create_setting_item("点击穿透", self.click_through_check,
                                             "鼠标就点不到我了，除非，仅按下左Ctrl键"))

        layout.addWidget(create_group_title("拖动抛掷"))
        layout.addWidget(create_setting_item("单击拖动", self.drag_follow_check,
                                             "鼠标左键可以拖动,移来移去..."))
        layout.addWidget(create_setting_item("重力抛掷", self.throw_follow_check,
                                             "拖动结束时，会被丢出去，自由落体"))
        layout.addWidget(create_setting_item("重力抛掷-反弹模式", self.throw_bounce_check,
                                             "重力抛掷开启的情况下，碰到屏幕边缘时会反弹"))
        layout.addWidget(create_slider_item("反弹因数", self.throw_follow_rebound_ratio_slider,
                                            self.throw_follow_rebound_ratio_label,
                                            "反弹因数越大，损失的能量越小（默认0.8）", False))

        layout.addWidget(create_group_title("鼠标跟随"))
        layout.addWidget(create_setting_item("鼠标跟随", self.mouse_follow_check,
                                             "鼠标移动时，会跟随移动到鼠标右下角（按住左Ctrl键时，会停止跟随）"))
        layout.addWidget(create_slider_item("跟随速度", self.mouse_follow_speed_slider,
                                            self.mouse_follow_speed_label,
                                            "值越大，跟随鼠标越快（默认5.0）", False))

        layout.addWidget(create_group_title("休息提醒"))
        layout.addWidget(create_setting_item("休息提醒", self.bigger_check,
                                             "定时长大变大，提醒该休息..."))
        layout.addWidget(create_slider_item("长大等待时间", self.wait_slider, self.wait_label,
                                            "多长时间后触发变大提醒（默认45分钟）"))
        layout.addWidget(create_slider_item("变大比例", self.bigger_max_ratio_slider,
                                            self.bigger_max_size_ratio_label,
                                            "变大的最大倍数（默认10），注意，如果 基数 × 倍数 > 15, 可能大量消耗系统资源", False))

        layout.addWidget(create_group_title("托盘消息"))
        layout.addWidget(create_setting_item("托盘消息", self.tray_message_check,
                                             "在系统托盘的左侧显示消息通知"))

        layout.addStretch()

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
                        f"图片模式: {self.parent.mode_manager.get_cur_mode().get_title_name()}"
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
        logger.info(f"设置，用户{'开启' if state else '关闭'} 屏幕循环连接 功能")

    def _on_drag_follow_changed(self, state):
        """处理拖动跟随功能切换"""
        config.drag_follow_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 单击拖动 功能")

    def _on_throw_follow_changed(self, state):
        """处理抛出跟随功能切换"""
        config.throw_follow_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 重力抛掷 功能")

    def _on_throw_bounce_changed(self, state):
        """处理反弹抛掷功能切换"""
        config.throw_follow_rebound_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 抛掷反弹 功能")

    def _on_throw_follow_rebound_ratio_changed(self, value):
        """处理反弹比例设置变化"""
        ratio = value / 100
        config.throw_follow_rebound_ratio = ratio
        self.throw_follow_rebound_ratio_label.setText(f"{ratio:.2f}")
        logger.info(f"设置，用户设置反弹损失因数为: {ratio}")

    def _on_mouse_follow_changed(self, state):
        """处理鼠标跟随功能切换"""
        config.mouse_follow_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}鼠标跟随功能")

    def _on_mouse_follow_speed_changed(self, value):
        """处理速度设置变化"""
        speed = value / 10
        config.mouse_follow_speed = speed
        self.mouse_follow_speed_label.setText(f"{speed:.1f}")
        logger.info(f"设置，用户设置跟随速度为: {speed}")

    def _on_click_through_changed(self, state):
        """处理点击穿透功能切换"""
        config.click_through_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}点击穿透功能")

    def _on_bigger_changed(self, state):
        """处理变大功能切换"""
        config.bigger_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}变大功能")

    def _on_size_ratio_base_changed(self, value):
        """处理标准大小比例设置变化"""
        config.size_ratio_base = value / 10
        self.size_ratio_base_label.setText(f"{config.size_ratio_base:.1f}")
        logger.info(f"设置，用户设置标准大小比例为: {config.size_ratio_base}")

    def _on_bigger_max_size_ratio_changed(self, value):
        """处理变大最大比例设置变化"""
        config.bigger_max_size_ratio = value / 10
        self.bigger_max_size_ratio_label.setText(f"{config.bigger_max_size_ratio:.1f}")
        logger.info(f"设置，用户设置变大最大比例为: {config.bigger_max_size_ratio}")

    def _on_wait_changed(self, value):
        """处理变大等待时间设置变化"""
        config.bigger_wait_time = value * 60 * 1000
        self.wait_label.setText(f"{value}分钟")
        logger.info(f"设置，用户设置变大等待时间为: {value}分钟")

    def _on_tray_message_changed(self, state):
        """处理托盘消息功能切换"""
        config.tray_msg_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}托盘消息功能")

    def closeEvent(self, event):
        """关闭窗口时停止定时器"""
        self.info_timer.stop()
        super().closeEvent(event)
