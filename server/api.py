import re
from typing import Union, Any

from avdc.people import gfriends
from avdc.provider import airav
from avdc.provider import avsox
from avdc.provider import dlsite
from avdc.provider import fanza
from avdc.provider import fc2
from avdc.provider import jav321
from avdc.provider import javbus
from avdc.provider import javdb
from avdc.provider import javlib
from avdc.provider import mgstage
from avdc.provider import xcity
from avdc.utility.image import autoCropImage, getImageByURL, imageToBytes
from avdc.utility.metadata import Metadata, joinMetadataCall
from server import app
from server import db_operator

_functions = {
    'airav': airav.main,
    'avsox': avsox.main,
    'fanza': fanza.main,
    'fc2': fc2.main,
    'javdb': javdb.main,
    'javbus': javbus.main,
    'mgstage': mgstage.main,
    'jav321': jav321.main,
    'xcity': xcity.main,
    'javlib': javlib.main,
    'dlsite': dlsite.main,
}

_priority = 'javbus+jav321,mgstage,avsox,javdb,fanza,xcity,javlib,fc2'


def _getSources(keyword: str) -> list[str]:
    sources = _priority.split(',')  # default priority

    if "avsox" in sources and (re.match(r"^\d{5,}", keyword) or
                               "HEYZO" in keyword.upper()):
        sources.insert(0, sources.pop(sources.index("avsox")))

    elif "mgstage" in sources and (re.match(r"\d+\D+", keyword) or
                                   "SIRO" in keyword.upper()):
        sources.insert(0, sources.pop(sources.index("mgstage")))

    elif "fc2" in sources and "FC2" in keyword.upper():
        sources.insert(0, sources.pop(sources.index("fc2")))

    elif "dlsite" in sources and "RJ" in keyword.upper():
        sources.insert(0, sources.pop(sources.index("dlsite")))

    return sources


def _getRemoteMetadata(_id: str) -> Union[Metadata, None]:
    for m in _getSources(_id):
        if not m.strip():
            continue
        try:
            return joinMetadataCall(*[_functions[i.strip()] for i in m.split('+')])(_id)
        except Exception as e:
            app.logger.warning(f'match metadata from {m}: {_id}: {e}')
            continue
    return


def _getLocalMetadata(_id: str) -> Union[Metadata, None]:
    return db_operator.GetMetadataByID(_id)


def GetMetadataByID(_id: str) -> Union[Metadata, None]:
    def valid(_m: Any) -> bool:
        return _m is not None and isinstance(_m, Metadata)

    def process(_s: str) -> str:
        _s = _s.strip()
        _s = _s.split('.', maxsplit=1)[0]
        _r = re.findall(r'(.*?)([\-._]CD\d)', _s, re.IGNORECASE)
        if _r:
            _s = _r[0][0]
        _s = _s.replace('-c', '').replace('-C', '')
        return _s

    _id = process(_id)

    m = _getLocalMetadata(_id)
    if valid(m):
        return m

    m = _getRemoteMetadata(_id)
    if not valid(m):
        return

    # store to database
    db_operator.StoreMetadata(m)
    app.logger.info(f'store {m.id} to database')
    return m


def GetPeopleByName(name: str) -> Union[list[str], None]:
    images = db_operator.GetPeopleByName(name)
    if images:
        return images

    images = gfriends.search(name)
    if not images:
        return

    # store to database
    db_operator.StorePeople(name, images)
    app.logger.info(f'store {name} images to database')
    return images


def GetImageByID(_id: str) -> Union[bytes, None]:
    m = GetMetadataByID(_id)
    if m and m.cover:
        return imageToBytes(
            autoCropImage(
                getImageByURL(
                    m.cover)))
    return


if __name__ == '__main__':
    from server.database import sqlite_db_init

    sqlite_db_init('../avdc.db')

    print(GetMetadataByID('abp-233'))
    # print(GetPeopleByName('通野未帆'))
    # m = _getRemoteMetadata('abp-999')
    # models.UpdateMetadata(m)
