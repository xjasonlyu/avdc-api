import json
from urllib.parse import urljoin

from lxml import etree

from avdc.model.metadata import Metadata
from avdc.provider import NotFound
from avdc.utility.httpclient import get_html, Session


def getTitle(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = html.xpath('/html/head/title/text()')
    return result[0] if result else ''


def getOverview(text: str, session: Session) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = html.xpath('//*[@id="top"]/div[1]/section[4]/iframe/@src')
    if not result:
        return ''

    url = urljoin('https://adult.contents.fc2.com/', result[0])
    return '\n'.join(i.strip() for i in
                     etree.fromstring(session.get(url).text,
                                      etree.HTMLParser()).xpath('/html/body/div/text()')
                     if i.strip())


def getStudio(text: str) -> str:  # 获取厂商
    html = etree.fromstring(text, etree.HTMLParser())
    result = html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()')
    return result[0] if result else ''


def getRelease(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result: list[str] = html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/div[2]/p/text()')
    text = result[0].replace('/', '-').replace(':', ' ') if result else '0000-00-00'
    return text.split()[-1]


def getCover(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[1]/span/img/@src')
    return urljoin('https:', result[0]) if result else ''


def getGenres(number: str) -> list[str]:
    url = f'https://adult.contents.fc2.com/api/v4/article/{number}/tag?'
    data = json.loads(get_html(url))
    if data['code'] != 200:
        raise ValueError(f"Bad code: {data['code']}")
    return [i['tag'] for i in data.get('tags', [])]


def getImages(text: str) -> list[str]:  # 获取剧照
    html = etree.fromstring(text, etree.HTMLParser())
    results = html.xpath('//*[@id="top"]/div[1]/section[2]/ul/li')
    return [result.xpath('.//a/@href')[0] for result in results
            if result.xpath('.//a/@href')]


def checkProduct(text: str) -> bool:
    html = etree.fromstring(text, etree.HTMLParser())
    title = html.xpath('/html/head/title/text()')[0]
    return 'Unable to find Product.' not in title


def main(keyword: str) -> Metadata:
    keyword = keyword.upper() \
        .replace('_', '-') \
        .replace('FC2PPV-', '') \
        .replace('FC2-PPV-', '') \
        .replace('FC2-', '')

    if not keyword.isdecimal():
        raise ValueError(f'invalid product number: {keyword}')

    with Session() as session:
        url = f'https://adult.contents.fc2.com/article/{keyword}/'
        text = session.get(url).text
        # overview
        overview = getOverview(text, session)

    if not checkProduct(text):
        raise NotFound(f'{keyword} not found')

    return Metadata(**{
        'title': getTitle(text),
        'studio': getStudio(text),
        'overview': overview,
        'runtime': 0,
        'director': getStudio(text),
        'actresses': [],  # fc2 no actresses
        'release': getRelease(text),
        'vid': f'FC2-{keyword}',
        'label': '',
        'cover': getCover(text),
        'images': getImages(text),
        'genres': getGenres(keyword),
        'source': url,
        'provider': 'fc2',
        'series': '',
    })


if __name__ == '__main__':
    # print(main('FC2-1603395'))
    print(main('FC2PPV-1455209'))
