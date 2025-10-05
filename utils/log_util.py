# import datetime
# import logging
# import os
# import sys
#
#
#
#
# def setup_logging():
#     """设置日志系统"""
#     # 创建logs目录
#     if not os.path.exists('logs'):
#         os.makedirs('logs')
#
#     # 生成日志文件名（带时间戳）
#     log_filename = f"logs/mouse_follower_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
#
#     # 配置日志
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(filename)-30s:%(lineno)-4d - %(message)s',
#         handlers=[
#             logging.FileHandler(log_filename, encoding='utf-8'),
#             logging.StreamHandler(sys.stdout)
#         ]
#     )
#     return logging.getLogger(__name__)
#
# logger = setup_logging()
import os
import sys
import logging
import datetime


def setup_logging():
    """设置日志系统，确保filename:lineno对齐"""
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # 生成日志文件名（带时间戳）
    log_filename = f"logs/mouse_follower_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # 自定义Formatter确保对齐
    class AlignedFormatter(logging.Formatter):
        def format(self, record):
            # 计算filename:lineno的组合长度（固定30字符）
            filename_lineno = f"{record.filename}:{record.lineno}"
            record.aligned_location = filename_lineno.ljust(35)  # 35是可调整的固定宽度
            return super().format(record)

    # 创建formatter
    formatter = AlignedFormatter(
        fmt='%(asctime)s - %(levelname)s - %(aligned_location)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 配置handler
    handlers = [
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]

    # 应用配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    return logging.getLogger(__name__)


logger = setup_logging()