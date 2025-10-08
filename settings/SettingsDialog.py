import os
import traceback

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QLabel, QWidget,
                             QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QTabWidget, QScrollArea, QApplication, )
from PyQt5.QtCore import Qt, QTimer, QPointF

from configs import config
from settings.TabWidget import TabWidget
from settings.create_setting_widgets import create_item_container, create_slider_item, create_group_title, create_setting_item, create_settings_item
from settings.settings_styles import settings_set_style, settings_tab_style
from utils.log_util import logger
from utils.pos_util import point_to_tuple, pointf_to_tuple


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

        # 信息页更新定时器
        self.info_timer = QTimer(self)
        self.info_timer.timeout.connect(self.update_info_page)
        self.info_timer.start(200)  # 每500ms更新一次信息页

        # 确保窗口关闭时清理资源
        # self.destroyed.connect(self._cleanup)  # 绑定清理函数

    # def _cleanup(self):
    #     """窗口关闭时清理资源"""
    #     if hasattr(self, 'info_timer'):
    #         self.info_timer.stop()  # 停止定时器
    #         self.info_timer.deleteLater()  # 安全删除定时器
    #     print("SettingsDialog 窗口关闭时清理资源完成")
    #
    # def closeEvent(self, event):
    #     """重写 closeEvent，确保关闭时执行清理"""
    #     self._cleanup()
    #     super().closeEvent(event)  # 调用父类方法，确保正常关闭

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
        # print(hasattr(parent,'image_label'))
        # cls._instance.setZValue(5)
        cls._instance.show()
        cls._instance.activateWindow()

        # if hasattr(parent,'image_label'):
        #     cls._instance.stackUnder(parent.image_label)
        # cls._instance.raise_()

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
        self.tab_widget.addTab("设置", self.createSettingsTab())
        self.tab_widget.addTab("监控", self.createInfoTab())
        self.tab_widget.addTab("关于", self.createAboutTab())

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

    def createSettingsTab(self):
        """初始化纯设置页（淡蓝色主题+修复布局）"""
        # 创建主容器和滚动区域
        self.settings_tab = QWidget()

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
        self.settings_tab.setStyleSheet(settings_set_style)

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
        ],margin_left_add=50))
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
        return self.settings_tab

    def createInfoTab(self):
        """初始化纯信息监控页"""
        self.info_tab = QWidget()

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

        # 抛掷速度
        self.throw_speed_label = QLabel("抛掷速度: --", self)
        layout.addWidget(self.throw_speed_label)

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
        return self.info_tab

    def createAboutTab(self):
        """初始化关于页"""
        self.about_tab = QWidget()
        layout = QVBoxLayout()

        text = """
        关于本项目
        版本: 25100824
        作者: 初心cx
        感谢，部分素材图片来源: 芝麻球促销（作者，半江离）
        感谢，部分桌宠模式项目: Shimeji（作者，Kilkakon）"""
        layout.addWidget(QLabel(text, self))
        layout.addStretch()
        self.about_tab.setLayout(layout)
        return self.about_tab

    def update_info_page(self):
        """专门用于更新信息页的实时数据"""
        # print(f"self.isVisible={self.isVisible()},self.tab_widget.currentIndex()={self.tab_widget.currentIndex()}")

        if not self.isVisible() or self.tab_widget.currentIndex() != 1:  # 仅当信息页激活时更新
            return
        try:
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

                    # 抛掷速度
                    throw_follow_speed:QPointF =config.throw_follow_speed*1000
                    self.throw_speed_label.setText(
                        f"抛掷速度: ({throw_follow_speed.x(): >11,.2f}, {throw_follow_speed.y(): >11,.2f})"
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
                f"图片锚点位置(px): {point_to_tuple(config.anchor_pos)}"
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
        self.throw_follow_max_speed_label.setText(f"{config.throw_follow_max_speed_ms *1000:,}px/s")
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

    def closeEvent(self, event):
        """关闭窗口时停止定时器"""
        self.info_timer.stop()
        super().closeEvent(event)
