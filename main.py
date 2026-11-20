import sys
from pathlib import Path

import anyio
import yaml
from datetime import datetime
from threading import Thread
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from modules import makeImg, setBg, weather, logger, Config
from modules.log import setupLogging
from modules.paths import instanceKey, runtimeDir

ROOT = Path(__file__).parent
IMGS_PATH = ROOT / "clock"


def _outputPath() -> Path:
    """运行时生成的图片写这里。

    素材（config.yml、数字图、字体）是只读的，跟程序放一起；合成结果不能写回
    _internal/，否则安装目录不可写（比如把便携版解压进 Program Files）时合成
    直接失败。打包后用用户数据目录（安装版与便携版各一个子目录，见
    modules/paths.py）；开发时仍写 clock/，方便直接看效果。
    """
    if not getattr(sys, "frozen", False):
        return IMGS_PATH
    return runtimeDir()


OUT_PATH = _outputPath()

# 先接上文件日志再读配置：配置校验失败会让 windowed exe 直接退出，没有日志
# 就什么线索都留不下。
# 注意先于一切建目录/读配置：打包后 runtimeDir() 会顺带写好归属标记，
# 卸载器靠它认领数据目录。
setupLogging()

try:
    _config = yaml.load(
        (IMGS_PATH / "config.yml").read_text(encoding="utf-8"), Loader=yaml.FullLoader
    )
    config = Config.model_validate(_config)
except Exception:
    logger.exception("读取配置失败：clock/config.yml 格式不对")
    raise


@logger.catch
async def img():
    logger.info("开始运行图片模块运行")
    i = True  # 是否是第一次
    nowTime = datetime.now()
    # logger.debug(f"{self.config}")
    while True:
        logger.debug(f"{datetime.now().minute} {nowTime.minute}")
        if datetime.now().minute != nowTime.minute or i:
            nowTime = datetime.now()
            makeImg.BgImg(
                IMGS_PATH,
                OUT_PATH,
                config.size,
                "bg.jpg",
                "weather.png",
                f"month{nowTime.month}.png",
                f"day{nowTime.day}.png",
                f"hour{nowTime.hour}.png",
                f"minute{nowTime.minute}.png",
                f"weekday{nowTime.weekday()+1}.png",
            )
            setBg.setBackGroundImg(OUT_PATH / "result.png")

        if i:
            i = False
        await anyio.sleep(10)


@logger.catch
async def exam():
    logger.info("开始运行考试模块")
    examDate = datetime(2027, 6, 7)
    while True:
        makeImg.examDaysImg(
            IMGS_PATH,
            OUT_PATH,
            config.size,
            config.place["exam"],
            str((examDate - datetime.now()).days),
            config.font,
            config.color,
        )
        await anyio.sleep(60)


@logger.catch
async def weater():
    logger.info("开始运行天气模块")
    while True:
        logger.debug(f"{datetime.now().minute}")
        makeImg.weatherImg(
            IMGS_PATH,
            OUT_PATH,
            config.size,
            config.place["weather"],
            weather.getweather(),
            config.font,
            config.color,
        )
        await anyio.sleep(60)


class TrayIcon(QSystemTrayIcon):

    def __init__(self):
        super().__init__()
        self.setIcon(QIcon(str(ROOT / "icon.ico")))
        self.initUI()

    def initUI(self):
        self.menu = QMenu()
        # self.menu.addAction("显示主窗口")
        self.menu.addAction("退出")
        self.setContextMenu(self.menu)
        self.menu.triggered.connect(self.clickEvent)

    def clickEvent(self, action: QAction):
        """点击托盘菜单时触发"""
        app.quit()


def _claimSingleInstance() -> QLocalServer | None:
    """同一安装只允许跑一份；已经有实例在跑时返回 None。

    开机自启 + 手动双击是最常见的重复启动场景，两个进程会抢同一个运行目录
    里的图、把同一个日志文件切来切去。

    用本地套接字而不是共享内存：后者在进程被强杀（任务管理器结束任务、崩溃）
    后标记仍留在系统里，下次启动会误判"已在运行"而永远起不来。套接字随进程
    消失，残留的也只是个连不上的文件，这里会顺手清掉。

    便携版是另一个安装目录、另一个套接字名，不受影响。
    """
    name = f"DesktopBackground-{instanceKey()}"
    probe = QLocalSocket()
    probe.connectToServer(name)
    if probe.waitForConnected(300):
        # 真有一个活着的实例在监听
        probe.disconnectFromServer()
        return None
    probe.abort()

    # 连不上：要么没人跑，要么上次是被强杀留下的残骸。removeServer 只删除
    # 套接字文件，安全。
    QLocalServer.removeServer(name)
    server = QLocalServer()
    if not server.listen(name):
        logger.warning(f"无法创建单实例监听：{server.errorString()}")
        return server  # 监听失败也不该阻止程序启动
    return server


async def main():
    async with anyio.create_task_group() as taskGroup:
        taskGroup.start_soon(weater)
        taskGroup.start_soon(exam)
        taskGroup.start_soon(img)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 同一个安装只允许跑一份（见 _claimSingleInstance）
    _instance = _claimSingleInstance()
    if _instance is None:
        logger.info("已有实例在运行，本次启动退出")
        sys.exit(0)

    logger.info("程序启动")
    Thread(target=anyio.run, args=(main,), daemon=True).start()
    app.setQuitOnLastWindowClosed(False)
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec())
