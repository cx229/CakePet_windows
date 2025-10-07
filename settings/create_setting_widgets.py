import os
import traceback

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox, QHBoxLayout, QTabWidget, QGroupBox, QScrollArea, QSizePolicy, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup

from configs import config
from utils.log_util import logger
from utils.pos_util import point_to_tuple


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

    # def create_item_container(check_widget: QCheckBox, widgets: list[QWidget]):
    #     """创建单个设置项容器"""
    #     tray_settings_container = QWidget()
    #     tray_settings_layout = QVBoxLayout()
    #     tray_settings_layout.setContentsMargins(0, 0, 0, 0)
    #     tray_settings_container.setLayout(tray_settings_layout)
    #     for widget in widgets:
    #         tray_settings_layout.addWidget(widget)
    #
    #     def _update_tray_settings_visibility():
    #         tray_settings_container.setVisible(check_widget.isChecked())
    #
    #     check_widget.toggled.connect(_update_tray_settings_visibility)
    #     # _update_tray_settings_visibility()
    #     return tray_settings_container


def create_item_container(check_widget: QCheckBox, widgets: list[QWidget]):
    """创建带动画效果的设置项容器（修复默认true时的问题）"""
    container = QWidget()
    container_layout = QVBoxLayout()
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setSpacing(0)
    container.setLayout(container_layout)

    # 添加所有子控件
    for widget in widgets:
        container_layout.addWidget(widget)

    # 初始化动画系统
    container._animation = QPropertyAnimation(container, b"maximumHeight")
    container._animation.setDuration(200)
    container._animation.setEasingCurve(QEasingCurve.OutQuad)

    # 确保布局完全计算完成
    def init_container():
        # 计算并存储完整高度
        container._full_height = container.sizeHint().height()

        # 根据初始状态设置高度
        if check_widget.isChecked():
            container.setMaximumHeight(container._full_height)
            container.setMinimumHeight(0)
        else:
            container.setMaximumHeight(0)
            container.setMinimumHeight(0)

        # 强制布局更新
        container.layout().activate()
        container.updateGeometry()

        # 预先设置正确的可见性
        container.setVisible(check_widget.isChecked())

    # 增加延迟时间确保布局计算完成
    QTimer.singleShot(100, init_container)

    def update_visibility():
        """带动画的可见性更新"""
        # 确保_full_height已初始化
        if not hasattr(container, '_full_height'):
            container._full_height = container.sizeHint().height()

        # 停止当前动画
        container._animation.stop()

        # 清除之前的finished连接
        try:
            container._animation.finished.disconnect()
        except:
            pass

        if check_widget.isChecked():
            # 显示动画 - 使用当前高度作为起始值
            container.show()
            current_height = container.height()
            container._animation.setStartValue(current_height)
            container._animation.setEndValue(container._full_height)
        else:
            # 隐藏动画
            container._animation.setStartValue(container.height())
            container._animation.setEndValue(0)
            container._animation.finished.connect(lambda: container.hide())

        container._animation.start()

    # 连接信号
    check_widget.toggled.connect(update_visibility)

    return container
