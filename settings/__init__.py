import traceback

from PyQt5.QtWidgets import QWidget, QSystemTrayIcon

from settings.Menu import Menu
from settings.TrayIcon import TrayIcon
from utils.log_util import logger

def create_tray(parent:QWidget):
    try:

        tray = TrayIcon(parent)
        # 创建托盘菜单

        menu=create_context_menu(parent, tray)

        tray.show()
        logger.info("系统托盘图标创建成功")
        return tray, menu
    except Exception as e:
        logger.error(f"创建托盘图标错误: {traceback.format_exc()}")
        raise



def create_context_menu(parent:QWidget, tray:QSystemTrayIcon):
    """创建右键菜单(用于托盘和窗口右键)"""
    try:
        menu = Menu(parent)
        # 同时设置给托盘和窗口
        tray.setContextMenu(menu) # 设置托盘菜单
        logger.info("右键菜单创建成功")
        return menu
    except Exception as e:
        logger.error(f"创建右键菜单错误: {traceback.format_exc()}")
        raise