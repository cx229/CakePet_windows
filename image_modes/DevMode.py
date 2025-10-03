import random

from PyQt5.QtWidgets import QWidget

from image_modes import ImagesMode
from resmeta import Images


class DevMode(ImagesMode):
    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.confs = {1: ImagesMode.ImageConf(Images.Dev.S1.value, 2, 1000),
                      2: ImagesMode.ImageConf(Images.Sit.CLAM2.value, 1, 1000),
                      }
        self.change_interval_min = self.change_interval_max = 100 * 1000
        self.next_mode_name='DevMode'
