import sys
import math
import traceback
import logging
import datetime
import os
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QSystemTrayIcon,
                             QMenu, QAction, QDialog, QVBoxLayout, QSlider,
                             QCheckBox, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon


def setup_logging():
    """设置日志系统"""
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # 生成日志文件名（带时间戳）
    log_filename = f"logs/mouse_follower_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理函数"""
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"未捕获的异常:\n{error_msg}")

    # 在GUI中显示错误信息
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("程序错误")
    msg_box.setText("程序发生错误，请查看日志")
    msg_box.setDetailedText(error_msg)
    msg_box.exec_()

    # 正常退出程序
    QApplication.quit()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.parent = parent
            self.setWindowTitle("鼠标跟随工具 - 设置")
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.setFixedSize(300, 250)

            layout = QVBoxLayout()

            # 跟随开关
            self.follow_check = QCheckBox("启用鼠标跟随", self)
            self.follow_check.setChecked(parent.follow_enabled)
            layout.addWidget(self.follow_check)

            # 跟随速度滑块
            self.speed_label = QLabel(f"跟随速度: {parent.follow_speed:.1f}", self)
            layout.addWidget(self.speed_label)

            self.speed_slider = QSlider(Qt.Horizontal, self)
            self.speed_slider.setRange(1, 20)
            self.speed_slider.setValue(int(parent.follow_speed * 10))
            self.speed_slider.valueChanged.connect(self.update_speed_label)
            layout.addWidget(self.speed_slider)

            # 拖动开关
            self.drag_check = QCheckBox("启用拖动功能", self)
            self.drag_check.setChecked(parent.drag_enabled)
            layout.addWidget(self.drag_check)

            # 退出按钮
            self.exit_btn = QPushButton("退出程序", self)
            self.exit_btn.clicked.connect(self.exit_program)
            layout.addWidget(self.exit_btn)

            # 确定按钮
            self.ok_btn = QPushButton("确定", self)
            self.ok_btn.clicked.connect(self.accept)
            layout.addWidget(self.ok_btn)

            self.setLayout(layout)

            # 连接信号
            self.follow_check.stateChanged.connect(parent.toggle_follow)
            self.drag_check.stateChanged.connect(parent.toggle_drag)
            self.speed_slider.valueChanged.connect(
                lambda v: setattr(parent, 'follow_speed', v / 10))

            logger.info("设置窗口已创建")

        except Exception as e:
            logger.error(f"SettingsDialog初始化错误: {traceback.format_exc()}")
            raise

    def update_speed_label(self, value):
        """更新速度显示标签"""
        self.speed_label.setText(f"跟随速度: {value / 10:.1f}")

    def exit_program(self):
        """退出程序"""
        logger.info("用户通过设置窗口退出程序")
        self.parent.close()


