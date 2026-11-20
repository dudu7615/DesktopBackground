# packaging/

Windows 打包。**只能在 Windows 上执行**（PyInstaller 不支持交叉编译）：

```powershell
uv sync --group build
uv run pyinstaller packaging/main.spec --noconfirm --clean     # → dist/DesktopBackground/
# 想在本机出安装包，再补一步（需自行安装 Inno Setup 6）：
ISCC.exe /DAppVersion=1.1.0 packaging\setup.iss                # → dist/installer/*.exe
```

只看效果、不需要安装包时，跑完第一条就能双击 `dist/DesktopBackground/DesktopBackground.exe`。

`.github/workflows/release.yml` 走的就是这两步：合并进 `main` 后自动跑，
产物传到 Actions Artifacts；该版本还没有 Release（或上次发到一半失败）时
顺带建一个 Release。手动触发跑别的分支只打包、不发布。
所以发版本的流程是：**在 PR 里改 `version` → 合并**。

## 产物

| 文件 | 说明 |
|---|---|
| `dist/installer/DesktopBackground-Setup-<版本>.exe` | 安装包 |
| `dist/DesktopBackground-portable-<版本>.zip` | 免安装版，解压双击 `DesktopBackground.exe` |

## 目录结构（打包后）

```
dist/DesktopBackground/
    DesktopBackground.exe
    _internal/
        clock/         # 素材：config.yml、背景图、数字图（只读，运行时只读不写）
        icon.ico       # 托盘图标
        base_library.zip / *.pyd ...
```

`main.py` 与 `modules/` 是纯 Python，会被打进 PYZ 归档、不落成目录，但
PyInstaller 把 `__file__` 统一解析到 `_internal/` 下，所以 `main.py` 里的
`ROOT = Path(__file__).parent` 拿到的就是 `_internal/`，`clock/` 与 `icon.ico`
的 dest 必须写 `"clock"` 和 `"."`。对不上就找不到素材。

**运行时生成的图片不写回安装目录**：`result.png`、`weather.png` 等写到
`%LOCALAPPDATA%\DesktopBackground\runtime\<安装路径哈希>\`（开发时仍写 `clock/`，方便看效果）。
按安装路径分目录，是为了安装版与便携版同时运行时不会互相覆盖对方的图。卸载时会一并删除。
这样程序目录可以只读——便携版解压进 Program Files 也能跑。

## 图标

仓库根的 `icon.ico` 同时用作 exe 图标、托盘图标、安装器图标，已是 256×256
多尺寸 ICO，无需转换。

## 几个不能改的东西

- `setup.iss` 里的 **`AppId`**：软件的唯一标识，改了等于换了另一个程序，
  老版本的覆盖安装和卸载都会错乱。
- **exe 名 `DesktopBackground.exe`**：`setup.iss` 的 `[Files]`/`[Icons]` 与
  `killapp.ps1` 的调用都按这个名字写；改名要同步改。
- spec 里 `clock/` 与 `icon.ico` 的 **dest**：见上文。
- `_internal\clock\config.yml` 在 `[Files]` 里被排除后单独 `onlyifdoesntexist`
  安装：用户可能改过它，升级不能覆盖。

## 覆盖升级

V1.0.x 的产物叫 `main.exe`，`setup.iss` 在 `[InstallDelete]` 里显式删掉它，
`[Code]` 里的 `KillRunningApp` 也会先结束它，所以从旧版本升级不会留下
两个 exe 或"文件被占用"装不上。

结束进程走 `packaging/killapp.ps1`（按 exe 完整路径匹配），**不是**
`taskkill /im`——后者按映像名匹配，会把机器上任何同名程序一起强杀。
`[InstallDelete]` 也不删整个 `_internal`：那会连带删掉用户改过的
`config.yml`，且安装中途失败时旧程序会残缺。旧文件靠 `ignoreversion` 覆盖。
