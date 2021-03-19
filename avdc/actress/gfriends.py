import json
from os.path import splitext
from urllib.parse import quote

from cachetools import cached, TTLCache

from avdc.utility.httpclient import get_html, Session, ResponseStream
from avdc.utility.imagesize import getSize
from avdc.utility.misc import concurrentMap

REPO = 'xinxin8816/gfriends'

REPO_RAW_URL = f'https://raw.githubusercontent.com/{REPO}/master'


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def _getIndex() -> dict:
    url = f'{REPO_RAW_URL}/Filetree.json'
    return json.loads(get_html(url, raise_for_status=True))


def getImageSize(url: str) -> tuple[int, int]:
    with Session() as session:
        r = session.get(url, stream=True)
        stream = ResponseStream(r.iter_content(chunk_size=64))
        return getSize(stream)  # width, height


def search(name: str) -> list[str]:
    content: dict[str, dict[str, str]] = _getIndex().get('Content')

    result_set = set()
    for company in content.keys():
        for img in content[company]:
            if name == splitext(img)[0]:
                result_set.add('/'.join([REPO_RAW_URL, 'Content',
                                         quote(company), quote(content[company][img])]))

    results = list(result_set)
    if results:  # auto sort by height and width
        sizes = concurrentMap(getImageSize, results, max_workers=len(results))
        results = [i for _, i in sorted(zip(sizes, results),
                                        key=lambda x: (x[0][1], x[0][0]), reverse=True)]
    return results


if __name__ == '__main__':
    # print(search('霧島レオナ'))
    # print(search('高瀬りな'))
    # print(search('橋本ありな'))
    # print(search('桜空もも'))
    # print(search('鈴木心春'))
    # print(search('三原ほのか'))
    print(search('詩音乃らん'))
