from dataclasses import dataclass
from PyQt5.QtCore import QRect, QObject, pyqtSignal, QPoint
from PyQt5.QtGui import QScreen
from PyQt5.QtWidgets import QApplication, QWidget

from utils.log_util import logger


@dataclass
class WorkAreaInfo:
    screen_rect: QRect  # 显示器物理区域（包含任务栏）
    work_rect: QRect  # 工作区域（扣除任务栏）


class ScreenMonitor(QObject):
    workarea_changed = pyqtSignal(list)  # 参数: [WorkAreaInfo]

    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self._parent_widget = parent_widget
        self._last_state = []
        self._setup_screen_monitor()
        self._check_workarea_changes()  # 初始化时获取一次状态

    def _setup_screen_monitor(self):
        """连接Qt屏幕变化信号"""
        app = QApplication.instance()

        # 监听现有屏幕的变化
        for screen in app.screens():
            screen.geometryChanged.connect(self._check_workarea_changes)
            screen.availableGeometryChanged.connect(self._check_workarea_changes)

        # 监听新增/移除屏幕（Qt 5.15+）
        if hasattr(app, 'screenAdded'):
            app.screenAdded.connect(self._on_screen_added)
        if hasattr(app, 'screenRemoved'):
            app.screenRemoved.connect(self._on_screen_removed)

    def _on_screen_added(self, screen: QScreen):
        """新增屏幕时连接信号"""
        screen.geometryChanged.connect(self._check_workarea_changes)
        screen.availableGeometryChanged.connect(self._check_workarea_changes)
        self._check_workarea_changes()

    def _on_screen_removed(self, screen: QScreen):
        """移除屏幕时触发检查"""
        self._check_workarea_changes()

    def _check_workarea_changes(self):
        """检查所有屏幕的工作区域是否变化"""
        new_state = []
        for screen in QApplication.screens():
            new_state.append(WorkAreaInfo(
                screen_rect=screen.geometry(),
                work_rect=screen.availableGeometry()
            ))

        if new_state != self._last_state:
            self._last_state = new_state
            logger.info(f"工作区域变化, 新状态: {new_state}")
            self.workarea_changed.emit(new_state)

    def get_left_screen(self) -> WorkAreaInfo:
        """获取最左侧的屏幕"""
        return min(self._last_state, key=lambda x: x.work_rect.left())

    def get_right_screen(self) -> WorkAreaInfo:
        """获取最右侧的屏幕"""
        return max(self._last_state, key=lambda x: x.work_rect.right())

    def get_screens(self) -> list[WorkAreaInfo]:
        """获取所有屏幕信息"""
        return self._last_state

    def get_combined_screen_geometry(self):
        """获取所有显示器的联合矩形区域"""
        combined = QRect()
        for screen in QApplication.screens():
            # 使用 united() 合并所有屏幕的几何区域
            combined = combined.united(screen.geometry())
        return combined


def get_cur_work_bottom(anchor_pos: QPoint, screen_monitor: ScreenMonitor) -> int:
    """
    获取当前工作区域的底部坐标
    1. 首先尝试根据锚点的x,y坐标找到完全包含它的屏幕
    2. 如果找不到，则仅根据x坐标判断所在屏幕
    """
    cur_anchor_pos = anchor_pos
    work_area_infos = screen_monitor.get_screens()

    # 精确匹配（x和y都匹配）
    for work_area_info in work_area_infos:
        if work_area_info.screen_rect.contains(cur_anchor_pos):
            return work_area_info.work_rect.bottom()

    # 仅根据x坐标匹配
    for work_area_info in work_area_infos:
        screen_rect = work_area_info.screen_rect
        if screen_rect.left() <= cur_anchor_pos.x() <= screen_rect.right():
            return work_area_info.work_rect.bottom()

    raise ValueError(f"未找到包含锚点 {cur_anchor_pos} 的工作区域")


# 使用示例
if __name__ == "__main__":
    class MyWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Qt显示器监听示例")
            self.resize(300, 200)

            # 初始化监听器
            self.screen_monitor = ScreenMonitor(parent_widget=self)
            self.screen_monitor.workarea_changed.connect(self.handle_display_change)

        def handle_display_change(self, screens):
            print("\n=== 显示器配置变化 ===")
            for i, screen in enumerate(screens):
                print(f"显示器 {i + 1}: 物理区域 {screen.screen_rect.getRect()}")
                print(f"显示器 {i + 1}: 工作区域 {screen.work_rect.getRect()}")
            print("===================\n")


    import sys

    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())
