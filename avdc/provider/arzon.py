import re
from typing import Optional
from urllib.parse import urljoin

from lxml import etree

from avdc.model.metadata import Metadata
from avdc.provider import NotFound
from avdc.utility.httpclient import Session


def getTitle(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    title = tree.xpath('//*[@id="detail_new"]/div[2]/table/tr/td[2]/h1/text()')[0]
    return re.sub(r'^【.*?】', '', title)


def getOverview(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    elements = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[2]/td/div/text()')
    return [i.strip() for i in elements if i.strip()][0]


def getCover(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    url = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[1]/td[1]/a/img/@src')[0]
    return urljoin('https:', url)


def getDirector(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    try:
        director = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[5]/td[2]/a/text()')[0]
    except IndexError:
        return ''
    else:
        return director.strip()


def getActresses(content: bytes) -> list[str]:
    tree = etree.fromstring(content, etree.HTMLParser())
    actresses = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[1]/td[2]/a/text()')
    return [actress.strip() for actress in actresses if actress.strip()]


# def getGenres(content: bytes) -> list[str]:
#     pass


def getImages(content: bytes) -> list[str]:
    tree = etree.fromstring(content, etree.HTMLParser())
    images = tree.xpath('//*[@id="detail_new"]/div[3]/img/@src')
    return [urljoin('https:', img.strip()) for img in images if img.strip()]


def getStudio(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    try:
        result = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[2]/td[2]/a/text()')[0]
    except IndexError:
        return ''
    else:
        return result.strip()


def getSeries(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    try:
        result = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[4]/td[2]/a/text()')[0]
    except IndexError:
        return getSeries2(content)  # fallback
    else:
        return result.strip()


def getSeries2(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    try:
        result = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[3]/td[2]/a/text()')[0]
    except IndexError:
        return ''
    else:
        return result.strip()


def getRelease(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    try:
        result = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[6]/td[2]/text()')[0]
    except IndexError:
        return ''
    else:
        release = re.findall(r'(\d{4}/\d{2}/\d{2})', result.strip())[0]
        return release.replace('/', '-')


def getRuntime(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    try:
        result: str = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[7]/td[2]/text()')[0]
    except IndexError:
        return ''
    else:
        return result.strip().removesuffix('分')


def getVID(content: bytes) -> str:
    tree = etree.fromstring(content, etree.HTMLParser())
    try:
        result: str = tree.xpath('//*[@id="detail_new"]/table/tr/td[1]/table/tr[3]/td/div/table/tr[8]/td[2]/text()')[0]
    except IndexError:
        return ''
    else:
        return re.findall(r'(\w+[\-_]\w+)', result.strip())[0]


def check_age(s: Session):
    r = s.get('https://www.arzon.jp/index.php', params={
        'action': 'adult_customer_agecheck',
        'agecheck': 1,
        'redirect': 'https://www.arzon.jp/'
    })
    r.raise_for_status()


def search(s: Session, keyword: str) -> Optional[int]:
    url = f'https://www.arzon.jp/itemlist.html'
    content = s.get(url, params={
        'q': keyword,
        't': 'all',
        'm': 'all',
        'mkt': 'all',
        'disp': 30,
        'sort': 'saledate'
    }).content

    tree = etree.fromstring(content, etree.HTMLParser())
    href = tree.xpath('//*[@id="item"]/div[1]/dl/dt/a/@href')

    try:
        item_id = int(re.findall(r'item_(\d+)\.html', href[0])[0])
    except (IndexError, TypeError, ValueError):
        return
    else:
        return item_id


def main(keyword: str) -> Metadata:
    with Session() as session:
        # pass age check
        check_age(session)

        # search for item id
        item_id = search(session, keyword)
        if item_id is None:
            raise NotFound(f'arzon: {keyword} not found')

        item_url = f'https://www.arzon.jp/item_{item_id}.html'
        content = session.get(item_url).content

        # headers={'Referer': 'https://www.arzon.jp/'}

    return Metadata(**{
        'title': getTitle(content),
        'studio': getStudio(content),
        'overview': getOverview(content),
        'runtime': getRuntime(content),
        'director': getDirector(content),
        'actresses': getActresses(content),
        'release': getRelease(content),
        'vid': getVID(content),
        'cover': getCover(content),
        'genres': [],
        'images': getImages(content),
        'label': getSeries(content),
        'source': item_url,
        'provider': 'arzon',
        'series': getSeries(content),
    })


if __name__ == '__main__':
    print(main('ssni-999'))
