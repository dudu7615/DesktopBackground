"""用户数据目录。

运行时产物（合成图、日志）不能写进程序目录：安装目录可能只读，便携版还可能
被解压进 Program Files。统一写到 %LOCALAPPDATA%\\DesktopBackground 下。

安装版与便携版可能同时开着，所以各自用一个以 exe 路径命名的子目录。
目录归属靠一个**标记文件**（.instance-key）识别：程序第一次写入时写下自己的
exe 路径，卸载器只删除标记内容对得上本安装目录的那些目录。

刻意不让 setup.iss 重算哈希来定位目录：那要求 Pascal Script 与 Python 的
字符串/编码处理逐字节一致，做不到（用户名可能是中文，比对与哈希都容易分叉）。
标记文件没有这个问题——它由程序自己写，卸载器只做前缀比较。
"""

import os
import sys
from pathlib import Path

APP_DIR_NAME = "DesktopBackground"
#: 标记文件，内容是本实例的 exe 所在目录（正斜杠、小写）
MARKER = ".instance-key"


def _root() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / APP_DIR_NAME
    # 非 Windows（只有 Linux 调试会走到）没有 LOCALAPPDATA
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def _appDir() -> str:
    """exe 所在目录，正斜杠 + ASCII 小写，作为实例标识的规范形式。

    setup.iss 的 InstanceKey 只做 `\\`→`/` 与 ASCII 小写，与此一致。
    """
    raw = Path(sys.executable).parent.as_posix()
    return "".join(ch.lower() if "A" <= ch <= "Z" else ch for ch in raw)


def instanceKey() -> str:
    """实例名（子目录名）：可读路径片段 + 4 位校验和。

    只用于让人一眼看出是哪个安装；真正的归属判断看 MARKER 文件。
    """
    appDir = _appDir()
    # djb2，仅用于给可读片段加一个短后缀，避免长路径截断后目录名撞在一起
    h = 5381
    for ch in appDir:
        h = (h * 33 + ord(ch)) & 0xFFFFFFFF
    readable = "".join(
        c if ("a" <= c <= "z" or "0" <= c <= "9") else "_" for c in appDir
    )[-40:]
    return f"{readable}-{h & 0xFFFF:04x}"


def _ensure(directory: Path) -> Path:
    """建目录并写入归属标记（已有内容匹配的标记就不动）。"""
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / MARKER
    tag = _appDir()
    try:
        if marker.exists() and marker.read_text(encoding="utf-8").strip() == tag:
            return directory
        marker.write_text(tag, encoding="utf-8")
    except OSError:
        # 标记写不进去不影响使用，只是卸载时可能清不掉这个目录
        pass
    return directory


def runtimeDir() -> Path:
    """合成图片的落点。"""
    return _ensure(_root() / "runtime" / instanceKey())


def logDir() -> Path:
    """日志落点。"""
    return _ensure(_root() / "logs" / instanceKey())
