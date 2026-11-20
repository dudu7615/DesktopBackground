import os
import sys
from pathlib import Path

from loguru import logger

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

    # 与运行时生成的图片放在同一处用户数据目录下（见 main.py 的 OUT_PATH）
    logDir = (
        Path(os.environ.get("LOCALAPPDATA", Path.home())) / "DesktopBackground" / "logs"
    )
    logDir.mkdir(parents=True, exist_ok=True)
    logger.add(
        logDir / "app.log", level="INFO", rotation="1 MB", retention=3, enqueue=True
    )
