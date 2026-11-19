# Linux 调试

`win32con` / `win32gui` 只在 Windows 上可用。`dev/win32_stub/` 里是两个假的同名模块，
**只打印一行 loguru 日志，不做任何实际操作**，用来在 Linux 上调试除壁纸设置以外的全部逻辑。

## 用法

```bash
uv sync                                    # 依赖已按平台标记，Linux 上不会装 pywin32
PYTHONPATH=dev/win32_stub uv run main.py   # 运行
PYTHONPATH=dev/win32_stub uv run python modules/weather.py   # 只测单个模块
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
- 日历/倒计时用的字体是 `clock/config.yml` 里的 `msyh.ttc`，PIL 按文件名查找，
  Linux 上没装微软雅黑会报 `OSError: cannot open resource`，与假包无关。
