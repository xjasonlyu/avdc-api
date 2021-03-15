import re
from functools import wraps
from typing import Any, Callable, Optional

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
from avdc.utility.image import (autoCropImage,
                                getRawImageByURL,
                                getRawImageFormat,
                                imageToBytes,
                                bytesToImage)
from avdc.utility.metadata import Metadata, joinMetadataCall
from avdc.utility.misc import extractID
from server import app
from server import db_operator


def extract_id(fn: Callable[[str, bool], Any]):
    @wraps(fn)
    def wrapper(_id: str):
        return fn(*extractID(_id))

    return wrapper


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


def _getRemoteMetadata(_id: str) -> Optional[Metadata]:
    for m in _getSources(_id):
        if not m.strip():
            continue
        try:
            return joinMetadataCall(*[_functions[i.strip()] for i in m.split('+')])(_id)
        except Exception as e:
            app.logger.warning(f'match metadata from {m}: {_id}: {e}')
            continue
    return


def _getLocalMetadata(_id: str) -> Optional[Metadata]:
    return db_operator.GetMetadataByID(_id)


def GetMetadataByID(_id: str) -> Optional[Metadata]:
    def valid(_m: Any) -> bool:
        return _m is not None and isinstance(_m, Metadata)

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


def GetPeopleByName(name: str) -> Optional[list[str]]:
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


def _getCoverImageByID(_id: str) -> Optional[tuple[str, bytes]]:
    result = db_operator.GetCoverByID(_id)
    if result:
        return result  # format, data

    m = GetMetadataByID(_id)
    if not m:
        return

    data = getRawImageByURL(m.cover)
    fmt = getRawImageFormat(data)
    assert fmt is not None

    db_operator.StoreCover(m.id, data, fmt)
    return fmt, data


def GetBackdropImageByID(_id: str) -> Optional[tuple[str, bytes]]:
    return _getCoverImageByID(_id)


def GetPrimaryImageByID(_id: str) -> Optional[bytes]:
    result = _getCoverImageByID(_id)
    if not result:
        return

    _, data = result
    return imageToBytes(autoCropImage(bytesToImage(data)))


if __name__ == '__main__':
    from server.database import sqlite_db_init

    sqlite_db_init('../avdc.db')

    print(GetMetadataByID('abp-233'))
    # print(GetPeopleByName('通野未帆'))
    # m = _getRemoteMetadata('abp-999')
    # models.UpdateMetadata(m)
