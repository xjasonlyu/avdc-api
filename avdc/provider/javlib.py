import re
from http.cookies import SimpleCookie

import bs4
import cloudscraper
from bs4 import BeautifulSoup
from lxml import html

from avdc.model.metadata import Metadata
from avdc.utility.httpclient import request


def get_from_xpath(lx: html.HtmlElement, xpath: str) -> str:
    return lx.xpath(xpath)[0].strip()


def get_table_el_single_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tag = soup.find(id=tag_id).find("a")

    if tag is not None:
        return tag.string.strip()
    else:
        return ""


def get_table_el_multi_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("a")

    return process(tags)


def get_table_el_td(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("td", class_="text")

    return process(tags)


def process(tags: bs4.element.ResultSet) -> str:
    values = []
    for tag in tags:
        value = tag.string
        if value is not None and value != "----":
            values.append(value)

    return ",".join(x for x in values if x)


def get_title(lx: html.HtmlElement, soup: BeautifulSoup) -> str:
    title = get_from_xpath(lx, '//*[@id="video_title"]/h3/a/text()')
    number = get_table_el_td(soup, "video_id")

    return title.replace(number, "").strip()


def getCover(lx: html.HtmlComment) -> str:
    return "http:{}".format(get_from_xpath(lx, '//*[@id="video_jacket_img"]/@src'))


def get_javlib_cookie() -> tuple[str, str]:
    return cloudscraper.get_cookie_string("http://www.m45e.com/")


def main(keyword: str) -> Metadata:
    raw_cookies, user_agent = get_javlib_cookie()

    # Blank cookies mean javlib site return error
    if not raw_cookies:
        raise Exception('javlib: get blank cookie')

    # Manually construct a dictionary
    s_cookie = SimpleCookie()
    s_cookie.load(raw_cookies)
    cookies = {}
    for key, morsel in s_cookie.items():
        cookies[key] = morsel.value

    # Scraping
    result = request(
        method='get',
        url='http://www.javlibrary.com/cn/vl_searchbyid.php?keyword={}'.format(keyword),
        cookies=cookies,
        user_agent=user_agent,
    )
    soup = BeautifulSoup(result.text, 'html.parser')
    lx = html.fromstring(str(soup))

    fanhao_pather = re.compile(r'<a href=".*?".*?><div class="id">(.*?)</div>')
    fanhao = fanhao_pather.findall(result.text)

    metadata = {}
    if '/?v=jav' in result.url:
        metadata = {
            'title': get_title(lx, soup),
            'studio': get_table_el_single_anchor(soup, 'video_maker'),
            # 'year': get_table_el_td(soup, 'video_date')[:4],
            'overview': '',
            'director': get_table_el_single_anchor(soup, 'video_director'),
            'cover': getCover(lx),
            'star_photos': '',
            'source': result.url,
            'provider': 'javlib',
            'actresses': get_table_el_multi_anchor(soup, 'video_cast').split(','),
            'label': get_table_el_td(soup, 'video_label'),
            'genres': get_table_el_multi_anchor(soup, 'video_genres').split(','),
            'vid': get_table_el_td(soup, 'video_id'),
            'release': get_table_el_td(soup, 'video_date'),
            'runtime': get_from_xpath(lx, '//*[@id="video_length"]/table/tr/td[2]/span/text()'),
            'series': '',
        }
    elif keyword.upper() in fanhao:
        url_pather = re.compile(r'<a href="(.*?)".*?><div class="id">(.*?)</div>')
        s = {}
        url_list = url_pather.findall(result.text)
        for url in url_list:
            s[url[1]] = 'http://www.javlibrary.com/cn/' + url[0].lstrip('.')
        av_url = s[keyword.upper()]
        result = request(
            method='get',
            url=av_url,
            cookies=cookies,
        )
        soup = BeautifulSoup(result.text, 'html.parser')
        lx = html.fromstring(str(soup))

        metadata = {
            'title': get_title(lx, soup),
            'studio': get_table_el_single_anchor(soup, 'video_maker'),
            # 'year': get_table_el_td(soup, 'video_date')[:4],
            'overview': '',
            'director': get_table_el_single_anchor(soup, 'video_director'),
            'cover': getCover(lx),
            # 'star_photos': '',
            'source': result.url,
            'provider': 'javlib',
            'actresses': get_table_el_multi_anchor(soup, 'video_cast').split(','),
            'label': get_table_el_td(soup, 'video_label'),
            'genres': get_table_el_multi_anchor(soup, 'video_genres').split(','),
            'vid': get_table_el_td(soup, 'video_id'),
            'release': get_table_el_td(soup, 'video_date'),
            'runtime': get_from_xpath(lx, '//*[@id="video_length"]/table/tr/td[2]/span/text()'),
            'series': '',
        }

    return Metadata(**metadata)


if __name__ == '__main__':
    lists = ['DVMC-003', 'MIAE-003', 'JKREZ-001', 'KMHRS-010', 'KNSD-023']
    # lists = ['DVMC-003']
    for num in lists:
        print(main(num))
