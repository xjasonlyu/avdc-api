import json
from os.path import splitext
from urllib.parse import quote

from cachetools import cached, TTLCache

from avdc.utility.httpclient import get_html, Session, ResponseStream
from avdc.utility.imagesize import getSize
from avdc.utility.misc import concurrentMap

REPO_URL = 'https://raw.githubusercontent.com/xinxin8816/gfriends/master'


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def _getIndex() -> dict:
    text = get_html(REPO_URL + '/Filetree.json')
    return json.loads(text)


def getImageHeight(url: str) -> int:
    with Session() as session:
        r = session.get(url, stream=True)
        stream = ResponseStream(r.iter_content(chunk_size=64))
        return getSize(stream)[1]


def search(name: str) -> list[str]:
    content = _getIndex().get('Content')

    results = []
    for studio in content:
        for img in content[studio]:
            if name == splitext(img)[0]:
                results.append('/'.join([REPO_URL, 'Content',
                                         quote(studio), quote(content[studio][img])]))

    if results:  # auto sort by image height
        sizes = concurrentMap(getImageHeight, results, max_workers=len(results))
        results = [i for _, i in sorted(zip(sizes, results), reverse=True)]

    return results


if __name__ == '__main__':
    # print(search('霧島レオナ'))
    print(search('高瀬りな'))
    # print(search('橋本ありな'))
    # print(search('桜空もも'))
    # print(search('鈴木心春'))
