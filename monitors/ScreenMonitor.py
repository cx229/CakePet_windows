import ctypes
from dataclasses import dataclass
from typing import Optional

from PyQt5.QtCore import QRect, QObject, pyqtSignal, QAbstractNativeEventFilter, QPoint, QPointF
from PyQt5.QtWidgets import QApplication, QWidget
import win32api
import win32con
import win32gui
from ctypes import wintypes

from configs import config
from module_controllers.portal_label import handle_portal
from utils.log_util import logger


@dataclass
class WorkAreaInfo:
    screen_rect: QRect  # 显示器物理区域, 包含任务栏.(x,y,width,height)
    work_rect: QRect  # 工作区域（扣除任务栏）, (x,y,width,height)


class ScreenMonitor(QObject, QAbstractNativeEventFilter):
    workarea_changed = pyqtSignal(list)  # 参数: [WorkAreaInfo]

    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self._parent_widget = parent_widget
        self._setup_dpi_awareness()
        self._setup_event_filter()

        self._last_state = []  # 表示最新的工作区域信息
        self.workarea_infos: list[WorkAreaInfo] = []  # 表示所有工作区域信息,基于联合矩阵
        self.combined_rect = QRect()  # 表示所有工作区域的联合矩形区域

        self._check_workarea_changes()  # 初始化时获取一次状态

    def get_left_screen(self) -> WorkAreaInfo:
        return min(self.workarea_infos, key=lambda x: x.work_rect.left())

    def get_right_screen(self) -> WorkAreaInfo:
        return max(self.workarea_infos, key=lambda x: x.work_rect.right())

    def get_screens(self) -> list[WorkAreaInfo]:
        return self.workarea_infos

    def get_screens_workarea_tuple_list(self) -> list[str]:
        return [f"屏幕工作区域 {i}: {screen.work_rect.getRect()}" for i, screen in enumerate(self.workarea_infos)]

    def get_screens_tuple_list(self):
        return [f"屏幕 {i}: {(screen.screen_rect.getRect(), screen.work_rect.getRect())}" for i, screen in enumerate(self.workarea_infos)]

    def _setup_dpi_awareness(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            ctypes.windll.user32.SetProcessDPIAware()

    def _setup_event_filter(self):
        QApplication.instance().installNativeEventFilter(self)

        # 复用现有Qt窗口的句柄（关键优化点）
        self._hwnd = int(self._parent_widget.winId())

        # 注册Shell钩子
        self._user32 = ctypes.WinDLL('user32')
        self._user32.RegisterShellHookWindow.argtypes = [wintypes.HWND]
        self._user32.RegisterShellHookWindow.restype = wintypes.BOOL
        self._user32.RegisterShellHookWindow(self._hwnd)

        # 替换窗口过程
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            self._original_wnd_proc = win32gui.SetWindowLong(
                self._hwnd, win32con.GWL_WNDPROC, self._wnd_proc
            )
        else:
            self._original_wnd_proc = win32gui.SetWindowLongPtr(
                self._hwnd, win32con.GWL_WNDPROC, self._wnd_proc
            )

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg in (win32con.WM_DISPLAYCHANGE, win32con.WM_SETTINGCHANGE):
            self._check_workarea_changes()
        return win32gui.CallWindowProc(self._original_wnd_proc, hwnd, msg, wparam, lparam)

    def _check_workarea_changes(self):
        new_state = []

        @ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                            ctypes.POINTER(wintypes.RECT), ctypes.c_double)
        def _monitor_callback(hmonitor, hdc, lprect, lparam):
            info = win32api.GetMonitorInfo(hmonitor)
            new_state.append(WorkAreaInfo(
                screen_rect=QRect(
                    info['Monitor'][0],  # left
                    info['Monitor'][1],  # top
                    info['Monitor'][2] - info['Monitor'][0],  # width (right - left)
                    info['Monitor'][3] - info['Monitor'][1]  # height (bottom - top)
                ),
                work_rect=QRect(
                    info['Work'][0],  # left
                    info['Work'][1],  # top
                    info['Work'][2] - info['Work'][0],  # width
                    info['Work'][3] - info['Work'][1]  # height
                )
            ))

            return 1

        ctypes.windll.user32.EnumDisplayMonitors(None, None, _monitor_callback, 0)
        if new_state != self._last_state:
            self._last_state = new_state
            self.update_workarea_infos(new_state)
            logger.info(f"屏幕变化，联合矩阵：{self.combined_rect.getRect()}")
            logger.info(f"屏幕变化，屏幕列表：{self.get_screens_tuple_list()}")

            self.workarea_changed.emit(self.workarea_infos)

    def update_workarea_infos(self, new_state: list[WorkAreaInfo]):
        """更新所有工作区域信息"""
        combined = QRect()
        screens_info = []

        # 首先计算联合矩形
        for screen in new_state:
            combined = combined.united(screen.screen_rect)
        screen_infos = [f"屏幕 {i}: {screen.work_rect.getRect()}" for i, screen in enumerate(new_state)]
        # 然后计算每个屏幕相对于联合矩形的偏移量
        for screen in new_state:
            screens_info.append(WorkAreaInfo(
                screen_rect=QRect(
                    screen.screen_rect.x() - combined.x(),
                    screen.screen_rect.y() - combined.y(),
                    screen.screen_rect.width(),
                    screen.screen_rect.height()
                ),
                work_rect=QRect(
                    screen.work_rect.x() - combined.x(),
                    screen.work_rect.y() - combined.y(),
                    screen.work_rect.width(),
                    screen.work_rect.height()
                )
            ))
        self.workarea_infos = screens_info
        self.combined_rect = combined

    def nativeEventFilter(self, eventType, message):
        msg = wintypes.MSG.from_address(message.__int__())
        if msg.message in (win32con.WM_DISPLAYCHANGE, win32con.WM_SETTINGCHANGE):
            self._check_workarea_changes()
        return False, 0

    def adjust_offset_screen(self, offset: QPoint, cur_anchor_pos: QPoint, portal_enabled: bool = True):
        if config.screen_connect_enabled:  # 循环屏幕
            new_offset = self.adjust_offset_screen_connect(offset, cur_anchor_pos, portal_enabled=portal_enabled)  # 循环屏幕
        else:
            new_offset = self.adjust_offset_screen_unconnect(offset, cur_anchor_pos)  # 普通移动，确保不会超出本屏幕
        return new_offset

    def adjust_offset_screen_unconnect(self, offset: QPoint, cur_anchor_pos: QPoint):
        """调整偏移量，确保图片不会超出桌面范围"""
        new_offset = QPoint(offset)
        combined_width = self.combined_rect.width()
        new_x = cur_anchor_pos.x() + new_offset.x()
        mew_x = max(0, new_x)
        new_x = min(mew_x, combined_width - 1)
        new_offset.setX(new_x - cur_anchor_pos.x())
        return new_offset

    def adjust_offset_screen_connect(self, offset: QPoint, cur_anchor_pos: QPoint, portal_enabled: bool = True):
        """调整偏移量，实现循环屏幕效果"""
        new_offset = QPoint(offset)
        combined_width = self.combined_rect.width()
        new_x = cur_anchor_pos.x() + new_offset.x()
        new_y = cur_anchor_pos.y() + new_offset.y()

        adjust_new_x = int(self.cal_x_connect_f(new_x))
        if portal_enabled and 0 <= new_y < self.combined_rect.height():
            if adjust_new_x < new_x:  # 右边消失，左边出现
                handle_portal(QPoint(0, new_y), self._parent_widget, turn_right=False, exit_flag=True)  # 出口传送门
                handle_portal(QPoint(combined_width - 1, new_y), self._parent_widget, turn_right=True, exit_flag=False)  # 入口传送门
            elif adjust_new_x > new_x:  # 左边消失，右边出现
                handle_portal(QPoint(combined_width - 1, new_y), self._parent_widget, turn_right=True, exit_flag=True)  # 出口传送门
                handle_portal(QPoint(0, new_y), self._parent_widget, turn_right=False, exit_flag=False)  # 入口传送门
        new_offset = QPointF(adjust_new_x - cur_anchor_pos.x(), new_offset.y()).toPoint() # 防止水平溢出报错
        return new_offset

    def get_cur_work_by_xy_f(self, pos_f: QPointF) -> Optional[QRect]:
        """根据x,y坐标获取当前工作区域(第一个匹配的屏幕)"""
        work_area_infos = self.get_screens()
        for work_area_info in work_area_infos:
            work_rect = work_area_info.work_rect
            if work_rect.contains(pos_f.toPoint()):
                return work_area_info.work_rect
        return None

    def get_cur_screen_work(self, pos: QPoint) -> QRect:
        """
        获取当前屏幕的工作区域
        1. 首先尝试根据锚点的x,y坐标找到完全包含它的屏幕
        2. 如果找不到，则仅根据x坐标判断所在屏幕
        3. 如果仍然找不到，则返回第一个屏幕的工作区域
        4. 如果未找到任何工作区域，则返回默认值(2560x1440)
        :return: 所在屏幕的工作区域
        """

        def get_cur_work_by_xy(pos: QPoint, screen_monitor: ScreenMonitor) -> Optional[QRect]:
            """根据x,y坐标获取当前工作区域(第一个匹配的屏幕)"""
            work_area_infos = screen_monitor.get_screens()
            for work_area_info in work_area_infos:
                screen_rect = work_area_info.screen_rect
                if screen_rect.contains(pos):
                    return work_area_info.work_rect
            return None

        def get_cur_work_by_x(pos: QPoint, screen_monitor: ScreenMonitor) -> Optional[QRect]:
            """根据x坐标获取当前工作区域(第一个匹配的屏幕)"""
            work_area_infos = screen_monitor.get_screens()
            for work_area_info in work_area_infos:
                screen_rect = work_area_info.screen_rect
                if screen_rect.left() <= pos.x() <= screen_rect.right():
                    return work_area_info.work_rect
            return None

        if self.get_screens():
            cur_work = get_cur_work_by_xy(pos, self)
            if not cur_work:
                cur_work = get_cur_work_by_x(pos, self)
                if not cur_work:
                    logger.error(f"未找到包含点 {pos} 的工作区域,返回第一个屏幕的工作区域")
                    cur_work = self.get_screens()[0].work_rect
            return cur_work
        return QRect(0, 0, 2560, 1440)  # 未找到任何工作区域时，返回默认值

    def get_cur_screen_work_bottom(self, pos: QPoint) -> int:
        # 获取当前屏幕的工作区域底部坐标
        cur_work = self.get_cur_screen_work(pos)
        return cur_work.bottom()

    def in_global_screen_rect_f(self, pos: QPointF) -> bool:
        # 判断点是否在全局屏幕矩形内
        global_screen_rect = self.combined_rect  # combined_rect 是 全局位置
        if 0 <= pos.x() <= global_screen_rect.width() and 0 <= pos.y() <= global_screen_rect.height():
            return True
        return False

    def cal_x_connect_f(self, x: float) -> float:
        # 计算x坐标，确保在全局屏幕矩形内（窗口连接模式）
        combined_width = self.combined_rect.width()
        while x < 0 or combined_width <= x:
            if x < 0:
                overflow = -x
                x = combined_width - overflow
            elif x >= combined_width:
                overflow = x - combined_width
                x = overflow
        return x

    def adjust_pos_connect_f(self, pos: QPointF) -> QPointF:
        # 调整点位置，确保在全局屏幕矩形内（窗口连接模式）
        new_pos = QPointF(pos)
        new_x = new_pos.x()
        new_x = self.cal_x_connect_f(new_x)
        new_pos.setX(new_x)
        return new_pos


# 使用示例


if __name__ == "__main__":
    class MyWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("显示器监听示例")
            self.resize(300, 200)

            # 初始化监听器（传入自身窗口）
            self.screen_monitor = ScreenMonitor(parent_widget=self)
            self.screen_monitor.workarea_changed.connect(self.handle_display_change)
            a = self.screen_monitor.get_screens()
            print(a)

            # self.screen_monitor._check_workarea_changes()

        def handle_display_change(self, screens):
            print("\n\n=== 显示器配置变化 ===")
            for i, screen in enumerate(screens):
                print(f"显示器 {i + 1}: 物理区域 {screen.screen_rect.getRect()}")
                print(f"显示器 {i + 1}: 工作区域 {screen.work_rect.getRect()}")
            print("\n\n")


    import sys

    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())
