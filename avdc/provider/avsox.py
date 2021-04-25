from bs4 import BeautifulSoup
from cachetools import cached, TTLCache
from lxml import etree

from avdc.model.metadata import Metadata
from avdc.provider import NotFound
from avdc.utility.httpclient import get_html
from avdc.utility.misc import extractTitle


def getTitle(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    title = tree.xpath('/html/body/div[2]/h3/text()')[0]
    return extractTitle(title)


def getActresses(content: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'avatar-box'})
    d = []
    for i in a:
        d.append(i.span.get_text())
    return d


def getStudio(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = tree.xpath('//p[contains(text(),"メーカー:")]/following-sibling::p[1]/a/text()')
    return result[0] if result else ''


def getRuntime(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = tree.xpath('//span[contains(text(),"収録時間:")]/../text()')
    return result[0].removesuffix('分') if result else ''


def getLabel(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = tree.xpath('//p[contains(text(),"メーカー:")]/following-sibling::p[1]/a/text()')
    return result[0] if result else ''


def getVID(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    return tree.xpath('//span[contains(text(),"品番:")]/../span[2]/text()')[0]


def getRelease(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = tree.xpath('//span[contains(text(),"発売日:")]/../text()')
    return result[0] if result else ''


def getCover(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    return tree.xpath('/html/body/div[2]/div[1]/div[1]/a/img/@src')[0]


# def getSmallCover(content: str) -> str:
#     tree = etree.fromstring(content, etree.HTMLParser())
#     result = str(tree.xpath('//*[@id="waterfall"]/div/a/div[1]/img/@src')).strip(" ['']")
#     return result


def getGenres(content: str) -> list[str]:
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'genre'})
    d = []
    for i in a:
        d.append(i.get_text())
    return d


def getSeries(content: str) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = tree.xpath('//span[contains(text(),"シリーズ:")]/../span[2]/text()')
    return result[0] if result else ''


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def _getAvsoxSite() -> str:
    text = get_html('https://tellme.pw/avsox')
    return etree.HTML(text).xpath('//div[@class="container"]/div/a/@href')[0]


def main(keyword: str) -> Metadata:
    avsox_site = _getAvsoxSite()

    def search_url(v):
        x = get_html(avsox_site + '/ja/search/' + v)
        tree = etree.fromstring(x, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        for r in tree.xpath('//*[@id="waterfall"]/div/a/@href'):
            return str(r), x
        return None, x

    url, search_page = search_url(keyword)

    if not url or url.count('https://') > 1:
        raise NotFound(f'avsox: {keyword} not found')

    text = get_html(url, raise_for_status=True)
    soup = BeautifulSoup(text, 'lxml')
    info = str(soup.find(attrs={'class': 'row movie'}))

    return Metadata(**{
        'actresses': getActresses(text),
        'title': getTitle(text),
        'studio': getStudio(info),
        'overview': '',  #
        'runtime': getRuntime(info),
        'director': '',  #
        'release': getRelease(info),
        'vid': getVID(info),
        'cover': getCover(text),
        # 'small_cover': getSmallCover(search_page),
        'genres': getGenres(text),
        'label': getLabel(info),
        'source': url,
        'provider': 'avsox',
        'series': getSeries(info),
    })


if __name__ == "__main__":
    # print(main('012717_472'))
    print(main('092719-001'))
