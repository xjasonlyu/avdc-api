from typing import Optional

from lxml import etree

from avdc.utility.httpclient import get_html
from avdc.utility.metadata import Actress

XSLIST_URL = 'https://xslist.org/'


def search(name: str) -> list[tuple[str, str]]:
    text = get_html(f'{XSLIST_URL}/search', params={
        'query': name,
        'lg': 'zh'
    })

    tree = etree.fromstring(text, etree.HTMLParser())

    results = []
    for item in tree.xpath('//ul/li'):
        title = item.xpath('.//h3/a/text()')[0]
        href = item.xpath('.//h3/a/@href')[0]
        results.append((title, href))

    return results


def parseURL(name: str) -> Optional[str]:
    for title, href in search(name):
        if name == title.split('-')[-1].strip() or \
                name.isascii() and name.lower() == title.split('-')[0].strip().lower():
            return href


def extractName(text: str) -> str:
    tree = etree.fromstring(text, etree.HTMLParser())
    return tree.xpath('//*[@id="sss1"]/header/h1/span/text()')[0]


def extractInfo(text: str):
    # //*[@id="layout"]/div/p[1]
    tree = etree.fromstring(text, etree.HTMLParser())
    infos: list[str] = tree.xpath('//*[@id="layout"]/div/p[1]/text()')
    extra: list[str] = tree.xpath('//*[@id="layout"]/div/p[1]/span/text()')
    return [parseInfo(i) for i in infos[:6] + extra]


def parseInfo(info: str) -> str:
    return info.split(':', maxsplit=1)[-1].replace('n/a', '').strip()


def main(name: str):
    url = parseURL(name)
    if not url:
        return

    text = get_html(url, raise_for_status=True)
    return Actress(extractName(text), *extractInfo(text))


if __name__ == '__main__':
    # print(main('桃園怜奈'))
    # print(main('桜空もも'))
    print(main('大原あむ'))
