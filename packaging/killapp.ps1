# 结束占用本软件 exe 的进程（安装/卸载前调用，参数是 exe 的完整路径）。
#
# 只按可执行文件的完整路径匹配：任务管理器里同名但装在别处的程序
# （比如别人自己编译的 main.exe）不该被安装器强杀。
param([Parameter(Mandatory = $true)][string]$ExePath)

$ErrorActionPreference = 'SilentlyContinue'
Get-CimInstance Win32_Process |
    Where-Object { $_.ExecutablePath -eq $ExePath } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
