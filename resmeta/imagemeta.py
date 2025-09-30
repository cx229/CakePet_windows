from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Dict, Optional
import PIL.Image
from pathlib import Path

# 锚点缓存结构：{name: (anchor_x, anchor_y)}
_ANCHOR_CACHE: Dict[str, Tuple[int, int]] = {}


@dataclass(frozen=True)
class ImageMeta:
    key: str
    path: str
    anchor_x: Optional[int] = field(default=None, repr=False)  # 自定义水平锚点
    anchor_y: Optional[int] = field(default=None, repr=False)  # 自定义垂直锚点

    def __post_init__(self):
        """初始化验证"""
        if not Path(self.path).exists():
            raise FileNotFoundError(f"图片文件不存在: {self.path}")

    def _calculate_anchor(self) -> Tuple[int, int]:
        """计算锚点坐标（首次访问时调用）"""
        if self.key not in _ANCHOR_CACHE:
            print(f"计算锚点: {self.key}")
            width, height = self.size
            # 优先使用自定义值，否则计算默认值（水平居中，底部对齐）
            x = self.anchor_x if self.anchor_x is not None else width // 2
            y = self.anchor_y if self.anchor_y is not None else height
            _ANCHOR_CACHE[self.key] = (x, y)
        return _ANCHOR_CACHE[self.key]

    @property
    def anchor_pixel(self) -> Tuple[int, int]:
        """获取锚点坐标（自动处理首次计算）"""
        return self._calculate_anchor()

    @property
    def size(self) -> Tuple[int, int]:
        """实时获取图片尺寸"""
        with PIL.Image.open(self.path) as img:
            return img.size


# 预设图片集合
class Images:
    class Sit(Enum): # 坐
        CLAM1 = ImageMeta("sit_clam1", "img/sit_clam-1.png")
        CLAM2 = ImageMeta("sit_clam2", "img/sit_clam-2.png")
        CLAM3 = ImageMeta("sit_clam3", "img/sit_clam-3.png")
        PUFFED1 = ImageMeta("sit_puffed1", "img/sit_puffed-1.png")
        PUFFED2 = ImageMeta("sit_puffed2", "img/sit_puffed-2.png")
        PUFFED3 = ImageMeta("sit_puffed3", "img/sit_puffed-3.png")
        PUFFED4 = ImageMeta("sit_puffed4", "img/sit_puffed-4.png")

    class Walk(Enum): # 走
        S1 = ImageMeta("walk1", "img/walk-1.png")
        S2 = ImageMeta("walk2", "img/walk-2.png")
        S3 = ImageMeta("walk3", "img/walk-3.png")
        WHITE1 = ImageMeta("walk_white1", "img/walk_white-1.png")
        WHITE2 = ImageMeta("walk_white2", "img/walk_white-2.png")
        WHITE3 = ImageMeta("walk_white3", "img/walk_white-3.png")
        WHITE4 = ImageMeta("walk_white4", "img/walk_white-4.png")
        WHITE5 = ImageMeta("walk_white5", "img/walk_white-5.png")


    class PatHead(Enum):
        S1 = ImageMeta("pat_head1", "img/pat_head-1.png")
        S2 = ImageMeta("pat_head2", "img/pat_head-2.png")
        S3 = ImageMeta("pat_head3", "img/pat_head-3.png")
        S4 = ImageMeta("pat_head4", "img/pat_head-4.png")
        S5 = ImageMeta("pat_head5", "img/pat_head-5.png")

    class ShakeHead(Enum): # 摇头头
        S1 = ImageMeta("shake_head1", "img/shake_head-1.png")
        S2 = ImageMeta("shake_head2", "img/shake_head-2.png")

    class LiftUp(Enum): # 提起
        S1 = ImageMeta("lift_up1", "img/lift_up-1.png")
        S2 = ImageMeta("lift_up2", "img/lift_up-2.png")
        S3 = ImageMeta("lift_up3", "img/lift_up-3.png")
        S4 = ImageMeta("lift_up4", "img/lift_up-4.png")
        S5 = ImageMeta("lift_up5", "img/lift_up-5.png")
        S6 = ImageMeta("lift_up6", "img/lift_up-6.png")

#
# 使用示例
if __name__ == "__main__":
    print("=== 锚点演示 ===")

    # 默认锚点
    print("\n--- 默认锚点 ---")
    sit1 = Images.Sit.CLAM1.value
    print(f"\nSIT1 (默认锚点): {sit1.anchor_pixel}, 尺寸: {sit1.size}")
    print(f"\nSIT1 (默认锚点): {sit1.anchor_pixel}, 尺寸: {sit1.size}")

    # 部分自定义
    print("\n--- 部分自定义 ---")
    sit2 = Images.Sit.PUFFED1.value
    print(f"\nSIT2 (自定义X): {sit2.anchor_pixel}, 尺寸: {sit2.size}")

    print(f"\nSIT2 (自定义Y): {type(Images.Sit.CLAM1.value)}")
