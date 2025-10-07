import sys
import traceback
from PyQt5.QtWidgets import (QApplication)

from FollowAndDragWidget import FollowAndDragWidget
from configs import config
from utils.log_util import logger, on_logger_only_error_changed
from utils.exce_util import handle_exception

if __name__ == "__main__":
    on_logger_only_error_changed(None, config.logger_only_error)
    config.logger_only_error_changed.connect(on_logger_only_error_changed)
    try:
        # 设置全局异常处理
        # sys.excepthook = handle_exception
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # 防止关闭窗口时退出程序
        widget = FollowAndDragWidget()
        widget.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"程序启动错误: {traceback.format_exc()}")
        sys.exit(1)
