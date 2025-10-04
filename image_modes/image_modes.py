import random

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QPixmap, QTransform
from PyQt5.QtWidgets import QWidget

from configs import config
from image_modes.ImagesMode import ImagesMode
from resmeta import Images


class SitClamMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """坐"""
        super().__init__(widget)
        self.confs = {1: ImagesMode.ImageConf(Images.Sit.CLAM1.value, 2, lambda: random.randint(120, 10 * 1000)),
                      2: ImagesMode.ImageConf(Images.Sit.CLAM2.value, 3, lambda: random.randint(120, 160)),
                      3: ImagesMode.ImageConf(Images.Sit.CLAM3.value, 4, lambda: random.randint(120, 160)),
                      4: ImagesMode.ImageConf(Images.Sit.CLAM2.value, 1, lambda: random.randint(120, 160)),
                      }
        self.change_interval_max = 25 * 1000


class SitPuffedMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """坐,炸毛"""
        super().__init__(widget)
        self.confs = {1: ImagesMode.ImageConf(Images.Sit.PUFFED1.value, 2, lambda: random.randint(120, 10 * 1000)),
                      2: ImagesMode.ImageConf(Images.Sit.PUFFED2.value, 3, lambda: random.randint(120, 160)),
                      3: ImagesMode.ImageConf(Images.Sit.PUFFED3.value, 4, lambda: random.randint(120, 160)),
                      4: ImagesMode.ImageConf(Images.Sit.PUFFED4.value, 5, lambda: random.randint(120, 160)),
                      5: ImagesMode.ImageConf(Images.Sit.PUFFED2.value, 1, lambda: random.randint(120, 160)),
                      }
        self.change_interval_max = 25 * 1000




class PatHeadMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """摸头"""
        super().__init__(widget)

        self.confs = {
            1: ImagesMode.ImageConf(Images.PatHead.S1.value, 2, lambda: random.randint(105, 110)),
            2: ImagesMode.ImageConf(Images.PatHead.S2.value, 3, lambda: random.randint(100, 110)),
            3: ImagesMode.ImageConf(Images.PatHead.S3.value, 4, lambda: random.randint(100, 110)),
            4: ImagesMode.ImageConf(Images.PatHead.S4.value, 5, lambda: random.randint(105, 110)),
            5: ImagesMode.ImageConf(Images.PatHead.S5.value, 1, lambda: random.randint(105, 110)),
        }
        self.change_interval_min = 3000
        self.change_interval_max = 4000
        self.change_prob = 0.9
        self.next_mode_name = ShakeHeadMode.name()  # 指定下一个模式为摇头


class ShakeHeadMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """摇头"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.ShakeHead.S1.value, 2, lambda: random.randint(140, 180)),
            2: ImagesMode.ImageConf(Images.ShakeHead.S2.value, 1, lambda: random.randint(140, 180)),
        }
        self.change_interval_min = 1000
        self.change_interval_max = 2000
        self.change_prob = 1


class WalkMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """走"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Walk.S1.value, 2, 100, QPoint(-5, 0)),
            2: ImagesMode.ImageConf(Images.Walk.S2.value, 3, 100, QPoint(-5, 0)),
            3: ImagesMode.ImageConf(Images.Walk.S3.value, 4, 100, QPoint(-5, 0)),
            4: ImagesMode.ImageConf(Images.Walk.S2.value, 1, 100, QPoint(-5, 0)),
        }
        self.transform_flag = random.choice([True, False])  # 是否需要镜像变换
        self.change_interval_max = 10 * 1000


# ===================================== FollowMode 跟随模式 =====================================
class DragFollowMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """提"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.LiftUp.S1.value, 2, lambda: random.randint(340, 370)),
            2: ImagesMode.ImageConf(Images.LiftUp.S2.value, 1, lambda: random.randint(340, 370)),
        }
        self.time_next_enabled = False  # 关闭定时切换


class ThrowFollowMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """投"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Throw.S1.value, 2, lambda: random.randint(140, 180)),
            2: ImagesMode.ImageConf(Images.Throw.S2.value, 3, lambda: random.randint(140, 180)),
            3: ImagesMode.ImageConf(Images.Throw.S3.value, 1, lambda: random.randint(140, 180)),
        }
        self.time_next_enabled = False  # 关闭定时切换
        self.next_mode_name = ThrowFallStandFollowMode.name()  # 指定下一个模式为摇头


class ThrowFallStandFollowMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """掉落"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.FallStand.S1.value, 2, lambda: random.randint(140, 180)),
            2: ImagesMode.ImageConf(Images.FallStand.S2.value, 3, lambda: random.randint(140, 180)),
            3: ImagesMode.ImageConf(Images.FallStand.S3.value, 4, lambda: random.randint(140, 180)),
            4: ImagesMode.ImageConf(Images.FallStand.S2.value, None, lambda: random.randint(140, 180)),
        }
        self.time_next_enabled = False  # 关闭定时切换


class MouseFollowMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """跟随"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Walk.S1.value, 2, 100, QPoint(0, 0)),
            2: ImagesMode.ImageConf(Images.Walk.S2.value, 3, 100, QPoint(0, 0)),
            3: ImagesMode.ImageConf(Images.Walk.S3.value, 4, 100, QPoint(0, 0)),
            4: ImagesMode.ImageConf(Images.Walk.S2.value, 1, 100, QPoint(0, 0)),
        }
        self.time_next_enabled = False  # 关闭定时切换

    def update_widget_image(self, next_conf):
        """运动的情况，根据鼠标位置判断是否需要镜像"""
        img = next_conf.img
        mouse_img_pos = self.widget.image_label.mapFromGlobal(QCursor.pos())
        if mouse_img_pos.x() > self.widget.image_label.width() // 2:
            self.transform_flag = True
        else:
            self.transform_flag = False
        self.widget.set_image(img, next_conf.img_meta, self.transform_flag, next_conf.offset)
