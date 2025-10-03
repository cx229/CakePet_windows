# from turtle import config_dict
from types import SimpleNamespace
from typing import Dict, Any, TYPE_CHECKING

from PyQt5.QtCore import QPoint, QPointF


class Signal:
    def __init__(self, name):
        self.name = name
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def send(self, sender, **kwargs):
        for callback in self._callbacks:
            callback(sender, **kwargs)


class ObservableMeta(type):
    """元类：自动生成信号 + 单例控制 + 清理类属性"""
    _instance = None

    def __new__(cls, name, bases, attrs):
        # 提取所有非私有、非方法的属性作为配置项

        config_items = {}
        # 遍历所有父类
        for base in bases:
            # 获取父类的非私有、非方法属性
            if hasattr(base, '_data'):
                base_items = {
                    k: v for k, v in getattr(base, '_data').items()
                    if not k.startswith('_') and not callable(v)
                }
                config_items.update(base_items)

        # 添加当前类的属性
        current_items = {
            k: v for k, v in attrs.items()
            if not k.startswith('_') and not callable(v)
        }

        config_items.update(current_items)

        # 创建新属性字典，移除原始配置项
        new_attrs = {
            k: v for k, v in attrs.items()
            if k.startswith('_') or callable(v)
        }
        new_attrs['_data'] = config_items

        return super().__new__(cls, name, bases, new_attrs)


class BaseObservable(metaclass=ObservableMeta):
    def __init__(self):
        import copy
        self.__dict__['_obj_data'] = copy.deepcopy(self._data)  # 深拷贝配置数据
        self.__dict__['_signals'] = {}  # 存储信号对象

        for key in self._data.keys():
            signal_name = f"{key}_changed"
            _signal = Signal(signal_name)
            setattr(self, signal_name, _signal)
            self._signals[key] = _signal

    def __setattr__(self, key, value):
        if key in self._obj_data:
            current_value = self._obj_data[key]
            if current_value != value:  # 处理值变化
                self._obj_data[key] = value
                self._signals[key].send(self, value=value)
        else:
            super().__setattr__(key, value)

    def __getattr__(self, key):
        if key in self._obj_data:
            return self._obj_data[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


class Config(BaseObservable):
    mode_name = "base"

    follow_update_interval = 3  # 跟随更新间隔（毫秒），不论什么模式，指的是定时器间隔

    drag_follow_enabled = True  # 是否开启拖动功能
    is_drag_follow = False  # 是否正在拖动

    throw_follow_enabled = True
    is_throw_follow = False  # 是否正在下落
    throw_follow_acceleration = QPointF(0, 0.02)  # 抛掷重力速度, 单位: 像素/s2
    throw_follow_radio = QPointF(1, 0.8)  # 抛掷的初速度与重力速度的比例
    throw_follow_speed = QPointF(0, 0)  # 抛掷速度，单位: 像素/s

    mouse_follow_enabled = True  # 是否开启跟随鼠标
    is_mouse_follow = False  # 是否正在跟随鼠标
    mouse_follow_speed = 5  # 每次的跟随，移动的像素点长度，跟随速度，单位:像素/s

    anchor_pos = QPoint(500, 500)  # 锚点坐标

    bigger_flag = False  # 放大的标志位


config = Config()
