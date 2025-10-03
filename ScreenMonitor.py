import ctypes
from dataclasses import dataclass
from PyQt5.QtCore import QRect, QObject, pyqtSignal, QAbstractNativeEventFilter, QPoint
from PyQt5.QtWidgets import QApplication, QWidget
import win32api
import win32con
import win32gui
from ctypes import wintypes


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
        self._last_state = []
        self._check_workarea_changes()  # 初始化时获取一次状态

        # 获取最左的工作区域，如果小于当前锚点x坐标，则返回最左工作区域底部坐标
        # left_work_area = min(work_area_infos, key=lambda x: x.work_rect.left())
        # if left_work_area.work_rect.left() >= cur_anchor_pos.x():
        #     logger.info(f"未找到包含锚点 {cur_anchor_pos} 的工作区域，返回最左工作区域底部坐标: {left_work_area.work_rect.bottom()}")
        #
        #     return left_work_area.work_rect.bottom()
        #
        # # 如果最右的工作区域也小于当前锚点x坐标，则返回最右工作区域底部坐标
        # right_work_area = max(work_area_infos, key=lambda x: x.work_rect.right())
        # if right_work_area.work_rect.right() <= cur_anchor_pos.x():
        #     logger.info(f"未找到包含锚点 {cur_anchor_pos} 的工作区域，返回最右工作区域底部坐标: {right_work_area.work_rect.bottom()}")
        #     return right_work_area.work_rect.bottom()

    def get_left_screen(self) -> WorkAreaInfo:
        return min(self._last_state, key=lambda x: x.work_rect.left())

    def get_right_screen(self) -> WorkAreaInfo:
        return max(self._last_state, key=lambda x: x.work_rect.right())

    def get_screens(self) -> list[WorkAreaInfo]:
        return self._last_state

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
            # new_state.append(WorkAreaInfo(
            #     screen_rect=QRect(*info['Monitor']),
            #     work_rect=QRect(*info['Work'])
            # ))
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
            self.workarea_changed.emit(new_state)

    def nativeEventFilter(self, eventType, message):
        msg = wintypes.MSG.from_address(message.__int__())
        if msg.message in (win32con.WM_DISPLAYCHANGE, win32con.WM_SETTINGCHANGE):
            self._check_workarea_changes()
        return False, 0

def get_cur_work_bottom(anchor_pos:QPoint, screen_monitor:ScreenMonitor):
    """
    获取当前工作区域的底部坐标
    1. 首先尝试根据锚点的x,y坐标找到完全包含它的屏幕
    2. 如果找不到，则仅根据x坐标判断所在屏幕
    :return: 所在屏幕底部坐标
    """
    cur_anchor_pos = anchor_pos
    work_area_infos = screen_monitor.get_screens()

    # 首先尝试精确匹配（x和y都匹配）
    for work_area_info in work_area_infos:
        if work_area_info.screen_rect.contains(cur_anchor_pos):
            return work_area_info.work_rect.bottom()

    # 如果没有精确匹配，则仅根据x坐标匹配
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
            self.setWindowTitle("显示器监听示例")
            self.resize(300, 200)

            # 初始化监听器（传入自身窗口）
            self.screen_monitor = ScreenMonitor(parent_widget=self)
            self.screen_monitor.workarea_changed.connect(self.handle_display_change)
            a = self.screen_monitor.get_screens()
            print(a)

            # self.screen_monitor._check_workarea_changes()

        def handle_display_change(self, screens):
            print("\n=== 显示器配置变化 ===")
            for i, screen in enumerate(screens):
                print(f"显示器 {i + 1}: 物理区域 {screen.screen_rect.getRect()}")
                print(f"显示器 {i + 1}: 工作区域 {screen.work_rect.getRect()}")


    import sys

    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())
