
def adjust_offset_screen(self, offset: QPoint):
    if config.screen_connect_enabled:  # 循环屏幕
        new_offset = self.adjust_offset_screen_connect(offset, config.anchor_pos)  # 循环屏幕
    else:
        new_offset = self.adjust_offset_screen_unconnect(offset, config.anchor_pos)  # 普通移动，确保不会超出本屏幕

    return new_offset

def adjust_offset_screen_unconnect(self, offset: QPoint, cur_anchor_pos: QPoint):
    """调整偏移量，确保图片不会超出桌面范围"""
    new_offset = QPoint(offset)
    target_anchor_pos = cur_anchor_pos + new_offset
    left_screen = self.screen_monitor.get_left_screen()
    if target_anchor_pos.x() < left_screen.screen_rect.left():
        new_offset.setX(left_screen.screen_rect.left() - config.anchor_pos.x())

    right_screen = self.screen_monitor.get_right_screen()
    if target_anchor_pos.x() > right_screen.screen_rect.right():
        new_offset.setX(right_screen.screen_rect.right() - config.anchor_pos.x())
    return new_offset

def adjust_offset_screen_connect(self, offset: QPoint, cur_anchor_pos: QPoint):
    """调整偏移量，实现循环屏幕效果"""
    new_offset = QPoint(offset)
    target_anchor_pos = cur_anchor_pos + new_offset

    # 获取左右屏幕信息
    left_screen = self.screen_monitor.get_left_screen()
    right_screen = self.screen_monitor.get_right_screen()

    # 如果移出左边界，从右边界出现
    if target_anchor_pos.x() < left_screen.screen_rect.left():
        overflow = left_screen.screen_rect.left() - target_anchor_pos.x()
        new_x = right_screen.screen_rect.right() - overflow
        new_offset.setX(new_x - cur_anchor_pos.x())

    # 如果移出右边界，从左边界出现
    elif target_anchor_pos.x() > right_screen.screen_rect.right():
        overflow = target_anchor_pos.x() - right_screen.screen_rect.right()
        new_x = left_screen.screen_rect.left() + overflow
        new_offset.setX(new_x - cur_anchor_pos.x())

    return new_offset