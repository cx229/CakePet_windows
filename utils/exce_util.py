import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox

from utils.log_util import logger


def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理函数"""
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"未捕获的异常:\n{error_msg}")

    # 在GUI中显示错误信息
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("程序错误")
    msg_box.setText("程序发生错误，请查看日志")
    msg_box.setDetailedText(error_msg)
    msg_box.exec_()

    # 正常退出程序
    QApplication.quit()