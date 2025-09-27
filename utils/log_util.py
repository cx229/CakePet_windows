import datetime
import logging
import os
import sys




def setup_logging():
    """设置日志系统"""
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # 生成日志文件名（带时间戳）
    log_filename = f"logs/mouse_follower_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
