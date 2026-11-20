# DesktopBackground

在电脑桌面显示时间、日期、天气。

## 开发

```bash
uv sync                      # 装依赖（Windows）
uv run main.py               # 直接跑
```

Linux 上调试见 `dev/README.md`（用 `dev/win32_stub` 顶替 pywin32）。

## 打包

Windows 专用，PyInstaller 不支持交叉编译。详细说明见 [`packaging/README.md`](packaging/README.md)。

```powershell
uv sync --group build
uv run pyinstaller packaging/main.spec --noconfirm --clean   # → dist/DesktopBackground/
ISCC.exe /DAppVersion=1.1.0 packaging\setup.iss              # → dist\installer\
```

## 发布

**合并进 `main` 后 GitHub Actions 会自动打包**，产物在 Actions 的 Artifacts 里；
该版本还没有 Release（或上次发布没传上产物）时，顺带建一个 Release。
手动触发跑别的分支只打包、不发布。

发版本的流程：在 PR 里改 `pyproject.toml` 的 `version` → 合并进 `main`。

产物：

- `DesktopBackground-Setup-<版本>.exe` —— 安装包
- `DesktopBackground-portable-<版本>.zip` —— 免安装版，解压双击 `DesktopBackground.exe`

安装包会装到 `%LOCALAPPDATA%\DesktopBackground`，可选创建桌面快捷方式、开机启动。
运行时生成的壁纸图写在同一处的 `runtime\` 目录，程序目录保持只读也能跑。
