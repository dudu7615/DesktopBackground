# DesktopBackground

在电脑桌面显示时间、日期、天气

## 构建

### 快速打包（仅 exe）

```batch
build\build.bat
```

输出目录：`build\dist\main\`

### 构建安装包（exe 安装程序）

```batch
build\build_installer.bat
```

该脚本会自动：
1. 使用 PyInstaller 打包 exe
2. 检测 Inno Setup（如未安装则自动下载）
3. 编译生成安装包 `.exe`

输出目录：`build\dist\DesktopBackground_Setup_*.exe`

## 安装

运行生成的 `DesktopBackground_Setup_*.exe` 安装程序，可选择：
- 安装到 `%LOCALAPPDATA%\DesktopBackground`
- 创建桌面快捷方式
- 添加到开机启动
