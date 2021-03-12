from bs4 import BeautifulSoup
from lxml import etree

from utility.http import get_html


def getActorPhoto(content: str) -> dict:  # //*[@id="star_qdt"]/li/a/img
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'avatar-box'})
    d = {}
    for i in a:
        s = i.img['src']
        t = i.span.get_text()
        p2 = {t: s}
        d.update(p2)
    return d


def getTitle(content: str) -> str:
    try:
        html = etree.fromstring(content, etree.HTMLParser())
        result = str(html.xpath('/html/body/div[2]/h3/text()')).strip(" ['']")  # [0]
        return result.replace('/', '')
    except:
        return ''


def getActor(content: str) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'avatar-box'})
    d = []
    for i in a:
        d.append(i.span.get_text())
    return d


def getStudio(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = str(html.xpath('//p[contains(text(),"制作商: ")]/following-sibling::p[1]/a/text()')).strip(" ['']").replace(
        "', '", ' ')
    return result


def getRuntime(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = str(html.xpath('//span[contains(text(),"长度:")]/../text()')).strip(" ['分钟']")
    return result


def getLabel(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = str(html.xpath('//p[contains(text(),"系列:")]/following-sibling::p[1]/a/text()')).strip(" ['']")
    return result


def getID(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = str(html.xpath('//span[contains(text(),"识别码:")]/../span[2]/text()')).strip(" ['']")
    return result


def getRelease(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = str(html.xpath('//span[contains(text(),"发行时间:")]/../text()')).strip(" ['']")
    return result


def getCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[2]/div[1]/div[1]/a/img/@src')).strip(" ['']")
    return result


def getCoverSmall(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('//*[@id="waterfall"]/div/a/div[1]/img/@src')).strip(" ['']")
    return result


def getTags(content: str) -> list[str]:
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'genre'})
    d = []
    for i in a:
        d.append(i.get_text())
    return d


def getSeries(content: str) -> str:
    try:
        html = etree.fromstring(content, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        result = str(html.xpath('//span[contains(text(),"系列:")]/../span[2]/text()')).strip(" ['']")
        return result
    except:
        return ''


def main(number: str) -> dict:
    html = get_html('https://tellme.pw/avsox')
    site = etree.HTML(html).xpath('//div[@class="container"]/div/a/@href')[0]
    a = get_html(site + '/cn/search/' + number)
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = str(html.xpath('//*[@id="waterfall"]/div/a/@href')).strip(" ['']")
    if result == '' or result == 'null' or result == 'None':
        a = get_html(site + '/cn/search/' + number.replace('-', '_'))
        html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        result = str(html.xpath('//*[@id="waterfall"]/div/a/@href')).strip(" ['']")
        if result == '' or result == 'null' or result == 'None':
            a = get_html(site + '/cn/search/' + number.replace('_', ''))
            html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
            result = str(html.xpath('//*[@id="waterfall"]/div/a/@href')).strip(" ['']")
    web = get_html(result)
    soup = BeautifulSoup(web, 'lxml')
    info = str(soup.find(attrs={'class': 'row movie'}))

    metadata = {
        'actor': getActor(web),
        'title': getTitle(web).strip(getID(web)),
        'studio': getStudio(info),
        'outline': '',  #
        'runtime': getRuntime(info),
        'director': '',  #
        'release': getRelease(info),
        'id': getID(info),
        'cover': getCover(web),
        'cover_small': getCoverSmall(a),
        'tags': getTags(web),
        'label': getLabel(info),
        'actor_photo': getActorPhoto(web),
        'website': result,
        'source': 'avsox',
        'series': getSeries(info),
    }
    return metadata


if __name__ == "__main__":
    print(main('012717_472'))
