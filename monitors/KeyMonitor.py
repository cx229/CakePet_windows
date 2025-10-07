import queue
from typing import TYPE_CHECKING, Optional

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget
from pynput import keyboard
import time

from configs import config
from resmeta.tray_msg_meta import TragMsgs, get_key_speed_tray_msg

if TYPE_CHECKING:
    from module_controllers.TrayMsgController import TrayMsgController

_VK_TO_NAME = {
    # 字母键 A-Z (65-90)
    65: 'A', 66: 'B', 67: 'C', 68: 'D', 69: 'E', 70: 'F', 71: 'G', 72: 'H',
    73: 'I', 74: 'J', 75: 'K', 76: 'L', 77: 'M', 78: 'N', 79: 'O', 80: 'P',
    81: 'Q', 82: 'R', 83: 'S', 84: 'T', 85: 'U', 86: 'V', 87: 'W', 88: 'X',
    89: 'Y', 90: 'Z',

    # 数字键 0-9 (48-57)
    48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7',
    56: '8', 57: '9',

    # 符号键（主键盘区）
    192: '`', 189: '-', 187: '=', 219: '[', 221: ']', 220: '\\', 186: ';',
    222: "'", 188: ',', 190: '.', 191: '/',

    # 功能键 F1-F24 (112-135)
    112: 'F1', 113: 'F2', 114: 'F3', 115: 'F4', 116: 'F5', 117: 'F6',
    118: 'F7', 119: 'F8', 120: 'F9', 121: 'F10', 122: 'F11', 123: 'F12',
    # F13-F24 通常需要特殊键盘支持
    124: 'F13', 125: 'F14', 126: 'F15', 127: 'F16', 128: 'F17', 129: 'F18',
    130: 'F19', 131: 'F20', 132: 'F21', 133: 'F22', 134: 'F23', 135: 'F24',

    # 修饰键
    160: 'Shift', 161: 'Shift', 162: 'Ctrl', 163: 'Ctrl', 164: 'Alt', 165: 'Alt',
    91: 'Win', 92: 'Win', 93: 'Menu',

    # 导航键
    33: 'PageUp', 34: 'PageDown', 35: 'End', 36: 'Home', 45: 'Insert', 46: 'Delete',

    # 方向键
    37: 'Left', 38: 'Up', 39: 'Right', 40: 'Down',

    # 数字小键盘
    96: 'Num0', 97: 'Num1', 98: 'Num2', 99: 'Num3', 100: 'Num4', 101: 'Num5',
    102: 'Num6', 103: 'Num7', 104: 'Num8', 105: 'Num9', 106: 'Num*', 107: 'Num+',
    109: 'Num-', 110: 'Num.', 111: 'Num/',

    # 其他常用键
    13: 'Enter', 27: 'Esc', 32: 'Space', 8: 'Backspace', 9: 'Tab', 20: 'CapsLock',
    144: 'NumLock', 145: 'ScrollLock', 19: 'Pause', 44: 'PrintScreen',

    # 多媒体键（部分键盘支持）
    173: 'Mute', 174: 'VolumeDown', 175: 'VolumeUp', 176: 'NextTrack',
    177: 'PreviousTrack', 178: 'Stop', 179: 'Play/Pause',

    # 鼠标键（通常不会触发键盘监听，但列出以防万一）
    1: 'MouseLeft', 2: 'MouseRight', 3: 'MouseMiddle',
}


