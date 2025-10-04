
import yaml
from PyQt5.QtCore import QPoint, QPointF

from utils.log_util import logger


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
    screen_connect_enabled: bool = None  # 是否开启屏幕连接功能
    click_through_enabled: bool = None  # 是否开启点击穿透功能
    key_ctrl_l_only: bool = False  # 监听结果，是否只有Ctrl+L按下

    mode_name = "base"
    size_ratio: float = 1.0  # 当前大小比例
    size_ratio_base: float = None  # 大小比例基数
    standard_anchor_pos = QPoint(64, 128)  # 标准锚点坐标

    follow_update_interval = 3  # 跟随更新间隔（毫秒），不论什么模式，指的是定时器间隔

    drag_follow_enabled: bool = None  # 是否开启拖动功能
    is_drag_follow = False  # 是否正在拖动

    throw_follow_enabled: bool = None
    is_throw_follow = False  # 是否正在下落
    throw_follow_acceleration = QPointF(0, 0.02)  # 抛掷重力速度, 单位: 像素/s2
    throw_follow_radio = QPointF(1, 0.8)  # 抛掷的初速度与重力速度的比例
    throw_follow_speed = QPointF(0, 0)  # 抛掷速度，单位: 像素/s

    mouse_follow_enabled: bool = None  # 是否开启跟随鼠标
    is_mouse_follow = False  # 是否正在跟随鼠标
    mouse_follow_speed = 5  # 每次的跟随，移动的像素点长度，跟随速度，单位:像素/s

    anchor_pos = QPoint(500, 500)  # 锚点坐标

    bigger_enabled: bool = None  # 是否开启放大功能
    bigger_flag = False  # 放大的标志位
    bigger_wait_time: int = None  # 等待时间，单位: 毫秒
    bigger_max_size_ratio: float = None  # 最大放大比例


config_path = "config.yaml"
config = Config()



def load_config():
    # Default configuration values
    default_config = {
        "size_ratio_base": 1.0,
        "click_through_enabled": True,
        "screen_connect_enabled": True,
        "drag_follow_enabled": True,
        "throw_follow_enabled": True,
        "mouse_follow_enabled": True,
        "bigger_enabled": True,
        "bigger_wait_time": 45 * 60 * 1000,  # 45 minutes in milliseconds
        "bigger_max_size_ratio": 10.0
    }

    try:
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f) or {}
            yaml_config = {k: v for k, v in yaml_config.items() if v is not None}

            # Update default values with any valid values from the config file
            for key, default_value in default_config.items():
                setattr(config, key, yaml_config.get(key, default_value))

    except FileNotFoundError:
        logger.info(f"配置文件 {config_path} 不存在，使用默认配置")
        for key, value in default_config.items():
            setattr(config, key, value)
    except Exception as e:
        logger.error(f"加载配置文件 {config_path} 时出错，使用默认配置，错误信息: {e}")
        for key, value in default_config.items():
            setattr(config, key, value)


# def load_config():
#     with open(config_path, 'r') as f:
#         yaml_config = yaml.safe_load(f) or {}
#         yaml_config = {k: v for k, v in yaml_config.items() if v is not None}
#         if yaml_config:
#             config.size_ratio_base = yaml_config.get("size_ratio_base", 1.0)
#             config.click_through_enabled = yaml_config.get("click_through_enabled", True)
#             config.screen_connect_enabled = yaml_config.get("screen_connect_enabled", True)
#             config.drag_follow_enabled = yaml_config.get("drag_follow_enabled", True)
#             config.throw_follow_enabled = yaml_config.get("throw_follow_enabled", True)
#             config.mouse_follow_enabled = yaml_config.get("mouse_follow_enabled", True)
#             config.bigger_enabled = yaml_config.get("bigger_enabled", True)
#             config.bigger_wait_time = yaml_config.get("bigger_wait_time", 45 * 60 * 1000)
#             config.bigger_max_size_ratio = yaml_config.get("bigger_max_size_ratio", 10.0)


def save_config(sender, value):
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml_config = {
            "size_ratio_base": config.size_ratio_base,
            "click_through_enabled": config.click_through_enabled,
            "screen_connect_enabled": config.screen_connect_enabled,
            "drag_follow_enabled": config.drag_follow_enabled,
            "throw_follow_enabled": config.throw_follow_enabled,
            "mouse_follow_enabled": config.mouse_follow_enabled,
            "bigger_enabled": config.bigger_enabled,
            "bigger_wait_time": config.bigger_wait_time,
            "bigger_max_size_ratio": config.bigger_max_size_ratio,
        }
        yaml.safe_dump(yaml_config, f, default_flow_style=False, sort_keys=False)


load_config()
config.size_ratio_base_changed.connect(save_config)
config.click_through_enabled_changed.connect(save_config)
config.screen_connect_enabled_changed.connect(save_config)
config.drag_follow_enabled_changed.connect(save_config)
config.throw_follow_enabled_changed.connect(save_config)
config.mouse_follow_enabled_changed.connect(save_config)
config.bigger_enabled_changed.connect(save_config)
config.bigger_wait_time_changed.connect(save_config)
config.bigger_max_size_ratio_changed.connect(save_config)
