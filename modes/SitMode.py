from typing import TYPE_CHECKING

from modes.Mode import Mode
from utils.img_uttil import load_img

if TYPE_CHECKING:
    from main import FollowAndDragWidget

class SitMode(Mode):
    NAME = "sit"
    def __init__(self, widget: 'FollowAndDragWidget'):
        super().__init__(widget, confs={
            1: {"img": load_img("img/image.png"), "next": 1, "duration": 0},
        })