class KeyMonitor:
    def __init__(self):
        self.last_key_speed = None
        self.pressed_keys: set[keyboard.Key] = set()  # 记录当前按下的键
        self.listener = None  # 监听器对象
        self.is_running = False  # 监听状态标志
        self.tray_msg_controller: Optional['TrayMsgController'] = None  # 托盘消息控制器

        self.key_speed_timer = None
        self.total_update_config_timer = None  # 按键总次数更新定时器
        self.key_today_total = 0  # 按键总次数
        self.key_queue: queue.Queue = queue.Queue()  # 存入按键时间列表

        config.tray_key_info_enabled_changed.connect(self._on_key_info_enabled_changed)  # 按键信息配置改变时调用

    def _on_key_info_enabled_changed(self, sender, value):
        """按键信息配置改变时调用"""
        if value:
            if self.key_speed_timer:
                self.key_speed_timer.start(5000)  # 每5秒检查一次按键速度
            if self.total_update_config_timer:
                self.total_update_config_timer.start(1000)  # 每60秒更新一次按键总次数
            self.last_key_speed = None  # 重置最后记录的按键速度
            self._check_total_update_config()  # 初始化按键总次数

        else:
            if self.key_speed_timer:
                self.key_speed_timer.stop()
            if self.total_update_config_timer:
                self.total_update_config_timer.stop()
            self.key_queue: queue.Queue = queue.Queue()  # 存入按键时间列表
            self.tray_msg_controller.set_default_tray_msg(tray_msg=TragMsgs.Default.DEFAULT.value)  # 重置默认消息

    def get_pressed_keys(self) -> str:
        """获取当前按下的键的字符串表示"""
        return ", ".join([_VK_TO_NAME.get(key, str(key)) for key in self.pressed_keys])

    def _on_press(self, key):
        if hasattr(key, 'vk'):
            key_add = key.vk  # 虚拟键
            if config.tray_key_info_enabled:
                self.key_queue.put(time.time())  # 记录按键时间
                self.key_today_total += 1  # 按键总次数增加
        else:
            key_add = key  # 非虚拟键
        if key_add not in self.pressed_keys:
            self.pressed_keys.add(key_add)
            self._update_config_ctrl_l_only()

    def _on_release(self, key):
        if hasattr(key, 'vk'):
            key_remove = key.vk
        else:
            key_remove = key
        if key_remove in self.pressed_keys:
            self.pressed_keys.remove(key_remove)
            self._update_config_ctrl_l_only()

    def _update_config_ctrl_l_only(self):
        """根据当前按下的键更新配置"""
        config.key_ctrl_l_only = self.check_ctrl_only()

    def check_key(self, key: keyboard.Key, is_only=False):
        """检查某个键是否按下（可选是否唯一按下）"""
        return key in self.pressed_keys and (not is_only or len(self.pressed_keys) == 1)

    def check_ctrl_only(self) -> bool:
        """检查是否只有 Ctrl 键被按下（左或右）"""
        ctrl_keys = {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
        is_only_ctrl = len(self.pressed_keys) > 0 and all(
            key in ctrl_keys for key in self.pressed_keys)
        return is_only_ctrl

    def start(self):
        """启动监听线程"""
        if not self.is_running:
            self.is_running = True
            self.listener = keyboard.Listener(
                on_press=self._on_press, on_release=self._on_release)
            self.listener.start()  # 非阻塞启动

    def stop(self):
        """停止监听线程"""
        if self.is_running and self.listener:
            self.is_running = False
            self.listener.stop()  # 停止监听
            self.listener = None

    def connect_tray_msg_controller(self, widget: QWidget, tray_msg_controller: 'TrayMsgController'):
        """连接托盘消息"""
        self.tray_msg_controller = tray_msg_controller

        self.key_speed_timer = QTimer(widget)  # 按键速度定时器
        self.key_speed_timer.timeout.connect(self._check_key_speed)  # 按键速度定时器超时调用

        self.total_update_config_timer = QTimer(widget)  # 按键总次数更新定时器
        self.total_update_config_timer.timeout.connect(self._check_total_update_config)  # 按键总次数更新定时器超时调用

        self._on_key_info_enabled_changed(None, config.tray_key_info_enabled)  # 初始化 配置

    def _check_key_speed(self):
        """检查按键速度"""
        if self.tray_msg_controller:
            # 获取当前时间：
            current_time = time.time()  # 当前时间
            # 删除队列中一分钟前的数据
            while not self.key_queue.empty() and current_time - self.key_queue.queue[0] > 60:
                self.key_queue.get()
            key_speed = self.key_queue.qsize()
            if key_speed != self.last_key_speed:
                # 计算按键速度（按键数 / 时间间隔）
                if key_speed > 0:
                    self.tray_msg_controller.set_default_tray_msg(tray_msg=get_key_speed_tray_msg(key_speed, self.key_today_total))
                else:
                    self.tray_msg_controller.set_default_tray_msg(tray_msg=TragMsgs.Default.DEFAULT.value)
                self.last_key_speed = key_speed  # 更新最后记录的按键速度

    def _check_total_update_config(self):
        """检查按键总次数更新配置"""
        if config.tray_key_info_enabled:
            cur_date = time.strftime("%Y-%m-%d", time.localtime())
            if config.tray_key_today_date != cur_date:  # 日期改变，重置按键总次数
                config.tray_key_today_date = cur_date
                config.tray_key_today_total = 0
                self.key_today_total = 0  # 重置按键总次数, 因为是新的一天
                # print(f"日期改变，重置按键总次数: {config.tray_key_today_total} -> {self.key_today_total}")
            elif config.tray_key_today_total != self.key_today_total:  # 相同日期的情况，更新按键总次数
                if self.key_today_total > config.tray_key_today_total:
                    config.tray_key_today_total = self.key_today_total
                else:
                    self.key_today_total = config.tray_key_today_total


# 使用示例
if __name__ == "__main__":
    key_monitor = KeyMonitor()
    key_monitor.start()  # 启动监听线程

    try:
        # 主程序继续运行（这里用死循环模拟，实际可能是 GUI 或任务循环）
        while True:
            # 按键信息
            print(f"按键信息: {key_monitor.get_pressed_keys()}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        key_monitor.stop()  # 按 Ctrl+C 停止
