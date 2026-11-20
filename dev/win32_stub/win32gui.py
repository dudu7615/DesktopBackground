"""pywin32 `win32gui` 的假实现（仅用于 Linux 调试）。

每个函数只打印一行 loguru 日志，不执行任何真实操作。
"""

from loguru import logger

import win32con


def SystemParametersInfo(action, param=None, flags=0):
    """假实现：只记录一行日志。"""
    logger.info(
        "win32gui.SystemParametersInfo({}, {!r}, {}) -> True",
        win32con.name_of(action),
        param,
        win32con.name_of(flags),
    )
    return True
