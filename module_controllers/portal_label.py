import weakref

from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtWidgets import QLabel

from configs import config
from resmeta import Images


class ProbeLabel(QLabel):  # 探头标签
    def __init__(self, parent=None):
        super().__init__(parent)

        pixmap = QPixmap(Images.ProbeHead.S1.value.path)

        self.setPixmap(pixmap)


def handle_portal(target_anchor_pos, widget, turn_right=True, exit_flag=True):
    """ 处理边界情况
    :param target_anchor_pos: 目标锚点位置
    :param widget: 父窗口
    :param turn_right: 是否向右传送门
    :param exit_flag: True 表示进出口传送门，False 表示 入口 传送门
    """
    portal_widget = QLabel(widget)
    # portal_widget.setZValue(20)
    show_timer = QTimer(widget)

    # 设置对象名称以便调试
    portal_widget.setObjectName("portal_widget")
    show_timer.setObjectName("portal_timer")

    # 使用弱引用避免循环引用
    weak_portal = weakref.ref(portal_widget)
    weak_timer = weakref.ref(show_timer)

    def cleanup():
        """清理资源"""
        portal = weak_portal()
        timer = weak_timer()
        if portal:
            portal.close()
            portal.deleteLater()
        if timer:
            timer.stop()
            timer.deleteLater()

    try:
        img_meta = Images.Portal.S1.value if exit_flag else Images.Portal.S2.value
        image_size_r = img_meta.size_r
        cur_size_r = config.size_ratio * config.size_ratio_base / image_size_r  # 表示当前的 最终比列
        pixmap = QPixmap(img_meta.path)
        if not turn_right:
            pixmap = pixmap.transformed(QTransform().rotate(180))

        scaled_pixmap = pixmap.scaled(
            pixmap.size() * cur_size_r,
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation
        )
        scaled_anchor_pos = QPoint(round(img_meta.anchor.x() * cur_size_r), round(img_meta.anchor.y() * cur_size_r))
        pos = QPoint(target_anchor_pos.x() - scaled_anchor_pos.x(), target_anchor_pos.y() - scaled_anchor_pos.y())
        portal_widget.setPixmap(scaled_pixmap)
        portal_widget.move(pos)
        portal_widget.show()

        show_timer.timeout.connect(cleanup)
        show_timer.setSingleShot(True)  # 设置为单次触发
        show_timer.start(3000)  # 三秒后关闭并清理

    except Exception as e:
        print(f"Error in handle_portal: {e}")
        cleanup()
        raise
