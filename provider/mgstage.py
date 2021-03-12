import re

from bs4 import BeautifulSoup
from lxml import etree

from utility.http import get_html


def getTitle(a: str) -> str:
    try:
        html = etree.fromstring(a, etree.HTMLParser())
        result = str(html.xpath('//*[@id="center_column"]/div[1]/h1/text()')).strip(" ['']")
        return result.replace('/', ',')
    except:
        return ''


def getActor(a: str) -> str:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"出演：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"出演：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '').replace('/', ',')


def getStudio(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"メーカー：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"メーカー：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getRuntime(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"収録時間：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"収録時間：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').rstrip('mi')


def getLabel(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"シリーズ：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"シリーズ：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getID(a: str) -> str:
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
    return str(result1 + result2).strip('+').replace("', '\\n", ",").replace("', '", ""). \
        replace('"', '').replace(',,', '').split(',')


def getCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[1]/div[1]/div/div/h2/img/@src')).strip(" ['']")
    #                    /html/body/div[2]/article[2]/div[1]/div[1]/div/div/h2/img/@src
    return result


def getDirector(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getOutline(content: str) -> str:
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


def main(number: str) -> dict:
    number = number.upper()
    content = str(get_html('https://www.mgstage.com/product/product_detail/' + str(number) + '/',
                           cookies={'adc': '1'}))
    soup = BeautifulSoup(content, 'lxml')

    a = str(soup.find(attrs={'class': 'detail_data'})). \
        replace('\n                                        ', ''). \
        replace('                                ', ''). \
        replace('\n                            ', ''). \
        replace('\n                        ', '')
    b = str(soup.find(attrs={'id': 'introduction'})). \
        replace('\n                                        ', ''). \
        replace('                                ', ''). \
        replace('\n                            ', ''). \
        replace('\n                        ', '')

    metadata = {
        'title': getTitle(content).replace("\\n", '').replace('        ', ''),
        'studio': getStudio(a),
        'outline': getOutline(b),
        'runtime': getRuntime(a),
        'director': getDirector(a),
        'actor': getActor(a),
        'release': getRelease(a),
        'id': getID(a),
        'cover': getCover(content),
        'tags': getTags(a),
        'label': getLabel(a),
        'images': getImages(content),
        'actor_photo': '',
        'website': 'https://www.mgstage.com/product/product_detail/' + str(number) + '/',
        'source': 'mgstage',
        'series': getSeries(a),
    }
    return metadata


if __name__ == '__main__':
    print(main('422ion-0062'))
