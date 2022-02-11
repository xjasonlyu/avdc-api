import re

from lxml import etree

from avdc.model.metadata import Metadata
from avdc.utility.httpclient import get_html


def getTitle(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath("/html/body/section/div/h2/strong/text()")[0]
    return result


def getActresses(a: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//strong[contains(text(),"演員")]/../span/text()')
    result2 = html.xpath('//strong[contains(text(),"演員")]/../span/a/text()')
    # actresses = str(result1 + result2).strip('+').replace(",\\xa0", "").replace("'", ""). \
    #     replace(' ', '').replace(',,', '').replace('N/A', '').lstrip(',').replace(',', ', ')
    return [i.replace('N/A', '').strip('+').strip() for i in result1 + result2
            if i.replace('N/A', '').strip('+').strip()]


def getOnePhoto(url: str) -> str:
    html_page = get_html(url)
    ir = re.compile(r'<span class=\"avatar\" style=\"background-image: url\((.*?)\)')
    img_url = ir.findall(html_page)
    if img_url:
        return img_url[0]
    else:
        return ''


def getActressPhoto(html: str) -> dict:  # //*[@id="star_qdt"]/li/a/img
    r = re.compile(r'<strong>演員:</strong>\s*?.*?<span class=\"value\">(.*)\s*?</div>')
    results = r.findall(html)

    if results:
        item = results[0]
        ar = re.compile(r'<a href=\"(.*?)\">(.*?)</a>')
        actresses = ar.findall(item)
        star_photos = {}
        for i in actresses:
            star_photos[i[1]] = getOnePhoto('https://javdb.com' + i[0])
        return star_photos
    else:
        return {}


def getStudio(a: str) -> str:
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"片商")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"片商")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
    patherr = re.compile(r'<strong>片商:</strong>[\s\S]*?<a href=\".*?>(.*?)</a></span>')
    pianshang = patherr.findall(a)
    if pianshang:
        result = pianshang[0]
    else:
        result = ""
    return result


def getRuntime(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi').rstrip('分鍾').strip()


def getLabel(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getVID(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//strong[contains(text(),"番號")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"番號")]/../span/a/text()')).strip(" ['']")
    return str(result2 + result1).strip('+')


def getRelease(a: str) -> str:
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"時間")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"時間")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+')
    patherr = re.compile(r'<strong>日期:</strong>\s*?.*?<span class="value">(.*?)</span>')
    dates = patherr.findall(a)
    if dates:
        result = dates[0]
    else:
        result = ''
    return result


def getGenres(a: str) -> list[str]:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        return html.xpath('//strong[contains(text(),"類別")]/../span/a/text()')
    except:
        return html.xpath('//strong[contains(text(),"類別")]/../span/text()')


def getSmallCover(a: str, index: int = 0) -> str:
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the first one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if 'https' not in result:
            result = 'https:' + result
        return result
    except:  # 2020.7.17 Repair Cover Url crawl
        try:
            result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
            if 'https' not in result:
                result = 'https:' + result
            return result
        except:
            result = html.xpath("//div[@class='item-image']/img/@data-src")[index]
            if 'https' not in result:
                result = 'https:' + result
            return result


def getImages(text: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<div class=\"tile-images preview-images\">[\s\S]*?</a>\s+?</div>\s+?</div>')
    html = hr.search(text)
    if html:
        html = html.group()
        hf = re.compile(r'<a class="tile-item" href=\"(.*?)\"')
        return [i.strip() for i in hf.findall(html) if i.startswith('http')]
    return []


def getCover(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    try:
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/a/img/@src")[0]
    except:  # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/img/@src")[0]
    return result


def getDirector(a: str) -> str:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"導演")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"導演")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getOverview(text: str) -> str:
    html = etree.fromstring(text, etree.HTMLParser())
    result = str(html.xpath('//*[@id="introduction"]/dd/p[1]/text()')).strip(" ['']")
    return result


def getSeries(a: str) -> str:
    # /html/body/section/div/div[3]/div[2]/nav/div[7]/span/a
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def main(keyword: str) -> Metadata:
    keyword = keyword.upper()
    query_result = get_html('https://javdb.com/search?q=' + keyword + '&f=all')

    html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # javdb sometime returns multiple results,
    # and the first elememt maybe not the one we are looking for
    # iterate all candidates and find the match one
    urls = html.xpath('//*[@id="videos"]/div/div/a/@href')
    # 记录一下欧美的ids  ['Blacked','Blacked']
    if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', keyword):
        ids = [keyword]
        correct_url = urls[0]
    else:
        ids = html.xpath('//*[@id="videos"]/div/div/a/div[contains(@class, "uid")]/text()')
        correct_url = urls[ids.index(keyword)]

    detail_page = get_html('https://javdb.com' + correct_url, params={'locale': 'zh'})

    # no cut image by default
    # If gray image exists ,then replace with normal cover
    # if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', keyword):
    #     small_cover = getSmallCover(query_result)
    # else:
    #     small_cover = getSmallCover(query_result, index=ids.index(keyword))
    # if 'placeholder' in small_cover:
    #     # replace wit normal cover and cut it
    #     small_cover = getCover(detail_page)

    vid = getVID(detail_page)
    title = getTitle(detail_page)
    if title and vid:
        # remove duplicate title
        title = title.replace(vid, '').strip()

    return Metadata(**{
        'actresses': getActresses(detail_page),
        'title': title,
        'studio': getStudio(detail_page),
        'overview': getOverview(detail_page),
        'runtime': getRuntime(detail_page),
        'director': getDirector(detail_page),
        'release': getRelease(detail_page),
        'vid': vid,
        'cover': getCover(detail_page),
        # 'small_cover': small_cover,
        'images': getImages(detail_page),
        'genres': getGenres(detail_page),
        'label': getLabel(detail_page),
        # 'star_photos': getActressPhoto(detail_page),
        'source': 'https://javdb.com' + correct_url,
        'provider': 'javdb',
        'series': getSeries(detail_page),
    })


if __name__ == "__main__":
    # print(main('blacked.20.05.30'))
    # print(main('AGAV-042'))
    # print(main('BANK-022'))
    # print(main('MIAE-003'))
    # print(main('ABW-065'))
    print(main('021022_001'))
