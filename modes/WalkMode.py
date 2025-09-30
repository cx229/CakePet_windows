from typing import TYPE_CHECKING

from modes.Mode import Mode
from utils.img_uttil import load_img

if TYPE_CHECKING:
    from main import FollowAndDragWidget


class WalkMode(Mode):
    NAME = "walk"
    def __init__(self, widget: 'FollowAndDragWidget'):
        super().__init__(widget,confs = {
            1: {"img": load_img("img/image3-1.png"), "next": 2, "duration": 145},
            2: {"img": load_img("img/image3-2.png"), "next": 3, "duration": 180},
            3: {"img": load_img("img/image3-3.png"), "next": 4, "duration": 150},
            4: {"img": load_img("img/image3-2.png"), "next": 1, "duration": 140},
        })

