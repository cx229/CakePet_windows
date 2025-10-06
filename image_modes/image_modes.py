import random
from dataclasses import replace

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QPixmap, QTransform
from PyQt5.QtWidgets import QWidget

from configs import config
from image_modes.ImagesMode import ImagesMode
from resmeta import Images


class SitClamMode(ImagesMode):
    title = "坐-安静"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {1: ImagesMode.ImageConf(Images.Sit.CLAM1.value, 2, lambda: random.randint(120, 10 * 1000)),
                      2: ImagesMode.ImageConf(Images.Sit.CLAM2.value, 3, lambda: random.randint(120, 160)),
                      3: ImagesMode.ImageConf(Images.Sit.CLAM3.value, 4, lambda: random.randint(120, 160)),
                      4: ImagesMode.ImageConf(Images.Sit.CLAM2.value, 1, lambda: random.randint(120, 160)),
                      }
        self.change_interval_max = 25 * 1000


class SitPuffedMode(ImagesMode):
    title = "坐-炸毛"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {1: ImagesMode.ImageConf(Images.Sit.PUFFED1.value, 2, lambda: random.randint(120, 10 * 1000)),
                      2: ImagesMode.ImageConf(Images.Sit.PUFFED2.value, 3, lambda: random.randint(120, 160)),
                      3: ImagesMode.ImageConf(Images.Sit.PUFFED3.value, 4, lambda: random.randint(120, 160)),
                      4: ImagesMode.ImageConf(Images.Sit.PUFFED4.value, 5, lambda: random.randint(120, 160)),
                      5: ImagesMode.ImageConf(Images.Sit.PUFFED2.value, 1, lambda: random.randint(120, 160)),
                      }
        self.change_interval_max = 25 * 1000


class PatHeadMode(ImagesMode):
    title = "坐-摸头"

    def __init__(self, widget: QWidget):
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
        self.change_prob = 0.95
        self.next_mode_name = ShakeHeadMode.get_name()  # 指定下一个模式为摇头


class ShakeHeadMode(ImagesMode):
    title = "坐-摇头"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.ShakeHead.S1.value, 2, lambda: random.randint(140, 180)),
            2: ImagesMode.ImageConf(Images.ShakeHead.S2.value, 1, lambda: random.randint(140, 180)),
        }
        self.change_interval_min = 1000
        self.change_interval_max = 2000
        self.change_prob = 1
        self.next_mode_name = SitPuffedMode.get_name()  # 指定下一个模式为 坐,炸毛


class WhiteMode(ImagesMode):
    title = "美白体验"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Walk.WHITE1.value, 2, lambda: random.randint(200, 300)),
            2: ImagesMode.ImageConf(Images.Walk.WHITE2.value, 3, lambda: random.randint(200, 300)),
            3: ImagesMode.ImageConf(Images.Walk.WHITE3.value, 4, lambda: random.randint(200, 300)),
            4: ImagesMode.ImageConf(Images.Walk.WHITE4.value, 5, lambda: random.randint(200, 300)),
            5: ImagesMode.ImageConf(Images.Walk.WHITE5.value, None, lambda: random.randint(5000, 10000)),
        }

        self.time_next_enabled = False


class ProbeHeadMode(ImagesMode):
    title = "猫猫探头"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.ProbeHead.S1.value, 2, lambda: random.randint(1000, 5000)),
            2: ImagesMode.ImageConf(Images.ProbeHead.S2.value, 1, lambda: random.randint(150, 300)),
        }
        self.change_interval_min = 5000
        self.change_interval_max = 10000
        self.change_prob = 0.5
        self.transform_flag = random.choice([True, False])  # 是否需要镜像变换
        self.next_mode_name = SitClamMode.get_name()  # 指定下一个模式为 坐


class LieMode(ImagesMode):
    title = "趴着"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Wriggle.S1.value, None, lambda: random.randint(3000, 7000)),
        }
        self.time_next_enabled = False  # 关闭定时切换,靠单个图片的next
        self.change_prob = 0.5


class WalkMode(ImagesMode):
    title = "走"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Walk.S1.value, 2, 100, QPoint(-5, 0)),
            2: ImagesMode.ImageConf(Images.Walk.S2.value, 3, 100, QPoint(-5, 0)),
            3: ImagesMode.ImageConf(Images.Walk.S3.value, 4, 100, QPoint(-5, 0)),
            4: ImagesMode.ImageConf(Images.Walk.S2.value, 1, 100, QPoint(-5, 0)),
        }
        self.transform_flag = random.choice([True, False])  # 是否需要镜像变换
        self.change_interval_max = 10 * 1000


class WriggleMode(ImagesMode):
    title = "蠕动"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Wriggle.S1.value, 2, lambda: random.randint(250, 300), QPoint(-3, 0)),
            2: ImagesMode.ImageConf(Images.Wriggle.S2.value, 1, lambda: random.randint(250, 300), QPoint(-3, 0)),
        }
        self.change_interval_min = 3000
        self.change_interval_max = 4000
        self.change_prob = 0.5
        self.transform_flag = random.choice([True, False])  # 是否需要镜像变换


