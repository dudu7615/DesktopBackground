from PIL import Image, ImageDraw, ImageFont
from .log import logger
from .dataClass import Font
from pathlib import Path
import os
import tempfile


def _saveAtomic(img: Image.Image, path: Path) -> None:
    """先写临时文件再原子替换。

    同一个用户的安装版与便携版可能同时开着，两边共用同一个 runtime 目录；
    直接覆盖会让另一边读到写了一半的文件。rename 是原子的，读到的永远是
    完整的旧图或完整的新图。
    """
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=path.suffix)
    os.close(fd)
    try:
        img.save(tmp)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _fontFile(assets: Path, name: str) -> str:
    """优先用 clock 目录里自带的字体文件，找不到再交给 PIL 按系统字体名查找。"""
    local = assets / name
    return str(local) if local.exists() else name


#: 由程序在运行时绘制、只存在于输出目录的图层。数字图（month/day/hour…）
#: 和背景是打包时自带的素材，不在此列。
GENERATED_LAYERS = frozenset({"weather.png", "exam.png"})


def _isGenerated(name: str) -> bool:
    return Path(name).name in GENERATED_LAYERS


def weatherImg(
    assets: Path,
    out: Path,
    size: tuple[int, int],
    place: tuple[float, float],
    weather: str,
    font: Font,
    fill: tuple[int, int, int],
):
    """绘制天气图片保存到 out/weather.png

    素材（字体）从 assets 读，生成结果写 out——打包后 out 是用户数据目录，
    程序目录可能不可写。
    """
    textFont = ImageFont.truetype(font=_fontFile(assets, font.name), size=font.size)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(img).text(place, weather, font=textFont, fill=fill)
    _saveAtomic(img, out / "weather.png")
    logger.debug("绘制天气图片成功")


def examDaysImg(
    assets: Path,
    out: Path,
    size: tuple[int, int],
    place: tuple[float, float],
    days: str,
    font: Font,
    fill: tuple[int, int, int],
):
    """高考剩余时间，保存到 out/exam.png

    字体参数与 weatherImg 保持一致（都收 Font），调用方直接传 config.font 即可。
    """
    textFont = ImageFont.truetype(font=_fontFile(assets, font.name), size=font.size)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(img).text(place, f"高考剩余{days}天", font=textFont, fill=fill)
    _saveAtomic(img, out / "exam.png")
    logger.debug("绘制高考时间图片成功")


def BgImg(
    assets: Path, out: Path, size: tuple[int, int], background: str, *layers: str
):
    """合成背景图片保存到 out/result.png

    背景与数字图从 assets 读，运行时生成的图层（weather.png、exam.png）从
    out 读。每个图层先找 out 再找 assets。

    运行时生成的文件**不能**回退到 assets：从 V1.0.x 升级上来的安装目录里
    还留着旧版本写在 clock/ 下的 weather.png，回退过去会把过期的天气叠上去。
    """

    def resolve(name: str) -> Path | None:
        generated = out / name
        if generated.exists():
            return generated
        bundled = assets / name
        return bundled if bundled.exists() else None

    logger.debug("开始合成背景图片")
    img = Image.open(assets / background).convert("RGBA")
    for imgPath in layers:
        resolved: Path | None
        if _isGenerated(imgPath):
            # 运行时生成的文件只认 out：开机第一次合成时天气模块可能还没写出
            # weather.png，少一层就少一层，不能让整次合成都失败
            candidate = out / imgPath
            resolved = candidate if candidate.exists() else None
        else:
            resolved = resolve(imgPath)
        if resolved is None:
            logger.warning(f"缺少图层 {imgPath}，本次跳过")
            continue
        img.alpha_composite(Image.open(resolved).convert("RGBA"))
    _saveAtomic(img, out / "result.png")
    logger.debug("合成背景图片成功")
