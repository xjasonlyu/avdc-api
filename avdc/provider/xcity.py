import re

from lxml import etree

from avdc.model.metadata import Metadata
from avdc.utility.httpclient import get_html


def getTitle(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath('//*[@id="program_detail_title"]/text()')[0]
    return result


def getActresses(a: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[2]/a/text()')
    if not result:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[3]/a/text()')

    return [i.strip() for i in result]


def getStudio(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[4]/a/span/text()')).strip(
            " ['']")
    except:
        result = str(html.xpath('//strong[contains(text(),"片商")]/../following-sibling::span/a/text()')).strip(" ['']")
    return result.strip('+').replace("', '", '').replace('"', '')


def getRuntime(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        # //*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[3]
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[3]/text()')
        result = [i for i in result if i.strip()]
        if result:
            return re.findall(r'\d+', result[0])[0]
    except:
        return ''
    return ''


def getLabel(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[5]/a/span/text()')[0]
        return result
    except:
        return ''


def getVID(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())
    try:
        result = html.xpath('//*[@id="hinban"]/text()')[0]
        return result
    except:
        return ''


def getRelease(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[4]/text()')
        result = [i for i in result if i.strip()]
        if result:
            return re.findall(r'\d{4}/\d{2}/\d{2}', result[0])[0].replace('/', '-')
    except:
        return ''
    return ''


def getGenres(a: str) -> list[str]:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # //*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[5]
    result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[5]/a/text()')
    return [i.strip() for i in result]


def getSmallCover(a: str, index: int = 0) -> str:
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
    if 'https' not in result:
        result = 'https:' + result
    return result


def getCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[1]/p/a/@href')[0]
        return 'https:' + result
    except:
        return ''


def getDirector(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//*[@id="program_detail_director"]/text()')[0].replace(u'\n', '').replace(u'\t', '')
        return result
    except:
        return ''


def getOverview(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[5]/p/text()')[0]
    except:
        return ''
    try:
        return re.sub(r'\\\\\w*\d+', '', result)
    except:
        return result


def getSeries(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    try:
        try:
            result = html.xpath("//span[contains(text(),'シリーズ')]/../a/span/text()")[0]
            return result
        except:
            result = html.xpath("//span[contains(text(),'シリーズ')]/../span/text()")[0]
            return result
    except:
        return ''


def getImages(content: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<div id="sample_images".*?>[\s\S]*?</div>')
    html = hr.search(content)
    if html:
        html = html.group()
        hf = re.compile(r'<a.*?href=\"(.*?)\"')
        return ['https:' + i.replace('/scene/small', '') for i in hf.findall(html)]
    return []


def main(keyword: str) -> Metadata:
    keyword = keyword.upper()

    query_result = get_html(
        'https://xcity.jp/result_published/?genre=%2Fresult_published%2F&q=' + keyword.
        replace('-', '') + '&sg=main&num=30')
    html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    urls = html.xpath("//table[contains(@class, 'resultList')]/tr[2]/td[1]/a/@href")[0]
    detail_page = get_html('https://xcity.jp' + urls)

    return Metadata(**{
        'actresses': getActresses(detail_page),
        'title': getTitle(detail_page),
        'studio': getStudio(detail_page),
        'overview': getOverview(detail_page),
        'runtime': getRuntime(detail_page),
        'director': getDirector(detail_page),
        'release': getRelease(detail_page),
        'vid': getVID(detail_page),
        'cover': getCover(detail_page),
        # 'small_cover': '',
        'images': getImages(detail_page),
        'genres': getGenres(detail_page),
        'label': getLabel(detail_page),
        # 'star_photos': '',
        'source': 'https://xcity.jp' + urls,
        'provider': 'xcity',
        'series': getSeries(detail_page),
    })


if __name__ == '__main__':
    # print(main('VNDS-2624'))
    print(main('MILK-079'))
