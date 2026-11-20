# Linux 调试

`win32con` / `win32gui` 只在 Windows 上可用。`dev/win32_stub/` 里是两个假的同名模块，
**只打印一行 loguru 日志，不做任何实际操作**，用来在 Linux 上调试除壁纸设置以外的全部逻辑。

## 用法

```bash
uv sync                                    # 依赖已按平台标记，Linux 上不会装 pywin32
PYTHONPATH=dev/win32_stub uv run main.py   # 运行
# 只测单个模块：用 -m 按模块跑，直接 `python modules/weather.py` 会因
# 相对导入 .log 报 ImportError
PYTHONPATH=dev/win32_stub:. uv run python -m modules.weather
```

VS Code 里直接选 `main (linux win32 stub)` 这个调试配置，`launch.json` 已经把
`dev/win32_stub` 加进 `PYTHONPATH` 了。

## 输出示例

```
2026-11-09 23:23:08.529 | DEBUG | modules.setBg:setBackGroundImg:9 - 开始设置壁纸
2026-11-09 23:23:08.529 | INFO  | win32gui:SystemParametersInfo:13 - win32gui.SystemParametersInfo(SPI_SETDESKWALLPAPER, '.../clock/result.png', SPIF_SENDWININICHANGE) -> True
```

## 注意

- 假包里的 `SystemParametersInfo` 是**空操作**，壁纸不会真的变。要验证真实效果得用 Windows。
- 字体是 `clock/config.yml` 里配的 `MapleMono-NF-CN-Regular.ttf`，文件就在 `clock/` 里，
  `makeImg._fontFile()` 会优先用这个自带文件，所以 Linux 上不用装系统字体也能跑。
  只有把 `font.name` 换成系统字体名（比如 `msyh.ttc`）且本机没装时才会报
  `OSError: cannot open resource`，与假包无关。
- 开发时合成结果仍写在 `clock/`（打包后改写到 `%LOCALAPPDATA%\DesktopBackground\runtime`），
  所以 Linux 上跑完会在 `clock/` 里留下 `result.png`、`weather.png`、`exam.png` 等未跟踪文件。
