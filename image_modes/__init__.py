from typing import Optional

from PyQt5.QtCore import QTimer

from configs import config
from image_modes.ChangeNextMode import NextChangeMode
from image_modes.multi_image_modes import *
from utils.log_util import logger

modes_map = {str(m.name()): m for m in
             [SitClamMode,SitPuffedMode, WalkMode, LiftUpMode, PatHeadMode, ShakeHeadMode]
             }

modes_name_standby = [str(m.name()) for m in
                      [SitClamMode,SitPuffedMode, WalkMode, LiftUpMode, PatHeadMode]]

