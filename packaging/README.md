# packaging/

Windows 打包。**只能在 Windows 上执行**（PyInstaller 不支持交叉编译）：

```powershell
uv sync --group build
uv run pyinstaller packaging/main.spec --noconfirm --clean     # → dist/DesktopBackground/
# 想在本机出安装包，再补一步（需自行安装 Inno Setup 6）：
ISCC.exe /DAppVersion=1.1.1 packaging\setup.iss                # → dist/installer/*.exe
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
`%LOCALAPPDATA%\DesktopBackground\runtime\<实例名>\`（开发时仍写 `clock/`，方便看效果）。
按实例分目录是为了安装版与便携版同时运行时不会互相覆盖对方的图。
这样程序目录可以只读——便携版解压进 Program Files 也能跑。

实例名由 exe 所在目录推出（`modules/paths.py` 的 `instanceKey()`），目录里还会写一个
`.instance-key` 标记文件，内容是自己的 exe 路径。卸载器靠它认领数据目录：
只删标记对得上的子目录，便携版的数据不会被牵连。

## 安装器（`setup.iss`）

**这个文件基本不会再动**，改之前请先读完本节。

### 两个名字

| 变量 | 值 | 用在哪 |
|---|---|---|
| `AppName` | `DesktopBackground` | 安装目录、数据目录、产物文件名 |
| `AppDisplayName` | `时钟壁纸` | 所有快捷方式、启动项、安装/卸载向导 |

分开是因为 `AppName` 牵扯升级链：安装目录变了，`UsePreviousAppDir` 就找不到旧版本，
数据目录也会跟着变。改 `AppDisplayName` 是安全的。

### 快捷方式与开机自启

`[Tasks]` 里两个复选框，都默认勾选：

- `desktopicon` → 桌面快捷方式
- `startupicon` → 开机自启，走「启动」文件夹的快捷方式而不是注册表 Run 键
  （用户能直接看到并删掉，卸载时 Inno 也会清理）

开始菜单文件夹、卸载项、桌面、启动项四个快捷方式的显示名都是「时钟壁纸」。

### 安装位置与权限

装到 `%LOCALAPPDATA%\DesktopBackground`，`PrivilegesRequired=lowest`，不弹 UAC。
**刻意不设 `PrivilegesRequiredOverridesAllowed`**：安装目录用户可写，而卸载时会经
powershell 执行 `{app}\killapp.ps1`；一旦允许临时提权卸载，就等于给了任何能写这个
目录的人一个提权执行点。`CurUninstallStepChanged` 里也加了 `if IsAdmin then Exit` 兜底。

### 几条踩过的坑（编译期才会暴露）

改完务必真的编译一遍——`ISCC.exe /DAppVersion=x packaging\setup.iss`。以下三类错误
`[Code]` 段写错时才会出现：

- 注释里**不要写 `[UninstallRun]` 这类段名**：Inno 会把它当成新的段标记，
  报 `Invalid section tag`
- 注释里**不要写 `{app}`**：花括号会提前闭合 Pascal 注释，报 `Syntax error`
- `LoadStringFromFile` 的第二个参数必须是 `AnsiString`，`String` 会报 `Type mismatch`

### 覆盖升级

V1.0.x 的产物叫 `main.exe`，`[InstallDelete]` 里显式删掉它——但那个删除被挪到了
`CurStepChanged(ssPostInstall)`，原因见下。

结束进程走 `packaging/killapp.ps1`（按 exe 完整路径匹配），**不是**
`taskkill /im`——后者按映像名匹配，会把机器上任何同名程序一起强杀。

`[InstallDelete]` 不删 `main.exe`，也不删整个 `_internal`：

- `main.exe` 不在 `[Files]` 里，删掉后没有任何东西会恢复它，所以要等新文件装完再删
- `_internal\clock\config.yml` 是用户可能改过的文件，整目录删会抹掉，改成
  `Excludes` + `onlyifdoesntexist` 保留

其余文件靠 `ignoreversion` 覆盖即可。安装过程中出错时 Inno 会整体回滚
（官方 Installation Order 文档：卸载器落盘之前的步骤都在回滚保护范围内），
所以不需要额外的 staging 目录。

## 几个不能改的东西

- `setup.iss` 里的 **`AppId`**：软件的唯一标识，改了等于换了另一个程序，
  老版本的覆盖安装和卸载都会错乱。
- **exe 名 `DesktopBackground.exe`**：`setup.iss` 的 `[Files]`/`[Icons]` 与
  `killapp.ps1` 的调用都按这个名字写；改名要同步改。
- spec 里 `clock/` 与 `icon.ico` 的 **dest**：见上文。
- `_internal\clock\config.yml` 在 `[Files]` 里被排除后单独 `onlyifdoesntexist`
  安装：用户可能改过它，升级不能覆盖。

## 图标

仓库根的 `icon.ico` 同时用作 exe 图标、托盘图标、安装器图标，已是 256×256
多尺寸 ICO，无需转换。
