"""统一日志工具 — 控制台彩色 + 文件轮转"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from src.config.loader import LoggingConfig


def setup_logger(config: LoggingConfig) -> logging.Logger:
    """
    初始化全局 logger

    功能：
    1. 控制台输出：彩色格式 [TIME] [LEVEL] message
    2. 文件输出：logs/companion.log，100MB 轮转，保留5份
    3. 级别：从配置读取

    返回：配置好的 root logger
    """
    logger = logging.getLogger("blockmind")
    logger.setLevel(getattr(logging, config.level.upper(), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(console)

    # 文件 handler（轮转）
    log_dir = Path(config.file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        config.file,
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=config.backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s"
    ))
    logger.addHandler(file_handler)

    return logger
