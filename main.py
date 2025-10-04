import sys
import traceback
from PyQt5.QtWidgets import (QApplication)

from FollowAndDragWidget import FollowAndDragWidget
from utils.log_util import logger
from utils.exce_util import handle_exception

if __name__ == "__main__":
    try:
        # 设置全局异常处理
        sys.excepthook = handle_exception
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # 防止关闭窗口时退出程序
        widget = FollowAndDragWidget()
        widget.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"程序启动错误: {traceback.format_exc()}")
        sys.exit(1)
