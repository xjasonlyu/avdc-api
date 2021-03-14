import json
from os.path import splitext
from urllib.parse import quote

from cachetools import cached, LRUCache, TTLCache

from avdc.utility.httpclient import get_html

REPO_URL = 'https://raw.githubusercontent.com/xinxin8816/gfriends/master'


@cached(cache=TTLCache(maxsize=1, ttl=600))
def _getIndex() -> dict:
    text = get_html(REPO_URL + '/Filetree.json')
    return json.loads(text)


@cached(cache=LRUCache(maxsize=100))
def search(name: str) -> list[str]:
    content = _getIndex().get('Content')

    results = []
    for studio in content:
        for img in content[studio]:
            if name == splitext(img)[0]:
                target = content[studio][img]
                results.append('/'.join([REPO_URL, 'Content', quote(studio), quote(target)]))
    return results


if __name__ == '__main__':
    # print(search('霧島レオナ'))
    # print(search('高瀬りな'))
    # print(search('橋本ありな'))
    # print(search('桜空もも'))
    # print(search('鈴木心春'))
    print(search('Rio（柚木ティナ）'))
