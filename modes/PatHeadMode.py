from typing import TYPE_CHECKING

from modes.Mode import Mode
from utils.img_uttil import load_img

if TYPE_CHECKING:
    from main import FollowAndDragWidget


class PatHeadMode(Mode):
    NAME = "pat_head"

    def __init__(self, widget: 'FollowAndDragWidget'):
        super().__init__(widget, confs={
            1: {"img": load_img("img/image4-1.png"), "next": 2, "duration": 145},
            2: {"img": load_img("img/image4-2.png"), "next": 3, "duration": 180},
            3: {"img": load_img("img/image4-3.png"), "next": 4, "duration": 150},
            4: {"img": load_img("img/image4-4.png"), "next": 5, "duration": 140},
            5: {"img": load_img("img/image4-5.png"), "next": 1, "duration": 159},
        })
