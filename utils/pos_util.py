from PyQt5.QtCore import QPoint, QRect, QPointF


def point_to_tuple(pos: QPoint) -> tuple:
    return pos.x(), pos.y()
def pointf_to_tuple(pos_f: QPointF) -> tuple:
    return round(pos_f.x(), 3), round(pos_f.y(), 3)


def adjust_pos_to_work_f(pos_f: QPointF, rect: QRect) -> QPointF:
    """
    如果位置超出了矩形区域，调整到矩形区域内
    :param pos_f: 位置
    :param rect: 矩形区域
    :return: 调整后的位置
    """
    res_pos_f = QPointF(pos_f)
    if pos_f.x() < rect.left():
        res_pos_f.setX(rect.left())
    elif pos_f.x() > rect.right():
        res_pos_f.setX(rect.right())
    if res_pos_f.y() < rect.top():
        res_pos_f.setY(rect.top())
    elif res_pos_f.y() > rect.bottom():
        res_pos_f.setY(rect.bottom())
    return res_pos_f
