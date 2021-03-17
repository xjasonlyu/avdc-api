import re

from bs4 import BeautifulSoup
from lxml import html

from avdc.utility.httpclient import post
from avdc.utility.metadata import Metadata


def get_bold_text(h: str) -> str:
    soup = BeautifulSoup(h, "html.parser")
    if soup.b:
        return soup.b.text
    else:
        return "UNKNOWN_TAG"


def get_anchor_info(h: str) -> str:
    result = []

    data = BeautifulSoup(h, "html.parser").find_all("a", href=True)
    for d in data:
        result.append(d.text)

    return ",".join(result)


def get_text_info(h: str) -> str:
    return h.split(": ")[1]


def getTitle(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[1]/div[1]/div[1]/h3/text()")[0].strip()


def getImages(content: str) -> list[str]:  # 获取剧照
    hr = re.compile(
        r'<div class=\"col-md-3\"><div class=\"col-xs-12 col-md-12\">[\s\S]*?</script><script async '
        r'src=\"//adserver\.juicyads\.com/js/jads\.js\">')
    h = hr.search(content)
    if h:
        h = h.group()
        hf = re.compile(r'<img.*?src=\"(.*?)\"')
        return hf.findall(h)
    return []


def getCover(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[2]/div[1]/p/a/img/@src")[0]


def getOverview(lx: html.HtmlElement) -> str:
    result = lx.xpath("/html/body/div[2]/div[1]/div[1]/div[2]/div[3]/div/text()")
    return result[0] if result else ''


def getStars(data: hash) -> list[str]:
    if "出演者" in data:
        return get_anchor_info(data["出演者"]).split(",")
    else:
        return []


def getLabel(data: hash) -> str:
    if "メーカー" in data:
        return get_anchor_info(data["メーカー"])
    else:
        return ""


def getTags(data: hash) -> list[str]:
    if "ジャンル" in data:
        return get_anchor_info(data["ジャンル"]).split(",")
    else:
        return []


def getStudio(data: hash) -> str:
    if "メーカー" in data:
        return get_anchor_info(data["メーカー"])
    else:
        return ""


def getID(data: hash) -> str:
    if "品番" in data:
        return get_text_info(data["品番"])
    else:
        return ""


def getRelease(data: hash) -> str:
    if "配信開始日" in data:
        return get_text_info(data["配信開始日"])
    else:
        return ""


def getRuntime(data: hash) -> str:
    if "収録時間" in data:
        return get_text_info(data["収録時間"]).rstrip("minutes").strip()
    else:
        return ""


# def getYear(data: hash) -> str:
#     if "release" in data:
#         return data["release"][:4]
#     else:
#         return ""


def getSeries(data: hash) -> str:
    if "シリーズ" in data:
        return get_anchor_info(data["シリーズ"])
    else:
        return ""


def getSeries2(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/a[11]/text()")[0]


def parse_info(soup: BeautifulSoup) -> dict:
    data = soup.select_one("div.row > div.col-md-9")

    if data:
        dd = str(data).split("<br/>")
        data_dic = {}
        for d in dd:
            data_dic[get_bold_text(h=d)] = d

        return {
            'stars': getStars(data_dic),
            'label': getLabel(data_dic),
            'studio': getStudio(data_dic),
            'tags': getTags(data_dic),
            'id': getID(data_dic),
            'release': getRelease(data_dic),
            'runtime': getRuntime(data_dic),
            'series': getSeries(data_dic),
        }
    else:
        return {}


def main(keyword: str) -> Metadata:
    r = post(url='https://www.jav321.com/search', data={'sn': keyword})

    soup = BeautifulSoup(r.text, 'html.parser')
    lx = html.fromstring(str(soup))

    metadata = {}
    if '/video/' in r.url:
        data = parse_info(soup)

        metadata = {
            'title': getTitle(lx),
            # 'year': getYear(data),
            'overview': getOverview(lx),
            'director': '',
            'cover': getCover(lx),
            'images': getImages(r.text),
            # 'star_photos': '',
            'website': r.url,
            'source': 'jav321',
            **data,
        }
    return Metadata(metadata)


if __name__ == '__main__':
    # print(main('miae-003'))
    print(main('ABP-110'))
