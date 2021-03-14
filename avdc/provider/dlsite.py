from lxml import etree

from avdc.utility.httpclient import get_html
from avdc.utility.metadata import toMetadata


# print(get_html('https://www.dlsite.com/pro/work/=/product_id/VJ013152.html'))
# title //*[@id="work_name"]/a/text()
# studio //th[contains(text(),"ブランド名")]/../td/span[1]/a/text()
# release //th[contains(text(),"販売日")]/../td/a/text()
# story //th[contains(text(),"シナリオ")]/../td/a/text()
# senyo //th[contains(text(),"声優")]/../td/a/text()
# tag //th[contains(text(),"ジャンル")]/../td/div/a/text()
# jianjie //*[@id="main_inner"]/div[3]/text()
# photo //*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li/img/@src

# https://www.dlsite.com/pro/work/=/product_id/VJ013152.html


def getTitle(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath('//*[@id="work_name"]/a/text()')[0]
    return result


def getStars(a: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//th[contains(text(),"声优")]/../td/a/text()')
    except:
        result = []
    return result


def getStudio(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result


def getRuntime(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')


def getLabel(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result


def getRelease(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"贩卖日")]/../td/a/text()')[0]
    return result.replace('年', '-').replace('月', '-').replace('日', '')


def getTags(a: str) -> list[str]:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//th[contains(text(),"分类")]/../td/div/a/text()')
        return result
    except:
        return []


def getSmallCover(a: str, index: int = 0) -> str:
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the first one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
    except:  # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
        if 'https' not in result:
            result = 'https:' + result
        return result


def getCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = html.xpath('//*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li/img/@src')[0]
    return result


def getDirector(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//th[contains(text(),"剧情")]/../td/a/text()')[0]
    except:
        result = ''
    return result


def getOverview(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    total = []
    result = html.xpath('//*[@id="main_inner"]/div[3]/text()')
    for i in result:
        total.append(i.strip('\r\n'))
    return str(total).strip(" ['']").replace("', '', '", r'\n').replace("', '", r'\n').strip(", '', '")


def getSeries(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result


@toMetadata
def main(number: str) -> dict:
    number = number.upper()
    content = get_html('https://www.dlsite.com/pro/work/=/product_id/' + number + '.html',
                       cookies={'locale': 'zh-cn'})

    metadata = {
        'stars': getStars(content),
        'title': getTitle(content),
        'studio': getStudio(content),
        'overview': getOverview(content),
        'runtime': '',
        'director': getDirector(content),
        'release': getRelease(content),
        'id': number,
        'cover': 'https:' + getCover(content),
        # 'small_cover': '',
        'tags': getTags(content),
        'label': getLabel(content),
        # 'star_photos': '',
        'website': 'https://www.dlsite.com/pro/work/=/product_id/' + number + '.html',
        'source': 'dlsite',
        'series': getSeries(content),
    }
    return metadata


if __name__ == "__main__":
    # print(main('VJ013178'))
    print(main('VJ014291'))
