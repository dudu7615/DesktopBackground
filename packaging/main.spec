# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置（Windows，onedir）。

**只能在 Windows 上跑**，PyInstaller 不支持交叉编译：

    uv sync --group build
    uv run pyinstaller packaging/main.spec --noconfirm --clean

产物是 dist/DesktopBackground/，整个目录才是可运行单元，再交给
packaging/setup.iss 封成安装包。

为什么是 onedir 而不是 onefile：onefile 每次启动都要把全部内容解包到临时目录，
而这个程序是开机自启的常驻托盘程序，每次登录都解包一遍不能接受。

打包后的目录结构（PyInstaller 6 起非 exe 文件都在 _internal/ 下）::

    dist/DesktopBackground/
        DesktopBackground.exe
        _internal/
            clock/         <- 素材（字体配置、背景图、数字图），真实目录
            icon.ico       <- 托盘图标，main.py 按 __file__ 同级查找
            base_library.zip / *.pyd

main.py 与 modules/ 是纯 Python，会被打进 PYZ 归档、不落成目录；但 PyInstaller
把 ``__file__`` 统一解析到 _internal/ 下，所以 main.py 里
``ROOT = Path(__file__).parent`` 拿到的就是 _internal/。因此 clock/ 与 icon.ico
的 dest 必须写 "clock" 和 "."。运行时程序会往 clock/ 里写 result.png、
exam.png、weather.png，因此安装位置必须在用户可写目录（见 setup.iss 的
DefaultDirName=%LOCALAPPDATA%）。

本文件扩展名是 .spec，不在 ruff 的检查范围内；SPECPATH 由 PyInstaller 注入。
"""

import sys
from pathlib import Path

#: spec 在 packaging/ 下，仓库根是它的上一层。
ROOT = Path(SPECPATH).parent  # noqa: F821  # SPECPATH 由 PyInstaller 注入


def find_dlls() -> Path | None:
    """定位解释器的 DLLs 目录。

    venv 里没有 _ssl.pyd 和 OpenSSL 的 DLL，它们跟着基础解释器走，所以优先
    从 base_prefix 找；拿不到再退回 exe 所在目录和 sys.path 里的 DLLs 项。
    这不是洁癖：路径猜错时下面那段 binaries 会静默变成空列表，打包照样成功，
    问题要等到用户机器上访问 HTTPS 时才炸。
    """
    candidates = [
        Path(sys.base_prefix) / "DLLs",
        Path(sys.executable).parent / "DLLs",
        *(Path(p) for p in sys.path if p.replace("\\", "/").endswith("/DLLs")),
    ]
    return next((p for p in candidates if p.is_dir()), None)


# 显式带上 _ssl 与 OpenSSL。requests 访问天气接口必须走 HTTPS，缺了这些文件
# PyInstaller 不会报错，只在用户机器上抛 ImportError——最难查的一类故障。
# Python 3.14 (OpenSSL 3) 的文件名是 libcrypto-3-x64.dll / libssl-3-x64.dll。
binaries = []
_dlls = find_dlls()
if _dlls:
    binaries = [
        (str(path), ".")
        for pattern in ("_ssl.pyd", "libcrypto*.dll", "libssl*.dll")
        for path in sorted(_dlls.glob(pattern))
    ]

# 打包机器是 Windows 却一个都没找到 —— 说明路径推断或文件命名变了。宁可在这里
# 吵一句，也不要等用户机器上访问天气接口时才炸。
if sys.platform == "win32" and not binaries:
    print(
        "[packaging/main.spec] 警告：没有找到 _ssl.pyd / libcrypto*.dll / libssl*.dll，"
        f"已尝试的 DLLs 目录：{_dlls}。打包出的程序可能无法访问 HTTPS。"
    )

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=[
        # clock/ 是素材目录：config.yml、背景图、年月日时分与星期的数字图。
        (str(ROOT / "clock"), "clock"),
        # 托盘图标。不能被 ignore 掉，main.py 直接读它。
        (str(ROOT / "icon.ico"), "."),
    ],
    # main.py 用 `from modules import *`，`modules/__init__.py` 又互相导入，
    # 但都是模块级 import，静态分析追得到（Linux 冒烟构建已验证 modules 全被打进
    # PYZ）。PySide6 的平台插件与 lxml 的 C 扩展由 PyInstaller 自带的 hook 处理，
    # 这里不需要额外补。
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DesktopBackground",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX 压过的 Qt DLL 在部分机器上会加载失败，收益也不大，关掉
    upx=False,
    # 这是托盘程序，不该弹控制台窗口；开机自启时更不能多一个黑框。
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "icon.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="DesktopBackground",
)
