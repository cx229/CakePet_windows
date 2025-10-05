import random
from dataclasses import dataclass, replace
from enum import Enum
from itertools import chain


@dataclass(frozen=True)
class TrayMsgMeta:
    """托盘消息元数据"""
    key: str = ""
    text: str = ""
    base_ms: int = 5000  # 基础持续时间（毫秒）,为0时表示持续显示
    random_ms: int = 0  # 随机增量持续时间（毫秒）
    priority: int = 5  # 优先级(0-10)，值越大越优先显示

    @property
    def duration(self) -> int:
        """获取持续时间（毫秒）"""
        if self.random_ms <= 0:
            return self.base_ms
        return self.base_ms + random.randint(0, self.random_ms)


class TragMsgs:
    """托盘消息"""

    class Default(Enum):
        DEFAULT = TrayMsgMeta(key="default", text="", base_ms=2000, random_ms=10000)

    class Meow(Enum):
        MIAO1 = TrayMsgMeta(key="meow_miao1", text="喵？！？", random_ms=2000)
        MIAO2 = TrayMsgMeta(key="meow_miao2", text="喵！", random_ms=2000)
        OHU1 = TrayMsgMeta(key="meow_ohu1", text="哦呜~ 哦呜~", random_ms=2000)
        OHU2 = TrayMsgMeta(key="meow_ohu2", text="哦呜~", random_ms=2000)
        PURR = TrayMsgMeta(key="meow_purr", text="咕噜咕咕噜...", random_ms=2000)
        WANG = TrayMsgMeta(key="meow_wang", text="汪 汪汪 汪汪汪", base_ms=1000, random_ms=2000)

    # 思考类消息
    class Thinking(Enum):
        PHILOSOPHY1 = TrayMsgMeta(key="think_philosophy1", text="你盯着屏幕，而我盯着你，谁又在盯着我们呢？", base_ms=100, random_ms=2000)
        PHILOSOPHY2 = TrayMsgMeta(key="think_philosophy2", text="存在大于本质，但小鱼干先大于一切", base_ms=100, random_ms=2000)
        PHILOSOPHY3 = TrayMsgMeta(key="think_philosophy3", text="我是谁？我从哪里来？要到哪里去？", base_ms=100, random_ms=2000)
        PHILOSOPHY4 = TrayMsgMeta(key="think_philosophy4", text="喵生三大事：吃饭，睡觉", random_ms=2000)
        PHILOSOPHY5 = TrayMsgMeta(key="think_philosophy5", text="如果桌面是无限的，它的尽头在哪里？", base_ms=500, random_ms=2000)

    class Event(Enum):
        REST = TrayMsgMeta(key="event_rest", text="休息时间到...", base_ms=0, priority=8)


tray_msgs_cls_standard = [*TragMsgs.Meow, *TragMsgs.Thinking]
