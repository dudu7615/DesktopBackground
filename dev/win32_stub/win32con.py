"""pywin32 `win32con` 的假实现（仅用于 Linux 调试，不会真的调用 Windows API）。

用法：把本目录放进 PYTHONPATH，见 dev/README.md
"""

SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02
SPI_GETDESKWALLPAPER = 0x0073

CONSTANTS = {
    name: value
    for name, value in globals().items()
    if name.isupper() and isinstance(value, int)
}


def name_of(value):
    """把常量值换回名字，让日志更好读。"""
    for name, const in CONSTANTS.items():
        if const == value:
            return name
    return value
