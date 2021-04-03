import re

from bs4 import BeautifulSoup
from lxml import etree
from pyquery import PyQuery as pq

from avdc.model.metadata import Metadata
from avdc.utility.httpclient import get_html
from avdc.utility.misc import concurrentMap, extractTitle


def getCover(text: str) -> str:  # 获取封面链接
    doc = pq(text)
    image = doc('a.bigImage')
    return image.attr('href')


def getTitle(text: str) -> str:  # 获取标题
    doc = pq(text)
    title = str(doc('div.container h3').text())
    return extractTitle(title)


def _getAttribute(text: str, attr: str, sub_expr: str) -> str:
    tree = etree.fromstring(text, etree.HTMLParser())
    for r in tree.xpath('/html/body/div[5]/div[1]/div[2]//p'):
        if attr in str(r.xpath('.//span[1]/text()')):
            for s in r.xpath(sub_expr):
                return str(s).strip()
    return ''


def getVID(text: str) -> str:  # 获取番号
    return _getAttribute(text, '識別碼', './span[2]/text()').upper()


def getStudio(text: str) -> str:  # 获取厂商
    return _getAttribute(text, '製作商', './a/text()')


def getPublisher(text: str) -> str:  # 获取發行商
    return _getAttribute(text, '發行商', './a/text()')


def getRelease(text: str) -> str:  # 获取出版日期
    return _getAttribute(text, '發行日期', './text()')


def getRuntime(text: str) -> str:  # 获取分钟
    return _getAttribute(text, '長度', './text()').removesuffix('分鐘')


def getDirector(text: str) -> str:  # 获取导演 已修改
    return _getAttribute(text, '導演', './a/text()')


def getSeries(text: str) -> str:  # 获取系列
    return _getAttribute(text, '系列', './a/text()')


def getOverview(_: str) -> str:
    return ''  # javbus don't provide overview


def getActresses(text: str) -> list[str]:  # 获取女优
    soup = BeautifulSoup(text, 'lxml')
    return [i.get_text() for i in soup.find_all(attrs={'class': 'star-name'})]


def getGenres(text: str) -> list[str]:  # 获取标签
    soup = BeautifulSoup(text, 'lxml')
    result = soup.find_all(attrs={'class': 'genre'})
    return [i.get_text().strip() for i in result if 'gr_sel' in str(i)]


def getImages(text: str) -> list[str]:  # 获取剧照
    results = re.search(r'<div id=\"sample-waterfall\">[\s\S]*?</div></a>\s*?</div>', text)
    if not results:
        return []

    results = results.group(0)
    return re.findall(r'<a class=\"sample-box\" href=\"(.*?)\"', results)


def searchVID(keyword: str):
    keyword = keyword.upper()

    def _searchVID(text: str):
        _keyword = keyword.replace('-', '').replace('_', '')

        soup = BeautifulSoup(text, 'lxml')
        results = soup.find_all(attrs={'class': 'movie-box'})
        if not results:
            return

        for result in results:
            r = re.compile(r'href="https://www.javbus.com/(.*?)"')
            items = re.findall(r, str(result))
            for vid in items:
                vid = vid.strip().upper()
                if vid.replace('-', '').replace('_', '').startswith(_keyword):
                    return vid

    search_page, search_page_uncensored = concurrentMap(
        lambda url: get_html(url, raise_for_status=lambda r: r.status_code != 404), [
            f'https://www.javbus.com/search/{keyword}',
            f'https://www.javbus.com/uncensored/search/{keyword}',
        ], max_workers=2)

    return _searchVID(search_page) or _searchVID(search_page_uncensored)


def main(keyword: str) -> Metadata:
    vid = searchVID(keyword)
    if not vid:
        vid = keyword

    url = f'https://www.javbus.com/{vid}'
    text = get_html(url, raise_for_status=True)

    return Metadata(**{
        'title': getTitle(text),
        'studio': getStudio(text) or getPublisher(text),
        'overview': getOverview(text),
        'runtime': getRuntime(text),
        'director': getDirector(text),
        'actresses': getActresses(text),
        'release': getRelease(text),
        'vid': getVID(text),
        'cover': getCover(text),
        'genres': getGenres(text),
        'images': getImages(text),
        'label': getSeries(text),
        'source': url,
        'provider': 'javbus',
        'series': getSeries(text),
    })


if __name__ == "__main__":
    # print(main('ipx-292'))
    # print(main('111820-001'))
    print(main('ABP-041'))
