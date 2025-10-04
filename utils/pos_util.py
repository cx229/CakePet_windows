from PyQt5.QtCore import QPoint


def point_to_tuple(pos: QPoint) -> tuple:
    return pos.x(), pos.y()
