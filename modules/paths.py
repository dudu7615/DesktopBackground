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
#: 子目录名保留的字符数。Windows 路径本身不会这么长，这里只是兜底。
_KEY_LEN = 80


def _root() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / APP_DIR_NAME
    # 非 Windows（只有 Linux 调试会走到）没有 LOCALAPPDATA
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def instanceKey() -> str:
    """由 exe 所在目录推出实例名，安装版与便携版各得一个。

    规则：转小写，非 ASCII 字母数字的字符一律换成 `_`，取末 80 个字符。
    刻意不用哈希——setup.iss 里要用 Pascal Script 算出同样的值，编码相关的
    哈希在两边很难保证一致（用户名可能是中文等非 ASCII 字符）。
    **改这里的话 packaging/setup.iss 的 InstanceKey 必须同步改。**
    """
    appDir = Path(sys.executable).parent.as_posix().lower()
    key = "".join(c if ("a" <= c <= "z" or "0" <= c <= "9") else "_" for c in appDir)
    return key[-_KEY_LEN:] or "_"


def runtimeDir() -> Path:
    """合成图片的落点。"""
    return _root() / "runtime" / instanceKey()


def logDir() -> Path:
    """日志落点。"""
    return _root() / "logs" / instanceKey()
