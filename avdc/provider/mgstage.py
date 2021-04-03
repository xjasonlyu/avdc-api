import re

from bs4 import BeautifulSoup
from lxml import etree

from avdc.model.metadata import Metadata
from avdc.utility.httpclient import get_html


def getTitle(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())
    return html.xpath('//*[@id="center_column"]/div[1]/h1/text()')[0].strip()


def getActresses(a: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"出演：")]/../td/text()')
    result2 = html.xpath('//th[contains(text(),"出演：")]/../td/a/text()')

    return [k.strip() for j in {i.strip() for i in result1 + result2 if i.strip()}
            for k in j.split() if k.strip()]


def getStudio(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"メーカー：")]/../td/a/text()')
    result2 = html.xpath('//th[contains(text(),"メーカー：")]/../td/text()')
    result = list({i.strip() for i in result1 + result2 if i.strip()})
    return result[0] if result2 else ''


def getRuntime(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"収録時間：")]/../td/a/text()')
    result2 = html.xpath('//th[contains(text(),"収録時間：")]/../td/text()')
    result: list[str] = [i.strip() for i in result1 + result2 if i.strip()]
    return result[0].removesuffix('min') if result else ''


def getLabel(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"レーベル：")]/../td/a/text()')
    result2 = html.xpath('//th[contains(text(),"レーベル：")]/../td/text()')
    result = [i.strip() for i in result1 + result2 if i.strip()]
    return result[0] if result else ''


def getVID(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"品番：")]/../td/a/text()')
    result2 = html.xpath('//th[contains(text(),"品番：")]/../td/text()')
    result = [i.strip() for i in result1 + result2 if i.strip()]
    return result[0] if result else ''


def getRelease(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"配信開始日：")]/../td/a/text()')
    result2 = html.xpath('//th[contains(text(),"配信開始日：")]/../td/text()')
    result = [i.strip().replace('/', '-') for i in result1 + result2 if i.strip()]
    return result[0] if result else ''


def getGenres(a: str) -> list[str]:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"ジャンル：")]/../td/a/text()')
    result2 = html.xpath('//th[contains(text(),"ジャンル：")]/../td/text()')
    return [i.strip() for i in result1 + result2 if i.strip()]


def getCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result: list[str] = html.xpath('//*[@id="EnlargeImage"]/@href')
    return result[0].strip() if result else ''


# def getSmallCover(content: str) -> str:
#     html = etree.fromstring(content, etree.HTMLParser())
#     result = str(html.xpath('//*[@id="center_column"]/div[1]/div[1]/div/div/h2/img/@src')).strip(" ['']")
#     #                    /html/body/div[2]/article[2]/div[1]/div[1]/div/div/h2/img/@src
#     return result


def getSeries(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"シリーズ")]/../td/a/text()')
    result2 = html.xpath('//th[contains(text(),"シリーズ")]/../td/text()')
    result = [i.strip() for i in result1 + result2 if i.strip()]
    return result[0] if result else ''


def getOverview(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result: list[str] = html.xpath('//p/text()')
    return result[0].strip() if result else ''


def getImages(content: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<dd>\s*?<ul>[\s\S]*?</ul>\s*?</dd>')
    html = hr.search(content)
    if html:
        html = html.group()
        hf = re.compile(r'<a class=\"sample_image\" href=\"(.*?)\"')
        return hf.findall(html)
    return []


def main(keyword: str) -> Metadata:
    keyword = keyword.upper()

    url = f'https://www.mgstage.com/product/product_detail/{keyword}/'
    text = str(get_html(url, cookies={'adc': '1'}))

    soup = BeautifulSoup(text, 'lxml')
    a = str(soup.find(attrs={'class': 'detail_data'}))
    b = str(soup.find(attrs={"id": "introduction"}))

    return Metadata(**{
        'title': getTitle(text),
        'studio': getStudio(a),
        'overview': getOverview(b),
        'runtime': getRuntime(a),
        # 'director': getDirector(a),
        'actresses': getActresses(a),
        'release': getRelease(a),
        'vid': getVID(a),
        'cover': getCover(text),
        # 'small_cover': getSmallCover(text),
        'genres': getGenres(a),
        'label': getLabel(a),
        'images': getImages(text),
        # 'star_photos': '',
        'source': url,
        'provider': 'mgstage',
        'series': getSeries(a),
    })


if __name__ == '__main__':
    # print(main('422ion-0062'))
    # print(main('AVOP-008'))
    print(main('485GCB-011'))
