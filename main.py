import sys
import math
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPixmap


class FollowAndDragWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 始终在最前
            Qt.Tool  # 不显示在任务栏
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景

        # 加载图片
        self.image_label = QLabel(self)
        pixmap = QPixmap("image.png")  # 替换为你的图片路径
        if pixmap.isNull():
            print("无法加载图片，请检查路径")
            sys.exit(1)

        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        # 调整窗口大小为图片大小
        self.resize(pixmap.size())


        # 鼠标交互相关变量
        self.dragging = False
        self.offset = QPoint()
        self.follow_speed = 0.1  # 跟随速度系数 (0-1)

        # 初始位置：屏幕中央
        screen_geometry = QApplication.desktop().screenGeometry()
        self.move(screen_geometry.center() - self.rect().center())

        # 设置定时器用于跟随鼠标
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.follow_mouse)
        self.timer.start(20)  # 每20毫秒更新一次

    def follow_mouse(self):
        if not self.dragging:
            # 获取鼠标和窗口的当前位置
            mouse_pos = self.mapFromGlobal(QApplication.desktop().cursor().pos())
            window_center = QPoint(self.width() // 2, self.height() // 2)

            # 计算移动方向向量
            direction = mouse_pos - window_center
            distance = math.sqrt(direction.x() ** 2 + direction.y() ** 2)

            # 如果距离足够大才移动
            if distance > 5:
                # 计算新位置（逐步靠近鼠标）
                new_pos = self.pos() + direction * self.follow_speed
                print(mouse_pos,new_pos)
                # self.move(new_pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 开始拖动
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            # 拖动状态下移动窗口
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 结束拖动
            self.dragging = False

    def mouseDoubleClickEvent(self, event):
        # 双击退出
        if event.button() == Qt.LeftButton:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = FollowAndDragWidget()
    widget.show()

    sys.exit(app.exec_())