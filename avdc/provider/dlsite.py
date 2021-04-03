from lxml import etree

from avdc.model.metadata import Metadata
from avdc.utility.httpclient import get_html
from avdc.utility.misc import extractTitle


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
    tree = etree.fromstring(a, etree.HTMLParser())
    title = tree.xpath('//*[@id="work_name"]/a/text()')[0]
    return extractTitle(title)


def getActresses(a: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    return tree.xpath('//th[contains(text(),"声优")]/../td/a/text()')


def getStudio(a: str) -> str:
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = tree.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except (IndexError, Exception):
            result = tree.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except (IndexError, Exception):
        result = ''
    return result


def getRuntime(a: str) -> str:
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(tree.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(tree.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')


def getLabel(a: str) -> str:
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = tree.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except (IndexError, Exception):
            result = tree.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except (IndexError, Exception):
        result = ''
    return result


def getRelease(a: str) -> str:
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = tree.xpath('//th[contains(text(),"贩卖日")]/../td/a/text()')[0]
    return result.replace('年', '-').replace('月', '-').replace('日', '')


def getGenres(a: str) -> list[str]:
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    return tree.xpath('//th[contains(text(),"分类")]/../td/div/a/text()')


def getSmallCover(a: str, index: int = 0) -> str:
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the first one, get the one with correct index number
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = tree.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if 'https' not in result:
            result = 'https:' + result
        return result
    except (IndexError, Exception):  # 2020.7.17 Repair Cover Url crawl
        result = tree.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
        if 'https' not in result:
            result = 'https:' + result
        return result


def getCover(text: str) -> str:
    tree = etree.fromstring(text, etree.HTMLParser())
    result = tree.xpath('//*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li/img/@src')[0]
    return result


def getDirector(a: str) -> str:
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = tree.xpath('//th[contains(text(),"剧情")]/../td/a/text()')[0]
    except (IndexError, Exception):
        result = ''
    return result


def getOverview(text: str) -> str:
    tree = etree.fromstring(text, etree.HTMLParser())
    total = []
    result = tree.xpath('//*[@id="main_inner"]/div[3]/text()')
    for i in result:
        total.append(i.strip('\r\n'))
    return str(total).strip(" ['']").replace("', '', '", r'\n').replace("', '", r'\n').strip(", '', '")


def getSeries(a: str) -> str:
    tree = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = tree.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except (IndexError, Exception):
            result = tree.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except (IndexError, Exception):
        result = ''
    return result


def main(keyword: str) -> Metadata:
    keyword = keyword.upper()

    url = f'https://www.dlsite.com/pro/work/=/product_id/{keyword}.html'
    text = get_html(url,
                    cookies={'locale': 'zh-cn'},
                    raise_for_status=True)

    return Metadata(**{
        'actresses': getActresses(text),
        'title': getTitle(text),
        'studio': getStudio(text),
        'overview': getOverview(text),
        'runtime': '',
        'director': getDirector(text),
        'release': getRelease(text),
        'vid': keyword,
        'cover': 'https:' + getCover(text),
        # 'small_cover': '',
        'genres': getGenres(text),
        'label': getLabel(text),
        # 'star_photos': '',
        'source': url,
        'provider': 'dlsite',
        'series': getSeries(text),
    })


if __name__ == "__main__":
    # print(main('VJ013178'))
    print(main('VJ014291'))