class FollowAndDragWidget(QWidget):
    def __init__(self):
        try:
            super().__init__()

            # 初始化设置
            self.follow_enabled = True
            self.drag_enabled = True
            self.follow_speed = 0.1

            # 跟随状态跟踪
            self.follow_start_time = None
            self.last_follow_time = None
            self.is_following = False

            # 设置窗口属性
            self.setWindowFlags(
                Qt.FramelessWindowHint |  # 无边框
                Qt.WindowStaysOnTopHint |  # 始终在最前
                Qt.Tool  # 不显示在任务栏
            )
            self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景

            # 加载主图片
            self.image_label = QLabel(self)
            try:
                pixmap = QPixmap("image.png")  # 主显示图片
                if pixmap.isNull():
                    raise FileNotFoundError("无法加载图片 image.png")
                logger.info("主图片加载成功")
            except Exception as e:
                logger.error(f"图片加载错误: {traceback.format_exc()}")
                # 创建默认图片
                pixmap = QPixmap(100, 100)
                pixmap.fill(Qt.red)
                self.image_label.setText("图片加载失败")

            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)

            # 调整窗口大小为图片大小
            self.resize(pixmap.size())

            # 鼠标交互相关变量
            self.dragging = False
            self.offset = QPoint()
            self.tray_menu = None  # 存储托盘菜单引用

            # 初始位置：屏幕中央
            screen_geometry = QApplication.desktop().screenGeometry()
            self.move(screen_geometry.center() - self.rect().center())

            # 设置定时器用于跟随鼠标
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.follow_mouse)
            self.timer.start(20)  # 每20毫秒更新一次

            # 创建系统托盘图标
            self.create_tray_icon()

            logger.info("程序启动成功")

        except Exception as e:
            logger.error(f"FollowAndDragWidget初始化错误: {traceback.format_exc()}")
            raise

    def create_tray_icon(self):
        try:
            # 加载托盘图标
            try:
                tray_icon = QPixmap("image.png")  # 任务栏图标
                if tray_icon.isNull():
                    raise FileNotFoundError("无法加载托盘图标 image2.png")
                logger.info("托盘图标加载成功")
            except Exception as e:
                logger.error(f"托盘图标加载错误: {traceback.format_exc()}")
                tray_icon = QPixmap(32, 32)
                tray_icon.fill(Qt.blue)

            self.tray = QSystemTrayIcon(self)
            self.tray.setIcon(QIcon(tray_icon))

            # 创建托盘菜单
            self.create_context_menu()

            self.tray.show()
            logger.info("系统托盘图标创建成功")

        except Exception as e:
            logger.error(f"创建托盘图标错误: {traceback.format_exc()}")
            raise

    def create_context_menu(self):
        """创建右键菜单(用于托盘和窗口右键)"""
        try:
            menu = QMenu()

            # 跟随开关
            follow_action = QAction("鼠标跟随", self, checkable=True)
            follow_action.setChecked(self.follow_enabled)
            follow_action.triggered.connect(self.toggle_follow)
            menu.addAction(follow_action)

            # 拖动开关
            drag_action = QAction("拖动功能", self, checkable=True)
            drag_action.setChecked(self.drag_enabled)
            drag_action.triggered.connect(self.toggle_drag)
            menu.addAction(drag_action)

            menu.addSeparator()

            # 设置
            settings_action = QAction("设置", self)
            settings_action.triggered.connect(self.show_settings)
            menu.addAction(settings_action)

            menu.addSeparator()

            # 退出
            exit_action = QAction("退出", self)
            exit_action.triggered.connect(self.close)
            menu.addAction(exit_action)

            # 同时设置给托盘和窗口
            self.tray.setContextMenu(menu)
            self.tray_menu = menu  # 保存引用

            # 双击托盘图标显示/隐藏窗口
            self.tray.activated.connect(self.toggle_window_visibility)

            logger.info("右键菜单创建成功")

        except Exception as e:
            logger.error(f"创建右键菜单错误: {traceback.format_exc()}")
            raise

    def contextMenuEvent(self, event):
        """重写右键菜单事件"""
        try:
            if self.tray_menu:
                self.tray_menu.exec_(event.globalPos())
                logger.info("用户右键点击窗口弹出菜单")
        except Exception as e:
            logger.error(f"显示右键菜单错误: {traceback.format_exc()}")

    def toggle_window_visibility(self, reason):
        try:
            if reason == QSystemTrayIcon.DoubleClick:
                if self.isVisible():
                    self.hide()
                    logger.info("用户双击托盘图标隐藏窗口")
                else:
                    self.show()
                    logger.info("用户双击托盘图标显示窗口")
        except Exception as e:
            logger.error(f"切换窗口可见性错误: {traceback.format_exc()}")

    def toggle_follow(self, checked):
        try:
            self.follow_enabled = checked
            action = "开启" if checked else "关闭"
            logger.info(f"用户{action}鼠标跟随功能")
        except Exception as e:
            logger.error(f"切换跟随状态错误: {traceback.format_exc()}")

    def toggle_drag(self, checked):
        try:
            self.drag_enabled = checked
            action = "开启" if checked else "关闭"
            logger.info(f"用户{action}拖动功能")
        except Exception as e:
            logger.error(f"切换拖动状态错误: {traceback.format_exc()}")

    def show_settings(self):
        try:
            logger.info("用户打开设置窗口")
            dialog = SettingsDialog(self)
            dialog.exec_()
            logger.info("设置窗口关闭")
        except Exception as e:
            logger.error(f"显示设置对话框错误: {traceback.format_exc()}")

    def follow_mouse(self):
        try:
            current_time = datetime.datetime.now()

            if self.follow_enabled and not self.dragging:
                # 获取鼠标和窗口的当前位置
                mouse_pos = self.mapFromGlobal(QApplication.desktop().cursor().pos())
                # window_center = QPoint(self.width() // 2, self.height() // 2)
                window_center=QPoint(0,0) # 修改为左上角跟随

                # 计算移动方向向量
                direction = mouse_pos - window_center
                distance = math.sqrt(direction.x() ** 2 + direction.y() ** 2)

                # 如果距离足够大才移动
                if distance > 5:
                    # 记录跟随开始
                    if not self.is_following:
                        self.follow_start_time = current_time
                        self.is_following = True
                        logger.info("开始跟随鼠标移动")

                    # 计算新位置（逐步靠近鼠标）
                    new_pos = self.pos() + direction * self.follow_speed
                    self.move(new_pos)

                    self.last_follow_time = current_time
                else:
                    # 如果之前正在跟随，现在停止了，记录跟随结束
                    if self.is_following:
                        duration = (current_time - self.follow_start_time).total_seconds()
                        logger.info(f"跟随鼠标移动结束，持续时间: {duration:.2f}秒")
                        self.is_following = False
            else:
                # 如果之前正在跟随，现在停止了（因为拖动或关闭跟随），记录跟随结束
                if self.is_following:
                    duration = (current_time - self.follow_start_time).total_seconds()
                    logger.info(f"跟随鼠标移动结束，持续时间: {duration:.2f}秒")
                    self.is_following = False

        except Exception as e:
            logger.error(f"跟随鼠标错误: {traceback.format_exc()}")

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.LeftButton and self.drag_enabled:
                # 开始拖动
                self.dragging = True
                self.offset = event.pos()
                logger.info("用户开始拖动图片")
        except Exception as e:
            logger.error(f"鼠标按下事件错误: {traceback.format_exc()}")

    def mouseMoveEvent(self, event):
        try:
            if self.dragging and self.drag_enabled:
                # 拖动状态下移动窗口
                self.move(event.globalPos() - self.offset)
        except Exception as e:
            logger.error(f"鼠标移动事件错误: {traceback.format_exc()}")

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.LeftButton and self.dragging:
                # 结束拖动
                self.dragging = False
                logger.info("用户结束拖动图片")
        except Exception as e:
            logger.error(f"鼠标释放事件错误: {traceback.format_exc()}")

    def closeEvent(self, event):
        try:
            # 清理资源
            self.timer.stop()
            self.tray.hide()
            logger.info("程序正常退出")
            event.accept()
        except Exception as e:
            logger.error(f"关闭事件错误: {traceback.format_exc()}")
            event.accept()


if __name__ == "__main__":
    try:
        # 设置全局异常处理
        sys.excepthook = handle_exception

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # 防止关闭窗口时退出程序

        widget = FollowAndDragWidget()
        widget.show()

        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"程序启动错误: {traceback.format_exc()}")
        sys.exit(1)