from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Dict, Optional
import PIL.Image
from pathlib import Path

from PyQt5.QtCore import QPoint, QSize

# 锚点缓存结构：{name: (anchor_x, anchor_y)}
_ANCHOR_CACHE: Dict[str, Tuple[int, int]] = {}
_SIZE_CACHE: Dict[str, Tuple[int, int]] = {}

@dataclass(frozen=True)
class ImageMeta:
    key: str
    path: str
    anchor_x: Optional[int] = field(default=None, repr=False)  # 自定义水平锚点
    anchor_y: Optional[int] = field(default=None, repr=False)  # 自定义垂直锚点
    size_r: float = field(default=1.0)  # 缩放比例

    def __post_init__(self):
        """初始化验证"""
        if not Path(self.path).exists():
            raise FileNotFoundError(f"图片文件不存在: {self.path}")

    def _calculate(self) -> None:
        """计算图片首次访问时调用）"""
        with PIL.Image.open(self.path) as img:
            width, height = img.size
        # 优先使用自定义值，否则计算默认值（水平居中，底部对齐）
        x = self.anchor_x if self.anchor_x is not None else width // 2
        y = self.anchor_y if self.anchor_y is not None else height
        _ANCHOR_CACHE[self.key] = (x, y)
        _SIZE_CACHE[self.key] = (width, height)

    def _calculate_anchor(self) -> Tuple[int, int]:
        """计算锚点坐标（首次访问时调用）"""
        if self.key not in _ANCHOR_CACHE:
            self._calculate()
        return _ANCHOR_CACHE[self.key]

    def _calculate_size(self) -> Tuple[int, int]:
        """计算图片尺寸（首次访问时调用）"""
        if self.key not in _SIZE_CACHE:
            self._calculate()
        return _SIZE_CACHE[self.key]

    @property
    def anchor(self) -> QPoint:
        """获取锚点坐标（自动处理首次计算）"""
        return QPoint(*self._calculate_anchor())

    @property
    def size(self) -> QSize:
        """实时获取图片尺寸"""
        return QSize(*self._calculate_size())


# 预设图片集合
class Images:
    class Dev(Enum):  # 开发用
        S1 = ImageMeta("dev1", "img/dev1.png", size_r=10)

    class Sit(Enum):  # 坐
        CLAM1 = ImageMeta("sit_clam1", "img/sit_clam-1.png")
        CLAM2 = ImageMeta("sit_clam2", "img/sit_clam-2.png")
        CLAM3 = ImageMeta("sit_clam3", "img/sit_clam-3.png")
        PUFFED1 = ImageMeta("sit_puffed1", "img/sit_puffed-1.png")
        PUFFED2 = ImageMeta("sit_puffed2", "img/sit_puffed-2.png")
        PUFFED3 = ImageMeta("sit_puffed3", "img/sit_puffed-3.png")
        PUFFED4 = ImageMeta("sit_puffed4", "img/sit_puffed-4.png")

    class Walk(Enum):  # 走
        S1 = ImageMeta("walk1", "img/walk-1.png", anchor_x=47)
        S2 = ImageMeta("walk2", "img/walk-2.png", anchor_x=47)
        S3 = ImageMeta("walk3", "img/walk-3.png", anchor_x=47)
        WHITE1 = ImageMeta("walk_white1", "img/walk_white-1.png", anchor_x=47)
        WHITE2 = ImageMeta("walk_white2", "img/walk_white-2.png", anchor_x=47)
        WHITE3 = ImageMeta("walk_white3", "img/walk_white-3.png", anchor_x=47)
        WHITE4 = ImageMeta("walk_white4", "img/walk_white-4.png", anchor_x=47)
        WHITE5 = ImageMeta("walk_white5", "img/walk_white-5.png", anchor_x=47)

    class PatHead(Enum):
        S1 = ImageMeta("pat_head1", "img/pat_head-1.png")
        S2 = ImageMeta("pat_head2", "img/pat_head-2.png")
        S3 = ImageMeta("pat_head3", "img/pat_head-3.png")
        S4 = ImageMeta("pat_head4", "img/pat_head-4.png")
        S5 = ImageMeta("pat_head5", "img/pat_head-5.png")

    class ShakeHead(Enum):  # 摇头头
        S1 = ImageMeta("shake_head1", "img/shake_head-1.png")
        S2 = ImageMeta("shake_head2", "img/shake_head-2.png")

    class LiftUp(Enum):  # 提起
        S1 = ImageMeta("lift_up1", "img/lift_up-1.png", anchor_y=71)
        S2 = ImageMeta("lift_up2", "img/lift_up-2.png", anchor_y=71)
        S3 = ImageMeta("lift_up3", "img/lift_up-3.png", anchor_y=71)
        S4 = ImageMeta("lift_up4", "img/lift_up-4.png", anchor_y=71)
        S5 = ImageMeta("lift_up5", "img/lift_up-5.png", anchor_y=71)
        S6 = ImageMeta("lift_up6", "img/lift_up-6.png", anchor_y=71)

    class Throw(Enum):  # 抛掷
        S1 = ImageMeta("throw1", "img/sit_clam-1.png")
        S2 = ImageMeta("throw2", "img/sit_clam-1.png")
        S3 = ImageMeta("throw3", "img/sit_clam-1.png")

    class FallStand(Enum):  # 掉落地面
        S1 = ImageMeta("fall_stand1", "img/sit_clam-1.png")
        S2 = ImageMeta("fall_stand2", "img/sit_clam-2.png")
        S3 = ImageMeta("fall_stand3", "img/sit_clam-3.png")


#
# 使用示例
if __name__ == "__main__":
    print("=== 锚点演示 ===")

    # 默认锚点
    print("\n--- 默认锚点 ---")
    sit1 = Images.Sit.CLAM1.value
    print(f"\nSIT1 (默认锚点): {sit1.anchor.x()}, 尺寸: {sit1.size}")
    print(f"\nSIT1 (默认锚点): {sit1.anchor}, 尺寸: {sit1.size}")

    # 部分自定义
    print("\n--- 部分自定义 ---")
    sit2 = Images.Sit.PUFFED1.value
    print(f"\nSIT2 (自定义X): {sit2.anchor}, 尺寸: {sit2.size}")

    print(f"\nSIT2 (自定义Y): {type(Images.Sit.CLAM1.value)}")
