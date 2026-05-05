import random
from dataclasses import dataclass, replace
from enum import Enum
from itertools import chain

from pynput import keyboard


@dataclass(frozen=True)
class TrayMsgMeta:
    """托盘消息元数据"""
    key: str
    text: str
    base_ms: int = 2000  # 基础持续时间（毫秒）,为0时表示持续显示
    random_ms: int = 1000  # 随机增量持续时间（毫秒）
    priority: int = 3  # 优先级(0-10)，值越大越优先显示

    @property
    def duration(self) -> int:
        """获取持续时间（毫秒）"""
        if self.base_ms <= 0:
            return 0
        if self.random_ms <= 0:
            return self.base_ms
        return self.base_ms + random.randint(0, self.random_ms)


class TragMsgs:
    """托盘消息"""

    class Default(Enum):
        DEFAULT = TrayMsgMeta(key="default", text="", base_ms=2000, random_ms=28000)
        KEY_SPEED = TrayMsgMeta(key="keyboard_speed", text="", base_ms=5000, random_ms=25000)

    class Meow(Enum):
        MIAO1 = TrayMsgMeta(key="meow_miao1", text="喵？！？", random_ms=2000)
        MIAO2 = TrayMsgMeta(key="meow_miao2", text="喵！", random_ms=2000)
        OHU1 = TrayMsgMeta(key="meow_ohu1", text="哦呜~ 哦呜~", random_ms=2000)
        OHU2 = TrayMsgMeta(key="meow_ohu2", text="哦呜~", random_ms=2000)
        PURR = TrayMsgMeta(key="meow_purr", text="咕噜咕咕噜...", random_ms=2000)
        WANG = TrayMsgMeta(key="meow_wang", text="汪 汪汪 汪汪汪", base_ms=500, random_ms=500)

    # 思考类消息
    class Thinking(Enum):
        PHILOSOPHY1 = TrayMsgMeta(key="think_philosophy1", text="你盯着屏幕，而我盯着你，谁又在盯着我们呢？", base_ms=500, random_ms=500)
        PHILOSOPHY2 = TrayMsgMeta(key="think_philosophy2", text="存在大于本质，但小鱼干先大于一切", base_ms=500, random_ms=500)
        PHILOSOPHY3 = TrayMsgMeta(key="think_philosophy3", text="我是谁？我从哪里来？要到哪里去？", base_ms=500, random_ms=500)
        PHILOSOPHY4 = TrayMsgMeta(key="think_philosophy4", text="喵生三大事：吃饭，睡觉", random_ms=2000)
        PHILOSOPHY5 = TrayMsgMeta(key="think_philosophy5", text="如果桌面是无限的，它的尽头在哪里？", base_ms=500, random_ms=500)
        PHILOSOPHY6 = TrayMsgMeta(key="think_philosophy6", text="今天想通了一个道理，有些道理是想不通的", base_ms=500, random_ms=500)
        PHILOSOPHY7 = TrayMsgMeta(key="think_philosophy7", text="今天想通了一个道理，有些道理是想不通的", base_ms=500, random_ms=500)

    class CollectionWord(Enum):
        COLLECTION_WORD1 = TrayMsgMeta(key="collection_word1", text="小〇〇〇〇", base_ms=2000, random_ms=2000)
        COLLECTION_WORD2 = TrayMsgMeta(key="collection_word2", text="〇小〇〇〇", base_ms=1000, random_ms=1000)
        COLLECTION_WORD3 = TrayMsgMeta(key="collection_word3", text="〇〇芝〇〇", base_ms=500, random_ms=500)
        COLLECTION_WORD4 = TrayMsgMeta(key="collection_word4", text="〇〇〇麻〇", base_ms=250, random_ms=250)
        COLLECTION_WORD5 = TrayMsgMeta(key="collection_word5", text="〇〇〇〇酥", base_ms=100, random_ms=100)

    class Event(Enum):
        REST = TrayMsgMeta(key="event_rest", text="休息时间到...", base_ms=0, priority=8)  # 优先级较高
        HIDE = TrayMsgMeta(key="event_hide", text="溜了溜了...", base_ms=0, priority=8)  # 优先级较高
        SHOW = TrayMsgMeta(key="event_show", text="芝麻酥 闪亮登场...", base_ms=0, priority=8)  # 优先级较高

    class Interact(Enum):
        DRAGGING = TrayMsgMeta(key="event_dragging", text="", base_ms=0)  # 持续显示
        THROWING = TrayMsgMeta(key="event_throwing", text="", base_ms=0)  # 持续显示
        THROW_HIGHEST = TrayMsgMeta(key="interact_throw_highest", text="", base_ms=5000)
        THROW_DISTANCE = TrayMsgMeta(key="interact_throw_distance", text="", base_ms=5000)


# 待机托盘消息类，包含喵类、思考类消息
tray_msgs_cls_standby = [*TragMsgs.Meow, *TragMsgs.Thinking,*TragMsgs.CollectionWord]


def get_standby_tray_msg() -> TrayMsgMeta:
    return random.choice(tray_msgs_cls_standby).value


def get_dragging_tray_msg() -> TrayMsgMeta:
    texts = ["喵？...", "喵？喵？喵？", "喵？！？"]
    return replace(TragMsgs.Interact.DRAGGING.value, text=random.choice(texts))


def get_throwing_tray_msg() -> TrayMsgMeta:
    texts = ["喵！", "喵！！！！！！", "呜呼 起飞！"]
    return replace(TragMsgs.Interact.THROWING.value, text=random.choice(texts))


def get_key_speed_tray_msg(speed: int, sum_keys: int = 0) -> TrayMsgMeta:
    if sum_keys == 0:
        return replace(TragMsgs.Default.KEY_SPEED.value, text=f"打字: {speed:2d}/分钟")
    return replace(TragMsgs.Default.KEY_SPEED.value, text=f"打字: {speed:2d}/分钟,  今日: {sum_keys:2d} 字符")


def get_throw_highest_tray_msg(height: int) -> TrayMsgMeta:
    texts = ["抛高高: {height:,} 像素", "抛高: {height:,} 像素", "抛: {height:,} 像素"]
    return replace(TragMsgs.Interact.THROW_HIGHEST.value, text=random.choice(texts).format(height=height))


def get_throw_distance_tray_msg(distance: int) -> TrayMsgMeta:
    texts = ["弹弹弹: {distance:,} 像素", "滚滚滚: {distance:,} 像素", "咕噜咕噜: {distance:,} 像素"]
    return replace(TragMsgs.Interact.THROW_DISTANCE.value, text=random.choice(texts).format(distance=distance))
