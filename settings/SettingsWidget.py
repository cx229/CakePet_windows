
from PyQt5.QtWidgets import (QLabel, QWidget,
                              QVBoxLayout, QSlider,
                             QCheckBox,  QScrollArea )
from PyQt5.QtCore import Qt

from configs import config
from settings.create_setting_widgets import create_item_container, create_slider_item, create_group_title, create_setting_item, create_settings_item
from settings.settings_styles import settings_set_style
from utils.log_util import logger

class SettingsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def start(self):
        pass
    def stop(self):
        pass

    def initUI(self):
        """初始化UI"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 淡蓝色主题样式表
        self.setStyleSheet(settings_set_style)

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

        # 运动速度滑块
        self.follow_update_interval_label = QLabel(f"{config.follow_update_interval}ms")
        self.follow_update_interval_slider = QSlider(Qt.Horizontal, self)
        self.follow_update_interval_slider.setRange(1, 50)
        self.follow_update_interval_slider.setValue(config.follow_update_interval)
        self.follow_update_interval_slider.valueChanged.connect(self._on_follow_update_interval_changed)

        # 抛掷功能开关
        self.throw_follow_check = QCheckBox(self)
        self.throw_follow_check.setChecked(config.throw_follow_enabled)
        self.throw_follow_check.stateChanged.connect(self._on_throw_follow_changed)

        # 重力加速度滑块
        self.throw_follow_gravity_label = QLabel(f"{int(config.throw_follow_gravity * 1000000):,}px/s²")
        self.throw_follow_gravity_slider = QSlider(Qt.Horizontal, self)
        self.throw_follow_gravity_slider.setRange(0, 50)
        self.throw_follow_gravity_slider.setValue(int(config.throw_follow_gravity * 1000))
        self.throw_follow_gravity_slider.valueChanged.connect(self._on_throw_follow_gravity_changed)

        # 抛掷最大速度滑块
        self.throw_follow_max_speed_label = QLabel(f"{config.throw_follow_max_speed_ms * 1000:,}px/s")
        self.throw_follow_max_speed_ms_slider = QSlider(Qt.Horizontal, self)
        self.throw_follow_max_speed_ms_slider.setRange(1, 50)
        self.throw_follow_max_speed_ms_slider.setValue(int(config.throw_follow_max_speed_ms))
        self.throw_follow_max_speed_ms_slider.valueChanged.connect(self._on_throw_follow_max_speed_ms_changed)

        # 反弹抛掷功能开关
        self.throw_rebounce_check = QCheckBox(self)
        self.throw_rebounce_check.setChecked(config.throw_follow_rebound_enabled)
        self.throw_rebounce_check.stateChanged.connect(self._on_throw_rebounce_changed)

        # 反弹 -上 开关
        self.throw_rebounce_up_check = QCheckBox(self)
        self.throw_rebounce_up_check.setChecked(config.throw_follow_rebound_up_enabled)
        self.throw_rebounce_up_check.stateChanged.connect(self._on_throw_rebounce_up_changed)

        # 反弹 -下 开关
        self.throw_rebounce_down_check = QCheckBox(self)
        self.throw_rebounce_down_check.setChecked(config.throw_follow_rebound_down_enabled)
        self.throw_rebounce_down_check.stateChanged.connect(self._on_throw_rebounce_down_changed)

        # 反弹 -左右 开关
        self.throw_rebounce_left_right_check = QCheckBox(self)
        self.throw_rebounce_left_right_check.setChecked(config.throw_follow_rebound_left_right_enabled)
        self.throw_rebounce_left_right_check.stateChanged.connect(self._on_throw_rebounce_left_right_changed)

        # 反弹损失因数滑块
        self.throw_follow_rebound_ratio_label = QLabel(f"{config.throw_follow_rebound_ratio:.2f}")
        self.throw_follow_rebound_ratio_slider = QSlider(Qt.Horizontal, self)
        self.throw_follow_rebound_ratio_slider.setRange(1, 150)
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
        self.wait_label = QLabel(f"{int(config.bigger_wait_time / 60 / 1000)}分钟")
        self.wait_slider = QSlider(Qt.Horizontal, self)
        self.wait_slider.setRange(1, 240)
        self.wait_slider.setValue(int(config.bigger_wait_time / 60 / 1000))
        self.wait_slider.valueChanged.connect(self._on_wait_changed)

        # 托盘消息开关
        self.tray_msg_check = QCheckBox(self)
        self.tray_msg_check.setChecked(config.tray_msg_enabled)
        self.tray_msg_check.stateChanged.connect(self._on_tray_msg_enabled_changed)

        # 托盘消息-键盘信息
        self.tray_key_info_check = QCheckBox(self)
        self.tray_key_info_check.setChecked(config.tray_key_info_enabled)
        self.tray_key_info_check.stateChanged.connect(self._on_tray_key_info_changed)

        # 托盘消息-位置-托盘
        self.tray_msg_position_tray_check = QCheckBox(self)
        self.tray_msg_position_tray_check.setChecked(config.tray_msg_position_tray)
        self.tray_msg_position_tray_check.stateChanged.connect(self._on_tray_msg_position_tray_changed)

        # 托盘颜色-白色
        self.tray_msg_color_white_check = QCheckBox(self)
        self.tray_msg_color_white_check.setChecked(config.tray_msg_color_white)
        self.tray_msg_color_white_check.stateChanged.connect(self._on_tray_msg_color_white_changed)

        # 托盘边距
        self.tray_msg_margin_label = QLabel(f"{config.tray_msg_margin}")
        self.tray_msg_margin_slider = QSlider(Qt.Horizontal, self)
        self.tray_msg_margin_slider.setRange(0, 300)
        self.tray_msg_margin_slider.setValue(int(config.tray_msg_margin / 10))
        self.tray_msg_margin_slider.valueChanged.connect(self._on_tray_msg_margin_changed)

        # 仅记录错误日志开关
        self.logger_only_error_check = QCheckBox(self)
        self.logger_only_error_check.setChecked(config.logger_only_error)
        self.logger_only_error_check.stateChanged.connect(self._on_logger_only_error_changed)

        # 创建布局
        layout.addWidget(create_group_title("基本功能"))
        layout.addWidget(create_slider_item("大小基数", self.size_ratio_base_slider, self.size_ratio_base_label,
                                            "调整大小基数比例（默认1.5）"))
        layout.addWidget(create_setting_item("屏幕循环连接", self.screen_connect_check,
                                             "传送门：左边消失，右边出现；右边消失，左边出现......"))
        layout.addWidget(create_setting_item("点击穿透", self.click_through_check,
                                             "鼠标就点不到我了，除非，仅按下左Ctrl键"))

        layout.addWidget(create_group_title("运动功能"))
        layout.addWidget(create_slider_item("刷新速度", self.follow_update_interval_slider, self.follow_update_interval_label,
                                            "运动状态下画面刷新速度，数值越小，画面越流畅（默认3ms）"))
        layout.addWidget(create_setting_item("单击拖动", self.drag_follow_check,
                                             "鼠标左键长按可以拖动,移来移去....."))
        layout.addWidget(create_setting_item("重力抛掷", self.throw_follow_check,
                                             "拖动结束时，会被丢出去（关闭后，将不会上下移动，也不会左右跑动）\n"
                                             "注意：如果关闭，要是走丢了，也就不能传送到地面了..."))
        layout.addWidget(create_item_container(check_widget=self.throw_follow_check, widgets=[
            create_slider_item("重力加速度", self.throw_follow_gravity_slider, self.throw_follow_gravity_label,
                               "数值越大，下落加速越快（默认10,000px/s²）"),
            create_slider_item("最大速度", self.throw_follow_max_speed_ms_slider, self.throw_follow_max_speed_label,
                               "抛掷时的最大速度，禁止超速！（默认10,000px/s）")
        ], margin_left_add=50))
        layout.addWidget(create_setting_item("重力抛掷-反弹模式", self.throw_rebounce_check,
                                             "重力抛掷开启时，碰到屏幕边缘时会反弹（关闭后，可以飞向太空）\n"
                                             "多屏幕下，即使关闭左右反弹，但目的地不存在时，还是会反弹的哦",
                                             margin_left_add=50))
        layout.addWidget(create_item_container(check_widget=self.throw_rebounce_check, widgets=[
            create_settings_item(["上反弹", "下反弹", "左右反弹"],
                                 [self.throw_rebounce_up_check, self.throw_rebounce_down_check, self.throw_rebounce_left_right_check], ),
            create_slider_item("反弹因数", self.throw_follow_rebound_ratio_slider,
                               self.throw_follow_rebound_ratio_label,
                               "反弹因数越大，损失的能量越小（默认0.80）\n"
                               "如果大于1.0，那么每次反弹就会加速！")
        ], margin_left_add=100))

        layout.addWidget(create_setting_item("鼠标跟随", self.mouse_follow_check,
                                             "非拖动和抛掷时，跟随移动到鼠标右下角（按住左Ctrl键时，会停止跟随）"))

        layout.addWidget(create_item_container(check_widget=self.mouse_follow_check, widgets=[
            create_slider_item("跟随速度", self.mouse_follow_speed_slider,
                               self.mouse_follow_speed_label,
                               "值越大，跟随鼠标越快（默认5.0）", False)
        ], margin_left_add=50))

        layout.addWidget(create_group_title("休息提醒"))
        layout.addWidget(create_setting_item("休息提醒", self.bigger_check,
                                             "定时长大变大，提醒该休息..."))
        layout.addWidget(create_item_container(check_widget=self.bigger_check, widgets=[
            create_slider_item("长大时间", self.wait_slider, self.wait_label,
                               "多长时间后触发变大提醒（默认45分钟）"),
            create_slider_item("变大比例", self.bigger_max_ratio_slider,
                               self.bigger_max_size_ratio_label,
                               "变大的最大倍数（默认10.0）\n注意，如果 基数 × 倍数 > 15, 可能大量消耗系统资源", False)
        ], margin_left_add=50))

        layout.addWidget(create_group_title("托盘消息"))
        layout.addWidget(create_setting_item("托盘消息", self.tray_msg_check,
                                             "在系统托盘的左侧显示消息通知"))

        layout.addWidget(create_item_container(check_widget=self.tray_msg_check, widgets=[
            create_setting_item("显示按键信息", self.tray_key_info_check,
                                "打字速度，今日打字总数（关闭后，将不会更新总数）"),
            create_setting_item("位置-托盘", self.tray_msg_position_tray_check,
                                "开启：系统托盘的左侧显示，关闭：在任务栏左侧显示"),
            create_setting_item("颜色-白色", self.tray_msg_color_white_check,
                                "开启：白色，关闭：黑色"),
            create_slider_item("边距", self.tray_msg_margin_slider,
                               self.tray_msg_margin_label,
                               "托盘消息与任务栏的边距（默认0）", False)
        ], margin_left_add=50))
        layout.addWidget(create_group_title("其他"))
        layout.addWidget(create_setting_item("仅记录错误日志", self.logger_only_error_check,
                                             "仅记录错误日志，而不是所有日志"))
        layout.addStretch()
        self.setLayout(layout)



    def _on_screen_connect_changed(self, state):
        """处理屏幕循环连接功能切换"""
        config.screen_connect_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 屏幕循环连接 功能")

    def _on_drag_follow_changed(self, state):
        """处理拖动跟随功能切换"""
        config.drag_follow_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 单击拖动 功能")

    def _on_follow_update_interval_changed(self, value):
        """处理运动速度设置变化"""
        config.follow_update_interval = value
        self.follow_update_interval_label.setText(f"{value}ms")
        logger.info(f"设置，用户设置运动速度为: {value}ms")

    def _on_throw_follow_changed(self, state):
        """处理抛出跟随功能切换"""
        config.throw_follow_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 重力抛掷 功能")

    def _on_throw_follow_gravity_changed(self, value):
        """处理重力加速度设置变化"""
        config.throw_follow_gravity = value / 1000
        self.throw_follow_gravity_label.setText(f"{int(config.throw_follow_gravity * 1000000):,}px/s²")
        logger.info(f"设置，用户设置重力加速度为: {int(config.throw_follow_gravity * 1000000):,}px/s²")

    def _on_throw_follow_max_speed_ms_changed(self, value):
        """处理抛掷最大速度设置变化"""
        config.throw_follow_max_speed_ms = value
        self.throw_follow_max_speed_label.setText(f"{config.throw_follow_max_speed_ms * 1000:,}px/s")
        logger.info(f"设置，用户设置抛掷最大速度为: {config.throw_follow_max_speed_ms * 1000:,}px/s")

    def _on_throw_rebounce_changed(self, state):
        """处理反弹抛掷功能切换"""
        config.throw_follow_rebound_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 抛掷反弹 功能")

    def _on_throw_rebounce_up_changed(self, state):
        """处理反弹-上 功能切换"""
        config.throw_follow_rebound_up_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 反弹-上 功能")

    def _on_throw_rebounce_down_changed(self, state):
        """处理反弹-下 功能切换"""
        config.throw_follow_rebound_down_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 反弹-下 功能")

    def _on_throw_rebounce_left_right_changed(self, state):
        """处理反弹-左右 功能切换"""
        config.throw_follow_rebound_left_right_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'} 反弹-左右 功能")

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

    def _on_tray_msg_enabled_changed(self, state):
        """处理托盘消息功能切换"""
        config.tray_msg_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}托盘消息功能")

    def _on_tray_key_info_changed(self, state):
        """处理托盘消息-键盘信息切换"""
        config.tray_key_info_enabled = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}托盘消息-键盘信息")

    def _on_tray_msg_position_tray_changed(self, state):
        """处理托盘消息位置-托盘切换"""
        config.tray_msg_position_tray = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}托盘消息模式-托盘")

    def _on_tray_msg_color_white_changed(self, state):
        """处理托盘消息颜色切换"""
        config.tray_msg_color_white = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}托盘消息颜色-白色")

    def _on_tray_msg_margin_changed(self, value):
        """处理托盘消息边距切换"""
        config.tray_msg_margin = value * 10
        self.tray_msg_margin_label.setText(f"{value * 10}")
        logger.info(f"设置，用户设置托盘消息边距为: {value * 10}")

    # 仅记录错误日志开关
    def _on_logger_only_error_changed(self, state):
        """处理仅记录错误日志开关切换"""
        config.logger_only_error = bool(state)
        logger.info(f"设置，用户{'开启' if state else '关闭'}仅记录错误日志")
