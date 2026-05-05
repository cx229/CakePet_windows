import traceback
from PyQt5.QtWidgets import (QLabel, QWidget,
                             QVBoxLayout)
from PyQt5.QtCore import QTimer, QPointF

from configs import config
from utils.log_util import logger
from utils.pos_util import point_to_tuple


class InfoWidget(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        self.initUI()

        self.info_timer = QTimer(self)  # 信息页更新定时器
        self.info_timer.timeout.connect(self.update_info_page)

    def start(self):
        self.update_info_page()
        self.info_timer.start(200)  # 每500ms更新一次信息页

    def stop(self):
        self.info_timer.stop()

    def initUI(self):
        """初始化UI"""
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
        self.setLayout(layout)

    def update_info_page(self):
        """专门用于更新信息页的实时数据"""
        try:
            print("XXXX")
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
                    throw_follow_speed: QPointF = config.throw_follow_speed * 1000
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
            traceback.print_exc()
            logger.error(f"更新监控页错误: {traceback.format_exc()}")
