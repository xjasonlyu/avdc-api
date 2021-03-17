import json
import re
from functools import wraps
from typing import Any, Callable, Optional

from avdc.people import gfriends
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
from avdc.utility.metadata import Metadata
from avdc.utility.misc import parseVID, concurrentMap
from server import app
from server import db_operator


def extract_vid(fn: Callable[[str, bool], Any]):
    @wraps(fn)
    def wrapper(vid: str):
        return fn(*parseVID(vid))

    return wrapper


def str_to_bool(s: str) -> bool:
    try:
        return True if json.loads(s) else False
    except json.decoder.JSONDecodeError:
        return False


_functions = {
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

_priority = 'javbus+jav321,mgstage,avsox,javdb'


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


def _getRemoteMetadata(vid: str) -> Optional[Metadata]:
    for m in _getSources(vid):
        if not m.strip():
            continue
        try:
            results = concurrentMap(lambda n: _functions[n](vid),
                                    m.split('+'), max_workers=len(m.split('+')))

            if len(results) < 2:
                return results[0]

            m = results[0]
            for result in results[1:]:
                m += result
            return m
        except Exception as e:
            app.logger.warning(f'match metadata from {m}: {vid}: {e}')
            continue
    return


def _getLocalMetadata(vid: str) -> Optional[Metadata]:
    return db_operator.GetMetadataByVID(vid)


def GetMetadataByVID(vid: str, update: bool = False) -> Optional[Metadata]:
    def valid(_m: Any) -> bool:
        return isinstance(_m, Metadata)

    if not update:  # try from database
        m = _getLocalMetadata(vid)
        if valid(m):
            return m

    m = _getRemoteMetadata(vid)
    if not valid(m):
        return

    # store to database
    db_operator.StoreMetadata(m, update=update)
    app.logger.info(f'store {m.vid} to database')
    return m


def GetPeopleByName(name: str, update: bool = False) -> Optional[list[str]]:
    if not update:
        images = db_operator.GetPeopleByName(name)
        if images:
            return images

    images = gfriends.search(name)
    if not images:
        return

    # store to database
    db_operator.StorePeople(name, images, update=update)
    app.logger.info(f'store {name} images to database')
    return images


def _getCoverImageByVID(vid: str, update: bool = False) -> Optional[tuple[str, bytes]]:
    if not update:
        result = db_operator.GetCoverByVID(vid)
        if result:
            return result  # format, data

    m = GetMetadataByVID(vid)
    if not m:
        return

    data = getRawImageByURL(m.cover)
    fmt = getRawImageFormat(data)
    assert fmt is not None

    db_operator.StoreCover(m.vid, data, fmt, update=update)
    return fmt, data


def GetBackdropImageByVID(vid: str, *args, **kwargs) -> Optional[tuple[str, bytes]]:
    return _getCoverImageByVID(vid, *args, **kwargs)


def GetPrimaryImageByVID(vid: str, *args, **kwargs) -> Optional[bytes]:
    result = _getCoverImageByVID(vid, *args, **kwargs)
    if not result:
        return

    _, data = result
    return imageToBytes(autoCropImage(bytesToImage(data)))


if __name__ == '__main__':
    # from server.database import sqlite_db_init, Metadata
    #
    # sqlite_db_init('../avdc.db')
    #
    # print(GetMetadataByVID('abp-233', update=True))
    # print(GetPeopleByName('通野未帆'))
    # print(_getRemoteMetadata('drm-003'))
    # models.UpdateMetadata(m)

    print(str_to_bool('true'))
    print(str_to_bool('True'))
    print(str_to_bool('1'))
    print(str_to_bool('0'))
    print(str_to_bool('idk'))
