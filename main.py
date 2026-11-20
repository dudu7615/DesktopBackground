import sys
import yaml
import anyio
from datetime import datetime
from pathlib import Path
from threading import Thread
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from modules import makeImg, setBg, weather, logger, Config

ROOT = Path(__file__).parent
IMGS_PATH = ROOT / "clock"

_config = yaml.load(
    (IMGS_PATH / "config.yml").read_text(encoding="utf-8"), Loader=yaml.FullLoader
)
config = Config.model_validate(_config)


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
                config.size,
                "bg.jpg",
                "weather.png",
                # "exam.png",
                f"month{nowTime.month}.png",
                f"day{nowTime.day}.png",
                f"hour{nowTime.hour}.png",
                f"minute{nowTime.minute}.png",
                f"weekday{nowTime.weekday()+1}.png",
            )
            setBg.setBackGroundImg(IMGS_PATH / "result.png")

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
