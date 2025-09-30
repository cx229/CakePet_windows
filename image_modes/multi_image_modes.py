from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QPixmap, QTransform
from PyQt5.QtWidgets import QWidget

from configs import config
from image_modes.MultiImageMode import MultiImageMode
from resmeta import Images


class SitClamMode(MultiImageMode):
    def __init__(self, widget: QWidget):
        """坐"""
        super().__init__(widget)
        self.confs = {1: MultiImageMode.ImageConf(Images.Sit.CLAM1.value, 2, 1500),
                      2: MultiImageMode.ImageConf(Images.Sit.CLAM2.value, 3, 150),
                      3: MultiImageMode.ImageConf(Images.Sit.CLAM3.value, 4, 140),
                      4: MultiImageMode.ImageConf(Images.Sit.CLAM2.value, 1, 140),
                      }

class SitPuffedMode(MultiImageMode):
    def __init__(self, widget: QWidget):
        """坐"""
        super().__init__(widget)
        self.confs = {1: MultiImageMode.ImageConf(Images.Sit.PUFFED1.value, 2, 2500),
                      2: MultiImageMode.ImageConf(Images.Sit.PUFFED2.value, 3, 150),
                      3: MultiImageMode.ImageConf(Images.Sit.PUFFED3.value, 4, 140),
                      4: MultiImageMode.ImageConf(Images.Sit.PUFFED4.value, 5, 140),
                      5: MultiImageMode.ImageConf(Images.Sit.PUFFED2.value, 1, 140),
                      }



class WalkMode(MultiImageMode):
    def __init__(self, widget: QWidget):
        """走"""
        super().__init__(widget)
        self.confs = {
            1: MultiImageMode.ImageConf(Images.Walk.S1.value, 2, 145),
            2: MultiImageMode.ImageConf(Images.Walk.S2.value, 3, 180),
            3: MultiImageMode.ImageConf(Images.Walk.S3.value, 4, 150),
            4: MultiImageMode.ImageConf(Images.Walk.S2.value, 1, 140),
        }

    def update_widget_image(self, next_conf):

        img= next_conf.img
        anchor=next_conf.anchor
        if config.is_following:
            mouse_img_pos = self.widget.image_label.mapFromGlobal(QCursor.pos())
            if mouse_img_pos.x() > self.widget.image_label.width() // 2:
                transform = QTransform().scale(-1, 1)  # 水平翻转
                img = img.transformed(transform)
                # anchor = (img.width() - anchor[0], anchor[1])
        self.widget.set_image(img,anchor)


class LiftUpMode(MultiImageMode):
    def __init__(self, widget: QWidget):
        """提"""
        super().__init__(widget)
        self.confs = {
            1: MultiImageMode.ImageConf(Images.LiftUp.S1.value, 2, 350),
            2: MultiImageMode.ImageConf(Images.LiftUp.S2.value, 1, 360),
        }


class PatHeadMode(MultiImageMode):
    def __init__(self, widget: QWidget):
        """摸头"""
        super().__init__(widget)

        self.confs = {
            1: MultiImageMode.ImageConf(Images.PatHead.S1.value, 2, 105),
            2: MultiImageMode.ImageConf(Images.PatHead.S2.value, 3, 100),
            3: MultiImageMode.ImageConf(Images.PatHead.S3.value, 4, 100),
            4: MultiImageMode.ImageConf(Images.PatHead.S4.value, 5, 105),
            5: MultiImageMode.ImageConf(Images.PatHead.S5.value, 1, 109),
        }
        self.change_interval_min = 3000
        self.change_interval_max = 4000
        self.change_prob=0.9
        self.next_mode_name = ShakeHeadMode.name() # 指定下一个模式为摇头


class ShakeHeadMode(MultiImageMode):
    def __init__(self, widget: QWidget):
        """摇头"""
        super().__init__(widget)
        self.confs = {
            1: MultiImageMode.ImageConf(Images.ShakeHead.S1.value, 2, 145),
            2: MultiImageMode.ImageConf(Images.ShakeHead.S2.value, 1, 160),
        }
        self.change_interval_min = 1000
        self.change_interval_max = 2000
        self.change_prob=1
