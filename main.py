import os
import sys
from pathlib import Path

import anyio
import yaml
from datetime import datetime
from threading import Thread
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from modules import makeImg, setBg, weather, logger, Config
from modules.log import setupLogging

ROOT = Path(__file__).parent
IMGS_PATH = ROOT / "clock"


def _outputPath() -> Path:
    """运行时生成的图片写这里。

    素材（config.yml、数字图、字体）是只读的，跟程序放一起；合成结果不能写回
    _internal/，否则安装目录不可写（比如把便携版解压进 Program Files）时合成
    直接失败。打包后用用户数据目录；开发时仍写 clock/，方便直接看效果。
    """
    if not getattr(sys, "frozen", False):
        return IMGS_PATH
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return base / "DesktopBackground" / "runtime"


OUT_PATH = _outputPath()
OUT_PATH.mkdir(parents=True, exist_ok=True)

# 先接上文件日志再读配置：配置校验失败会让 windowed exe 直接退出，没有日志
# 就什么线索都留不下。
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
            (config.font.name, config.font.size),
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


async def main():
    async with anyio.create_task_group() as taskGroup:
        taskGroup.start_soon(weater)
        taskGroup.start_soon(exam)
        taskGroup.start_soon(img)


if __name__ == "__main__":
    logger.info("程序启动")
    Thread(target=anyio.run, args=(main,), daemon=True).start()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray = TrayIcon()
    tray.show()
    sys.exit(app.exec())
