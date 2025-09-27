# 定义全局信号
from blinker import Signal

keywords = {}

switch_mode_signal = Signal("switch-mode")  # 模式切换信号

def switch_mode(mode_name):
    """外部调用切换模式"""
    switch_mode_signal.send(mode_name=mode_name)  # 触发信号