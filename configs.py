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


class GlobalConfig(BaseObservable):
    """ 全局配置 """
    logger_only_error: bool = None  # 是否仅记录错误日志
    img_hide_flag = False  # 是否隐藏图片
    screen_connect_enabled: bool = None  # 是否开启屏幕连接功能
    click_through_enabled: bool = None  # 是否开启点击穿透功能
    key_ctrl_l_only: bool = False  # 监听结果，是否只有Ctrl+L按下
    mode_name = "base"
    size_ratio: float = 1.0  # 当前大小比例
    size_ratio_base: float = None  # 大小比例基数
    standard_anchor_pos = QPoint(64, 128)  # 标准锚点坐标
    anchor_pos = QPoint(500, 500)  # 锚点坐标

    """ 跟随模式配置 """
    follow_update_interval = None  # 跟随更新间隔（毫秒），不论什么模式，指的是定时器间隔
    throw_follow_max_speed_ms:int  = None  # 最大抛掷速度，单位: 像素/ms

    drag_follow_enabled: bool = None  # 是否开启拖动功能
    is_drag_follow = False  # 是否正在拖动

    throw_follow_enabled: bool = None
    throw_follow_rebound_enabled: bool = None  # 是否开启反弹功能
    throw_follow_rebound_up_enabled: bool = None  # 是否开启反弹-上 功能
    throw_follow_rebound_down_enabled: bool = None  # 是否开启反弹-下 功能
    throw_follow_rebound_left_right_enabled: bool = None  # 是否开启反弹-左右 功能
    throw_follow_rebound_ratio: float = None  # 反弹系数
    is_throw_follow = False  # 是否正在下落
    gravity_enable: bool = True  # 是否开启重力功能 处理一些临时关闭重力的情况
    # throw_follow_acceleration = QPointF(0, 0.01)  # 抛掷重力速度, 单位: 像素/s2
    throw_follow_gravity = None  # 抛掷重力速度 ms
    # throw_follow_radio = QPointF(1, 0.8)  # 抛掷的初速度与鼠标速度的比例
    throw_follow_speed = QPointF(0, 0)  # 抛掷速度(每次刷新时）

    mouse_follow_enabled: bool = None  # 是否开启跟随鼠标
    is_mouse_follow = False  # 是否正在跟随鼠标
    mouse_follow_speed = None  # 每次的跟随，移动的像素点长度，跟随速度，单位:像素/s

    """ 放大模式配置 """
    bigger_enabled: bool = None  # 是否开启放大功能
    bigger_flag = False  # 放大的标志位
    bigger_wait_time: int = None  # 等待时间，单位: 毫秒
    bigger_max_size_ratio: float = None  # 最大放大比例

    """ 托盘消息配置 """
    tray_msg_enabled: bool = None  # 是否开启托盘消息
    tray_key_info_enabled: bool = None  # 是否开启按键速度功能
    tray_key_today_date: str = None  # 托盘消息-键盘信息-当前日期
    tray_key_today_total: int = None  # 托盘消息-键盘信息-当前日期的总按键次数
    tray_msg_position_tray: bool = None  # True 表示托盘左侧显示，False 表示任务栏左侧显示
    tray_msg_color_white: bool = None  # 托盘消息是否为白色
    tray_msg_margin: int = None  # 托盘消息与图标之间的间距，默认0

    """ 按键速度配置 """


config_path = "config.yaml"
config = GlobalConfig()

default_config = {
    "logger_only_error": True,  # 是否仅记录错误日志，默认打开，避免文件过多
    "size_ratio_base": 1.5,  # 大小比例基数，默认1.5倍
    "click_through_enabled": False,  # 是否开启点击穿透功能，默认关闭
    "screen_connect_enabled": True,  # 是否开启屏幕连接功能，默认开启
    "drag_follow_enabled": True,  # 是否开启拖动功能，默认开启
    "follow_update_interval": 3,  # 跟随更新间隔（毫秒），不论什么模式，指的是定时器间隔
    "throw_follow_max_speed_ms": 10,  # 最大抛掷速度，单位: 像素/ms
    "throw_follow_enabled": True,  # 是否开启抛掷功能，默认开启
    "throw_follow_gravity": 0.01,  # 抛掷重力速度 ms
    "throw_follow_rebound_enabled": True,  # 是否开启反弹功能，默认开启
    "throw_follow_rebound_up_enabled": True,  # 是否开启反弹-上 功能, 默认开启
    "throw_follow_rebound_down_enabled": True,  # 是否开启反弹-下 功能, 默认开启
    "throw_follow_rebound_left_right_enabled": True,  # 是否开启反弹-左右 功能, 默认开启
    "throw_follow_rebound_ratio": 0.8,  # 反弹系数
    "mouse_follow_enabled": False,  # 是否开启跟随鼠标功能，默认关闭
    "mouse_follow_speed": 5,  # 每次的跟随，移动的像素点长度，跟随速度，单位:像素/s
    "bigger_enabled": True,  # 是否开启放大功能，默认开启
    "bigger_wait_time": 45 * 60 * 1000,  # 45 minutes in milliseconds
    "bigger_max_size_ratio": 10.0, # 最大放大比例，默认10倍
    "tray_msg_enabled": True, # 是否开启托盘消息功能，默认开启
    "tray_key_info_enabled": True,  # 是否开启按键信息功能, 默认开启
    "tray_key_today_date": None,  # 托盘消息-键盘信息-当前日期
    "tray_key_today_total": 0,  # 托盘消息-键盘信息-当前日期的总按键次数
    "tray_msg_position_tray": True, # 是否开启托盘位置是托盘，默认 True
    "tray_msg_color_white": True,  # 托盘消息是否为白色，默认 True
    "tray_msg_margin": 0,  # 托盘消息与图标之间的间距，默认0
}


def load_config():
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


def save_config(sender, value):
    # 自动保存所有配置项，避免手动列出每个字段
    config_dict = {key: getattr(config, key)
                   for key in default_config.keys()
                   if hasattr(config, key)}

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_dict, f, default_flow_style=False, sort_keys=False)


load_config()

# 自动连接所有配置项的changed信号
for key in default_config.keys():
    if hasattr(config, f"{key}_changed"):
        getattr(config, f"{key}_changed").connect(save_config)
