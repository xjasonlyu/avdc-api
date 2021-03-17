import re

from bs4 import BeautifulSoup
from lxml import etree

from avdc.utility.httpclient import get_html
from avdc.utility.metadata import Metadata


def getTitle(a: str) -> str:
    try:
        html = etree.fromstring(a, etree.HTMLParser())
        result = str(html.xpath('//*[@id="center_column"]/div[1]/h1/text()')).strip(" ['']")
        return result.replace('/', ',')
    except:
        return ''


def getStars(a: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"出演：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"出演：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    stars = str(result1 + result2).strip('+').replace("', '", '').replace('"', '').replace('/', ',').replace('\\n', '')
    return [i.strip() for i in stars.split() if i.strip()]


def getStudio(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"メーカー：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"メーカー：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '').strip()


def getRuntime(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"収録時間：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"収録時間：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').rstrip('mi').strip()


def getLabel(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"レーベル：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"レーベル：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '').strip()


def getVID(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"品番：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"品番：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+')


def getRelease(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"配信開始日：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"配信開始日：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace('/', '-')


def getTags(a: str) -> list[str]:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"ジャンル：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"ジャンル：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result = str(result1 + result2).strip('+').replace("', '\\n", ",").replace("', '", ""). \
        replace('"', '').replace(',,', '').split(',')
    return [i.strip() for i in result if i.strip()]


def getCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('//*[@id="EnlargeImage"]/@href')).strip(" ['']")
    #                    //*[@id="EnlargeImage"]
    return result


def getSmallCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[1]/div[1]/div/div/h2/img/@src')).strip(" ['']")
    #                    /html/body/div[2]/article[2]/div[1]/div[1]/div/div/h2/img/@src
    return result


# def getDirector(a: str) -> str:
#     html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
#     result1 = str(html.xpath('//th[contains(text(),"メーカー")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
#         '\\n')
#     result2 = str(html.xpath('//th[contains(text(),"メーカー")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
#         '\\n')
#     return str(result1 + result2).strip('+').replace("', '", '').replace('"', '').strip()


def getOverview(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('//p/text()')).strip(" ['']").replace(u'\\n', '').replace("', '', '", '')
    return result


def getSeries(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


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
    a = str(soup.find(attrs={'class': 'detail_data'})). \
        replace('\n                                        ', ''). \
        replace('                                ', ''). \
        replace('\n                            ', ''). \
        replace('\n                        ', '')
    b = str(soup.find(attrs={"id": "introduction"})). \
        replace('\n                                        ', ''). \
        replace('                                ', ''). \
        replace('\n                            ', ''). \
        replace('\n                        ', '')

    return Metadata({
        'title': getTitle(text).replace("\\n", '').replace('        ', ''),
        'studio': getStudio(a),
        'overview': getOverview(b),
        'runtime': getRuntime(a),
        # 'director': getDirector(a),
        'stars': getStars(a),
        'release': getRelease(a),
        'vid': getVID(a),
        'cover': getCover(text),
        'small_cover': getSmallCover(text),
        'tags': getTags(a),
        'label': getLabel(a),
        'images': getImages(text),
        # 'star_photos': '',
        'website': url,
        'source': 'mgstage',
        'series': getSeries(a),
    })


if __name__ == '__main__':
    # print(main('422ion-0062'))
    # print(main('AVOP-008'))
    print(main('259LUXU-1377'))
