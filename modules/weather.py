import requests
from lxml import etree
from .log import logger

#: (连接超时, 读取超时) 秒。没有超时的话，接口卡住会把整个天气循环永久挂住，
#: 壁纸也就不再更新了。
TIMEOUT = (5, 10)


def resqPage():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0"
    }
    try:
        resq = requests.get(
            "https://www.tianqi.com/lanzhou/15/", headers=headers, timeout=TIMEOUT
        )
    except requests.RequestException as e:
        logger.warning(f"获取天气失败：{e}")
        return ""
    if resq.status_code != 200:
        logger.error("获取天气失败")
        return ""
    logger.debug("天气网页获取成功")
    return resq.text


def getweather():
    page = resqPage()
    if not page:
        return "获取天气失败"
    html = etree.HTML(page, etree.HTMLParser())
    # 网页改版或返回错误页时 xpath 取不到，别让整个循环崩掉
    weather = html.xpath("/html/body/div[6]/div[4]/div[1]/div[1]/div/h3/text()")
    low = html.xpath("/html/body/div[6]/div[4]/div[1]/div[1]/div/p/span[1]/text()")
    high = html.xpath("/html/body/div[6]/div[4]/div[1]/div[1]/div/p/span[2]/text()")
    if not (weather and low and high):
        logger.warning("解析天气数据失败，页面结构可能变了")
        return "获取天气失败"
    temperature = f"{low[0]}~{high[0]} ℃"
    logger.debug(f"天气：{weather[0]}，温度：{temperature}")
    return (
        f"{weather[0]}  {temperature}"
        if weather[0] and temperature != "~ ℃"  # 判断是否获取到天气
        else "获取天气失败"
    )


@logger.catch
def test():
    logger.info(getweather())


if __name__ == "__main__":
    test()
