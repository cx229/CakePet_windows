
from image_modes.ChangeNextMode import NextChangeMode
from image_modes.image_modes import *

modes_standby_fix = [SitClamMode, SitPuffedMode, PatHeadMode] # 固定待机模式
modes_standby_move = [WalkMode] # 移动待机模式

# 模式映射,是所有模式的映射
modes = [SitClamMode, SitPuffedMode, PatHeadMode, ShakeHeadMode,  # 坐（摸头->摇头）
         WalkMode,
         DragFollowMode, ThrowFollowMode, ThrowFallStandFollowMode, MouseFollowMode  # 鼠标事件：拖拽，(抛掷->落地），鼠标跟随
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
