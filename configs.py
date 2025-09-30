from blinker import signal


class ConfigMeta(type):
    """元类：自动生成信号 + 单例控制 + 清理类属性"""
    _instance = None

    def __new__(cls, name, bases, attrs):
        # 提取所有非私有、非方法的属性作为配置项
        config_items = {
            k: v for k, v in attrs.items()
            if not k.startswith('_') and not callable(v)
        }

        # 创建新属性字典，移除原始配置项
        new_attrs = {
            k: v for k, v in attrs.items()
            if k.startswith('_') or callable(v) or k in config_items
        }

        # 动态生成信号
        for key in config_items:
            new_attrs[f"{key}_changed"] = signal(f"{key}_changed")

        # 存储信号和配置数据
        new_attrs['_signals'] = {k: new_attrs[f"{k}_changed"] for k in config_items}
        new_attrs['_data'] = config_items

        # 移除原始配置项，避免类属性干扰
        for key in config_items:
            if key in new_attrs:
                del new_attrs[key]

        return super().__new__(cls, name, bases, new_attrs)

    def __call__(cls, *args, **kwargs):
        """单例控制：确保全局唯一实例"""
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Config(metaclass=ConfigMeta):
    mode_name = "base"
    follow_enabled = True  # 是否开启跟随鼠标
    drag_enabled = True  # 是否开启拖动功能
    follow_update_interval = 3  # 跟随更新间隔（毫秒）
    follow_speed = 5 # 每次的跟随，移动的像素点长度

    def __init__(self):
        # 不再需要复制 _data，因为元类已经处理
        pass

    def __setattr__(self, key, value):
        if key in type(self)._data:
            current_value = type(self)._data[key]
            if current_value != value:
                type(self)._data[key] = value
                type(self)._signals[key].send(self, value=value)
        else:
            super().__setattr__(key, value)

    def __getattr__(self, key):
        if key in type(self)._data:
            return type(self)._data[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


config = Config()


if __name__ == '__main__':



    # 监听信号
    @config.follow_enabled_changed.connect
    def on_follow_changed(sender, value):
        print(f"Follow enabled changed to: {value}") # 结果是False

    config.follow_enabled = False  # 触发信号
    config.follow_enabled = True  # 触发信号
    config.follow_enabled = False  # 触发信号

    print(config.follow_enabled) # 结果是True, False
