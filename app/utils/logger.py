"""结构化日志配置"""

import logging
import sys
from app.config import settings


def setup_logger(name: str = "shareconn") -> logging.Logger:
    """创建并配置结构化日志记录器"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(level)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 格式化器
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 全局 logger 实例
logger = setup_logger()
