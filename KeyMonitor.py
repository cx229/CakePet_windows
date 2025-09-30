from pynput import keyboard
import threading
import time


class KeyMonitor:
    def __init__(self):
        self.pressed_keys = set()  # 记录当前按下的键
        self.listener = None  # 监听器对象
        self.is_running = False  # 监听状态标志

    def on_press(self, key):
        self.pressed_keys.add(key)
        # self.check_ctrl_only()

    def on_release(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def check_key(self, key: keyboard.Key, is_only=False):
        """检查某个键是否按下（可选是否唯一按下）"""
        return key in self.pressed_keys and (not is_only or len(self.pressed_keys) == 1)

    def check_ctrl_only(self):
        """检查是否只有 Ctrl 键被按下（左或右）"""
        ctrl_keys = {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
        is_only_ctrl = len(self.pressed_keys) > 0 and all(
            key in ctrl_keys for key in self.pressed_keys)
        if is_only_ctrl:
            print("仅 Ctrl 键被按下")

    def start(self):
        """启动监听线程"""
        if not self.is_running:
            self.is_running = True
            self.listener = keyboard.Listener(
                on_press=self.on_press, on_release=self.on_release)
            self.listener.start()  # 非阻塞启动
            print("键盘监听已启动")

    def stop(self):
        """停止监听线程"""
        if self.is_running and self.listener:
            self.is_running = False
            self.listener.stop()  # 停止监听
            self.listener = None
            print("键盘监听已停止")


key_monitor = KeyMonitor()
key_monitor.start()  # 启动监听线程

# 使用示例
if __name__ == "__main__":
    key_monitor = KeyMonitor()
    key_monitor.start()  # 启动监听线程

    try:
        # 主程序继续运行（这里用死循环模拟，实际可能是 GUI 或任务循环）
        while True:
            print("主程序正在运行...")
            time.sleep(1)
    except KeyboardInterrupt:
        key_monitor.stop()  # 按 Ctrl+C 停止
