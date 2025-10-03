from typing import Optional

from PyQt5.QtCore import QTimer

from configs import config
from image_modes.ChangeNextMode import NextChangeMode
from image_modes.image_modes import *
from utils.log_util import logger

modes_standby = [SitClamMode, SitPuffedMode, WalkMode, PatHeadMode]
modes_name_standby = [str(m.name()) for m in modes_standby]

# 模式映射,是所有模式的映射
modes = [SitClamMode, SitPuffedMode, PatHeadMode, ShakeHeadMode,  # 坐（摸头->摇头）
         WalkMode,
         LiftUpMode, ThrowMode, FallStandMode,  # 鼠标事件：提，(抛掷->落地）
         ]
modes_map = {str(m.name()): m for m in modes}

init_mode_name = SitClamMode.name()  # 初始模式

#
# if True:
#     from image_modes.DevMode import DevMode
#     init_mode_name = 'DevMode'
#     modes_map.update({str(m.name()): m for m in
#              [DevMode]
#              })
#     modes_name_standby = [str(m.name()) for m in
#                       [DevMode]]
