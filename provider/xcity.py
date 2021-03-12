import re

from lxml import etree

from utility.http import get_html


def getTitle(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath('//*[@id="program_detail_title"]/text()')[0]
    return result


def getActor(a: str) -> str:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[3]/a/text()')[0]
    return result


def getActorPhoto(actor: str) -> dict:  # //*[@id="star_qdt"]/li/a/img
    a = actor.split(',')
    d = {}
    for i in a:
        p = {i: ''}
        d.update(p)
    return d


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


def getID(a: str) -> str:
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


def getTags(a: str) -> list[str]:
    result2 = []
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[6]/a/text()')
    for i in result1:
        i = i.replace(u'\n', '')
        i = i.replace(u'\t', '')
        result2.append(i)
    return result2


def getCoverSmall(a: str, index: int = 0) -> str:
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


def getOutline(content: str) -> str:
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


def main(number: str) -> dict:
    number = number.upper()
    query_result = get_html(
        'https://xcity.jp/result_published/?genre=%2Fresult_published%2F&q=' + number.
        replace('-', '') + '&sg=main&num=30')
    html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    urls = html.xpath("//table[contains(@class, 'resultList')]/tr[2]/td[1]/a/@href")[0]
    detail_page = get_html('https://xcity.jp' + urls)

    metadata = {
        'actor': getActor(detail_page),
        'title': getTitle(detail_page),
        'studio': getStudio(detail_page),
        'outline': getOutline(detail_page),
        'runtime': getRuntime(detail_page),
        'director': getDirector(detail_page),
        'release': getRelease(detail_page),
        'number': getID(detail_page),
        'cover': getCover(detail_page),
        'cover_small': '',
        'images': getImages(detail_page),
        'tags': getTags(detail_page),
        'label': getLabel(detail_page),
        'actor_photo': getActorPhoto(getActor(detail_page)),
        'website': 'https://xcity.jp' + urls,
        'source': 'xcity',
        'series': getSeries(detail_page),
    }
    return metadata


if __name__ == '__main__':
    print(main('VNDS-2624'))
