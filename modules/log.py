import sys

from loguru import logger

from .paths import logDir

__all__ = ["logger", "setupLogging"]


def setupLogging() -> None:
    """打包成无控制台的 exe 后没有 stderr，诊断信息改落到文件。"""
    if not getattr(sys, "frozen", False):
        # 开发时直接看终端输出就够了
        return

    # console=False 的 windowed exe 里 sys.stderr 是 None，默认 sink 写不进去，
    # 留着只会静默丢弃日志，不如摘掉
    if sys.stderr is None:
        logger.remove()

    # 每个安装位置一个日志文件：安装版与便携版可能同时开着，共用一个文件时
    # loguru 的 rotation 属于不同进程、互不知情，会把对方的记录切走或写乱。
    # 注意这是给诊断看的，不是多进程安全的审计日志。
    directory = logDir()
    directory.mkdir(parents=True, exist_ok=True)
    logger.add(
        directory / "app.log", level="INFO", rotation="1 MB", retention=3, enqueue=True
    )