class RollMode(ImagesMode):
    title = "翻滚"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Roll.S1.value, 2, 50, QPoint(-50, 0)),
            2: ImagesMode.ImageConf(Images.Roll.S2.value, 3, 50, QPoint(-50, 0)),
            3: ImagesMode.ImageConf(Images.Roll.S3.value, 4, 50, QPoint(-50, 0)),
            4: ImagesMode.ImageConf(Images.Roll.S4.value, 5, 50, QPoint(-50, 0)),
            5: ImagesMode.ImageConf(Images.Roll.S5.value, 6, 50, QPoint(-50, 0)),
            6: ImagesMode.ImageConf(Images.Roll.S6.value, 1, 50, QPoint(-50, 0)),
        }

        self.transform_flag = random.choice([True, False])  # 是否需要镜像变换


class PullFishMode(ImagesMode):
    title = "拔鱼"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        ratio = random.random() * 0.8 + 0.7  # 0.7-1.5 的随机数
        self.confs = {
            1: ImagesMode.ImageConf(Images.PullFish.S1.value, 2, lambda: random.randint(300, 500)),
            2: ImagesMode.ImageConf(Images.PullFish.S2.value, 3, lambda: random.randint(130, 160)),
            3: ImagesMode.ImageConf(Images.PullFish.S3.value, 4, lambda: random.randint(160, 200)),
            4: ImagesMode.ImageConf(Images.PullFish.S4.value, 5, lambda: random.randint(130, 160)),
            5: ImagesMode.ImageConf(Images.PullFish.S5.value, 6, 70),
            6: ImagesMode.ImageConf(replace(Images.PullFish.S6.value, anchor_dy=int(70 * ratio)), 7, 70, QPoint(130, 0) * ratio),
            7: ImagesMode.ImageConf(replace(Images.PullFish.S6.value, anchor_dy=int(110 * ratio)), 8, 70, QPoint(125, 0) * ratio),
            8: ImagesMode.ImageConf(replace(Images.PullFish.S6.value, anchor_dy=int(70 * ratio)), 9, 70, QPoint(120, 0) * ratio),
            9: ImagesMode.ImageConf(replace(Images.Wriggle.S1.value, anchor_dy=0), None, 500, QPoint(120, 0) * ratio),
        }
        self.time_next_enabled = False  # 关闭定时切换
        self.change_prob = 1
        self.next_mode_name = LieMode.get_name()  # 指定下一个模式为趴着


# ===================================== FollowMode 跟随模式 =====================================
class DragFollowMode(ImagesMode):
    title = "提-跟随"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.LiftUp.S1.value, 2, lambda: random.randint(340, 370)),
            2: ImagesMode.ImageConf(Images.LiftUp.S2.value, 1, lambda: random.randint(340, 370)),
            3: ImagesMode.ImageConf(Images.LiftUp.S3.value, 1, 100),
            4: ImagesMode.ImageConf(Images.LiftUp.S4.value, 2, 100),
            5: ImagesMode.ImageConf(Images.LiftUp.S5.value, 3, 100),
            6: ImagesMode.ImageConf(Images.LiftUp.S6.value, 4, 100)
        }

        self.time_next_enabled = False  # 关闭定时切换


class ThrowFollowMode(ImagesMode):
    title = "抛掷-跟随"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.Roll.S1.value, 2, lambda: random.randint(140, 180)),
            2: ImagesMode.ImageConf(Images.Roll.S2.value, 3, lambda: random.randint(140, 180)),
            3: ImagesMode.ImageConf(Images.Roll.S3.value, 4, lambda: random.randint(140, 180)),
            4: ImagesMode.ImageConf(Images.Roll.S4.value, 5, lambda: random.randint(140, 180)),
            5: ImagesMode.ImageConf(Images.Roll.S5.value, 6, lambda: random.randint(140, 180)),
            6: ImagesMode.ImageConf(Images.Roll.S6.value, 1, lambda: random.randint(140, 180)),
        }
        self.time_next_enabled = False  # 关闭定时切换
        self.next_mode_name = ThrowFallStandFollowMode.get_name()  # 指定下一个模式为 掉落-跟随
        # self.next_mode_name = RollMode.name  # 指定下一个模式为 掉落-跟随


class ThrowFallStandFollowMode(ImagesMode):
    title = "掉落-跟随"

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {
            1: ImagesMode.ImageConf(Images.JumpDown.S1.value, 2, lambda: random.randint(50, 70)),
            2: ImagesMode.ImageConf(Images.JumpDown.S2.value, 3, lambda: random.randint(80, 90)),
            3: ImagesMode.ImageConf(Images.JumpDown.S3.value, None, lambda: random.randint(200, 250)),
        }
        self.time_next_enabled = False  # 关闭定时切换
        self.next_mode_name = WalkMode.get_name()
        # self.next_mode_name = LieMode.name # DEV


class MouseFollowMode(ImagesMode):
    title = "跟随"

    def __init__(self, widget: QWidget):
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
