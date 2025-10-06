from image_modes.ChangeNextMode import NextChangeMode
from image_modes.image_modes import *

# 固定待机模式
modes_standby_fix = [SitClamMode, PatHeadMode, ShakeHeadMode,
                     ProbeHeadMode, LieMode, WhiteMode]
# 移动待机模式
modes_standby_move = [WriggleMode, WalkMode, RollMode, PullFishMode]

modes_standby = modes_standby_fix + modes_standby_move
# 模式映射,是所有模式的映射
modes = [SitClamMode, PatHeadMode, ShakeHeadMode, SitPuffedMode,  # 坐: 静坐，摸头->摇头->炸毛
         ProbeHeadMode, LieMode, WhiteMode,  # 探头，躺，美白
         WriggleMode, WalkMode, RollMode, PullFishMode,  # 蠕动，走，翻滚，拉鱼
         DragFollowMode, ThrowFollowMode, ThrowFallStandFollowMode, MouseFollowMode  # 鼠标事件：拖拽，抛掷->落地，鼠标跟随
         ]
modes_map = {str(m.get_name()): m for m in modes}

init_mode_name = SitClamMode.get_name()  # 初始模式

# modes_standby_fix = [ ProbeHeadMode,LieMode]  # 固定待机模式
# modes_standby_move = [ WriggleMode, PullFishMode]  # 移动待机模式


#
# if True:
#     from image_modes.DevMode import DevMode
#     init_mode_name = 'DevMode'
#     modes_map.update({str(m.name()): m for m in
#              [DevMode]
#              })
#     modes_name_standby = [str(m.name()) for m in
#                       [DevMode]]
