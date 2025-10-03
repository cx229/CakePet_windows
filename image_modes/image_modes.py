import random

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QPixmap, QTransform
from PyQt5.QtWidgets import QWidget

from configs import config
from image_modes.ImagesMode import ImagesMode, FollowTransImagesMode
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


class WalkMode(FollowTransImagesMode):
    def __init__(self, widget: QWidget):
        """走"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Walk.S1.value, 2, lambda: random.randint(140, 150)),
            2: ImagesMode.ImageConf(Images.Walk.S2.value, 3, lambda: random.randint(140, 150)),
            3: ImagesMode.ImageConf(Images.Walk.S3.value, 4, lambda: random.randint(140, 150)),
            4: ImagesMode.ImageConf(Images.Walk.S2.value, 1, lambda: random.randint(140, 150)),
        }


class LiftUpMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """提"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.LiftUp.S1.value, 2, lambda: random.randint(340, 370)),
            2: ImagesMode.ImageConf(Images.LiftUp.S2.value, 1, lambda: random.randint(340, 370)),
        }


class ThrowMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """投"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Throw.S1.value, 2, lambda: random.randint(140, 180)),
            2: ImagesMode.ImageConf(Images.Throw.S2.value, 3, lambda: random.randint(140, 180)),
            3: ImagesMode.ImageConf(Images.Throw.S3.value, 4, lambda: random.randint(140, 180)),
            4: ImagesMode.ImageConf(Images.Throw.S2.value, 1, lambda: random.randint(140, 180)),
        }

class FallStandMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """掉落"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.FallStand.S1.value, 2, lambda: random.randint(140, 180)),
            2: ImagesMode.ImageConf(Images.FallStand.S2.value, 3, lambda: random.randint(140, 180)),
            3: ImagesMode.ImageConf(Images.FallStand.S3.value, 4, lambda: random.randint(140, 180)),
            4: ImagesMode.ImageConf(Images.FallStand.S2.value, 1, lambda: random.randint(140, 180)),
        }

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


class DragMode(ImagesMode):
    def __init__(self, widget: QWidget):
        """提"""
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.LiftUp.S1.value, 2, lambda: random.randint(340, 370)),
            2: ImagesMode.ImageConf(Images.LiftUp.S2.value, 1, lambda: random.randint(340, 370)),
        }
