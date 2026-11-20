"""用户数据目录。

运行时产物（合成图、日志）不能写进程序目录：安装目录可能只读，便携版还可能
被解压进 Program Files。统一写到 %LOCALAPPDATA%\\DesktopBackground 下。

安装版与便携版可能同时开着，所以按 exe 所在目录再分一层子目录，互不覆盖。
子目录名由安装路径推出（规则见 instanceKey），卸载程序用同一规则定位并只清理
自己那一份。
"""

import os
import sys
from pathlib import Path

APP_DIR_NAME = "DesktopBackground"


def _root() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / APP_DIR_NAME
    # 非 Windows（只有 Linux 调试会走到）没有 LOCALAPPDATA
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def instanceKey() -> str:
    """由 exe 所在目录推出实例名，安装版与便携版各得一个。

    组成：8 位十六进制的 djb2 校验和 + `_` + 可读路径片段（转小写、非 ASCII
    字母数字换成 `_`、取末 72 个字符）。校验和负责区分只看片段会撞车的路径，
    片段负责让人一眼看出是哪个安装。

    刻意不用 SHA-1：setup.iss 里要用 Pascal Script 算出同样的值，
    GetSHA1OfString 的编码行为无法保证与 Python 一致（用户名可能是中文）。
    这里只用字符码点做整数运算，两边逐字符完全等价。
    **改这里的话 packaging/setup.iss 的 InstanceKey 必须同步改。**
    """
    appDir = Path(sys.executable).parent.as_posix().lower()

    # djb2：h = h * 33 + ord(c)，按 32 位无符号回绕
    h = 5381
    for ch in appDir:
        h = (h * 33 + ord(ch)) & 0xFFFFFFFF

    readable = "".join(
        c if ("a" <= c <= "z" or "0" <= c <= "9") else "_" for c in appDir
    )[-72:]
    return f"{h:08x}_{readable}"


def runtimeDir() -> Path:
    """合成图片的落点。"""
    return _root() / "runtime" / instanceKey()


def logDir() -> Path:
    """日志落点。"""
    return _root() / "logs" / instanceKey()
