import json
import re

from bs4 import BeautifulSoup
from lxml import etree
from pyquery import PyQuery as pq

from provider import javbus
from utility.http import get_html

'''
API
注册：https://www.airav.wiki/api/auth/signup
设置：https://www.airav.wiki/api/get_web_settings
搜索：https://www.airav.wiki/api/video/list?lng=zh-CN&search=
搜索：https://www.airav.wiki/api/video/list?lang=zh-TW&lng=zh-TW&search=
'''
host = 'https://www.airav.wiki'


# airav 这个网站没有演员图片，所以直接使用 javbus 的图
def getActorPhoto(content: str) -> dict:  # //*[@id="star_qdt"]/li/a/img
    soup = BeautifulSoup(content, 'lxml')
    a = soup.find_all(attrs={'class': 'star-name'})
    d = {}
    for i in a:
        r = i.a['href']
        t = i.get_text()
        html = etree.fromstring(get_html(r), etree.HTMLParser())
        p = str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[1]/img/@src')).strip(" ['']")
        p2 = {t: p}
        d.update(p2)
    return d


def getTitle(content: str) -> str:  # 获取标题
    doc = pq(content)
    # h5:first-child定位第一个h5标签，妈的找了好久才找到这个语法
    title1 = str(doc('div.d-flex.videoDataBlock h5.d-none.d-md-block:nth-child(2)').text()).replace(' ', '-')
    title2 = re.sub(r'n\d+-', '', title1)
    return title1 if not title2 else title2


def getStudio(content: str) -> str:  # 获取厂商 已修改
    return javbus.getStudio(content)


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


def getActor(content: str) -> list[str]:  # 获取女优
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


def getOutline(content: str) -> str:  # 获取演员
    html = etree.fromstring(content, etree.HTMLParser())
    try:
        result = html.xpath("string(//div[@class='d-flex videoDataBlock']/div[@class='synopsis']/p)").replace('\n', '')
        return result
    except:
        return ''


def getSeries(content: str) -> str:  # 获取系列 已修改
    html = etree.fromstring(content, etree.HTMLParser())
    # 如果记录中冇导演，系列排在第6位
    if '系列:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[6]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[6]/a/text()')).strip(" ['']")
    # 如果记录中有导演，系列排在第7位
    elif '系列:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[7]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[7]/a/text()')).strip(" ['']")
    else:
        result = ''
    return result


def getTags(content: str) -> list[str]:  # 获取标签
    tag = []
    soup = BeautifulSoup(content, 'lxml')
    x = soup.find_all(attrs={'class': 'tagBtnMargin'})
    a = x[0].find_all('a')

    for i in a:
        tag.append(i.get_text())
    return tag


def getImages(content: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<div class=\"mobileImgThumbnail\">[\s\S]*?</div></div></div></div>')
    html = hr.search(content)
    if html:
        html = html.group()
        fr = re.compile(r'<img.*?src=\"(.*?)\"')
        images = fr.findall(html)
        if images:
            return images
    return []


def search(keyword: str) -> list:  # 搜索，返回结果
    result = []
    page = 1
    while page > 0:
        # search_result = {"offset": 0,"count": 4,"result": [ {"vid": "99-07-15076","slug": "Wrop6o",
        # "name": "朝ゴミ出しする近所の遊び好きノーブラ奥さん 江波りゅう", "url": "","view": 98,"img_url":
        # "https://wiki-img.airav.wiki/storage/big_pic/99-07-15076.jpg","barcode": "_1pondo_012717_472"},
        # {"vid": "99-27-00286","slug": "DlPEua","name": "放課後に、仕込んでください 〜優等生は無言でスカートを捲り上げる〜", "url": "","view": 69,
        # "img_url": "https://wiki-img.airav.wiki/storage/big_pic/99-27-00286.jpg","barcode":
        # "caribbeancom012717-360"}, {"vid": "99-07-15070","slug": "VLS3WY","name": "放課後に、仕込んでください
        # ～優等生は無言でスカートを捲り上げる～ ももき希", "url": "","view": 58,"img_url":
        # "https://wiki-img.airav.wiki/storage/big_pic/99-07-15070.jpg","barcode": "caribbeancom_012717-360"},
        # {"vid": "99-27-00287","slug": "YdMVb3","name": "朝ゴミ出しする近所の遊び好きノーブラ奥さん 江波りゅう", "url": "","view": 56,
        # "img_url": "https://wiki-img.airav.wiki/storage/big_pic/99-27-00287.jpg","barcode": "1pondo_012717_472"} ],
        # "status": "ok"}
        search_result = get_html(host + '/api/video/list?lang=zh-TW&lng=jp&search=' + keyword + '&page=' + str(page))

        try:
            json_data = json.loads(search_result)
        except json.decoder.JSONDecodeError:
            return []

        result_offset = int(json_data["offset"])
        result_count = int(json_data["count"])
        result_size = len(json_data["result"])
        if result_count <= 0 or result_size <= 0:
            return result
        elif result_count > result_offset + result_size:  # 请求下一页内容
            result.extend(json_data["result"])
            page += 1
        elif result_count == result_offset + result_size:  # 请求最后一页内容
            result.extend(json_data["result"])
            page = 0
        else:
            page = 0

    return result


def main(number: str) -> dict:
    content = get_html('https://cn.airav.wiki/video/' + number)
    javbus_content = get_html('https://www.javbus.com/ja/' + number)

    metadata = {
        # 标题可使用airav
        'title': str(re.sub(r'\w+-\d+-', '', getTitle(content))),
        # 制作商选择使用javbus
        'studio': getStudio(javbus_content),
        #  简介 使用 airav
        'outline': getOutline(content),
        # 使用javbus
        'runtime': getRuntime(javbus_content),
        # 导演 使用javbus
        'director': getDirector(javbus_content),
        # 作者 使用airav
        'actor': getActor(javbus_content),
        # 发售日使用javbus
        'release': getRelease(javbus_content),
        # 番号使用javbus
        'id': getID(javbus_content),
        # 封面链接 使用javbus
        'cover': getCover(javbus_content),
        # 剧照获取
        'images': getImages(content),
        # 使用 airav
        'tags': getTags(content),
        # 使用javbus
        'label': getSeries(javbus_content),
        # 妈的，airav不提供作者图片
        'actor_photo': getActorPhoto(javbus_content),

        'website': 'https://www.airav.wiki/video/' + number,
        'source': 'airav',
        # 使用javbus
        'series': getSeries(javbus_content),
    }
    return metadata


if __name__ == '__main__':
    print(main('ADN-188'))

    # print(search('ADN-188'))
    # print(search('012717_472'))
    # print(search('080719-976'))
    # print(search('姫川ゆうな'))
