from dataclasses import dataclass, field, replace
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
    anchor_dx: Optional[int] = field(default=0, repr=False)  # 自定义水平偏移
    anchor_dy: Optional[int] = field(default=0, repr=False)  # 自定义垂直偏移
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
        return QPoint(*self._calculate_anchor()) + QPoint(self.anchor_dx, self.anchor_dy)

    @property
    def size(self) -> QSize:
        """实时获取图片尺寸"""
        return QSize(*self._calculate_size())


class Images:
    class Dev(Enum):  # 开发用
        S1 = ImageMeta("dev1", "img/dev1.png", size_r=10)



s1 = Images.Dev.S1.value
s2 = replace(Images.Dev.S1.value, anchor_dy=-15)
s3 = Images.Dev.S1.value

print(s1.anchor)
print(s2.anchor)
print(s3.anchor)

