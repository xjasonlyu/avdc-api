import re

from bs4 import BeautifulSoup
from lxml import etree
from pyquery import PyQuery as pq
from requests.exceptions import HTTPError

from avdc.utility.httpclient import get_html
from avdc.utility.metadata import toMetadata


def getActorPhoto(content: str) -> dict:  # //*[@id="star_qdt"]/li/a/img
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'star-name'})
    d = {}
    for i in a:
        s = i.a['href']
        t = i.get_text()
        html = etree.fromstring(get_html(s), etree.HTMLParser())
        p = str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[1]/img/@src')).strip(" ['']")
        p2 = {t: p}
        d.update(p2)
    return d


def getTitle(content: str) -> str:  # 获取标题
    doc = pq(content)
    title = str(doc('div.container h3').text()).replace(' ', '-')
    try:
        title2 = re.sub(r'n\d+-', '', title)
        return title2
    except:
        return title


def getStudio(content: str) -> str:  # 获取厂商 已修改
    html = etree.fromstring(content, etree.HTMLParser())
    # 如果记录中冇导演，厂商排在第4位
    if '製作商:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/a/text()')).strip(" ['']")
    # 如果记录中有导演，厂商排在第5位
    elif '製作商:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[5]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[5]/a/text()')).strip(" ['']")
    else:
        result = ''
    return result


def getCover(content: str) -> str:  # 获取封面链接
    doc = pq(content)
    image = doc('a.bigImage')
    return image.attr('href')


def getRelease(content: str) -> str:  # 获取出版日期
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result


def getRuntime(content: str) -> str:  # 获取分钟 已修改
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[3]/text()')).strip(" ['']分鐘")
    return result


def getStars(content: str) -> list[str]:  # 获取女优
    b = []
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'star-name'})
    for i in a:
        b.append(i.get_text())
    return b


def getID(content: str) -> str:  # 获取番号
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result


def getDirector(content: str) -> str:  # 获取导演 已修改
    html = etree.fromstring(content, etree.HTMLParser())
    if '導演:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/a/text()')).strip(" ['']")
    else:
        result = ''  # 记录中有可能没有导演数据
    return result


def getCID(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    # print(content)
    string = html.xpath("//a[contains(@class,'sample-box')][1]/@href")[0].replace(
        'https://pics.dmm.co.jp/digital/video/', '')
    result = re.sub('/.*?.jpg', '', string)
    return result


def getOverview(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    try:
        result = html.xpath("string(//div[contains(@class,'mg-b20 lh4')])").replace('\n', '')
        return result
    except:
        return ''


def getSeries(content: str) -> str:  # 获取系列 已修改
    html = etree.fromstring(content, etree.HTMLParser())
    for i in range(1, 8):
        if '系列:' == str(html.xpath(f'/html/body/div[5]/div[1]/div[2]/p[{i}]/span/text()')).strip(" ['']"):
            return str(html.xpath(f'/html/body/div[5]/div[1]/div[2]/p[{i}]/a/text()')).strip(" ['']")
    return ''


def getTags(content: str) -> list[str]:  # 获取标签
    soup = BeautifulSoup(content, 'lxml')
    result = soup.find_all(attrs={'class': 'genre'})
    return [i.get_text().strip() for i in result if 'gr_sel' in str(i)]


def getImages(content: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<div id=\"sample-waterfall\">[\s\S]*?</div></a>\s*?</div>')
    html = hr.search(content)
    if html:
        html = html.group()
        hf = re.compile(r'<a class=\"sample-box\" href=\"(.*?)\"')
        return hf.findall(html)
    return []


def search(keyword: str) -> str:
    keyword = keyword.upper()

    def extract_id(content: str):
        soup = BeautifulSoup(content, 'lxml')
        results = soup.find_all(attrs={'class': 'movie-box'})
        if not results:
            return ''

        for result in results:
            r = re.compile(r'href="https://www.javbus.com/(.*?)"')
            items = re.findall(r, str(result))
            for item in items:
                item: str = item.upper()
                if item.startswith(keyword) \
                        or item.startswith(keyword.replace('-', '')) \
                        or item.startswith(keyword.replace('_', '')) \
                        or item.startswith(keyword.replace('-', '_')) \
                        or item.startswith(keyword.replace('_', '-')):
                    return item
        return ''

    try:
        search_page = get_html('https://www.javbus.com/search/' + keyword)
    except HTTPError:
        search_page = ''
    try:
        search_page_uncensored = get_html('https://www.javbus.com/uncensored/search/' + keyword)
    except HTTPError:
        search_page_uncensored = ''

    return extract_id(search_page) or extract_id(search_page_uncensored)


# def main_uncensored(number):
#     content = get_html('https://www.javbus.com/ja/' + number)
#     if getTitle(content) == '':
#         content = get_html('https://www.javbus.com/ja/' + number.replace('-', '_'))
#
#     metadata = {
#         'title': str(re.sub(r'\w+-\d+-', '', getTitle(content))).replace(getID(content) + '-', ''),
#         'studio': getStudio(content),
#         'overview': '',
#         'runtime': getRuntime(content),
#         'director': getDirector(content),
#         'stars': getStars(content),
#         'release': getRelease(content),
#         'id': getID(content),
#         'cover': getCover(content),
#         'tags': getTags(content),
#         'images': getImages(content),
#         'label': getSeries(content),
#         'star_photos': '',
#         'website': 'https://www.javbus.com/ja/' + number,
#         'source': 'javbus',
#         'series': getSeries(content),
#     }
#     return metadata


@toMetadata
def main(number):
    _id = search(number)
    if _id:
        number = _id

    content = get_html('https://www.javbus.com/' + number)
    metadata = {
        'title': str(re.sub(r'\w+-\d+-', '', getTitle(content))),
        'studio': getStudio(content),
        'overview': '',
        'runtime': getRuntime(content),
        'director': getDirector(content),
        'stars': getStars(content),
        'release': getRelease(content),
        'id': getID(content),
        'cover': getCover(content),
        'tags': getTags(content),
        'images': getImages(content),
        'label': getSeries(content),
        'star_photos': getActorPhoto(content),
        'website': 'https://www.javbus.com/' + number,
        'source': 'javbus',
        'series': getSeries(content),
    }
    return metadata


if __name__ == "__main__":
    # print(main('ipx-292'))
    # print(main('111820-001'))
    # print(main('abp-110'))
    # print(search('god-128'))
    # print(search('111820-001'))
    print(search('drm-003'))
