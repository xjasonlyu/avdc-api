from typing import Optional

from peewee import DoesNotExist

from avdc.utility.image import getRawImageFormat
from avdc.utility.metadata import Actress as _A
from avdc.utility.metadata import Metadata as _M
from server.database import Metadata, Actress, Cover


def GetMetadataByVID(vid: str) -> Optional[_M]:
    vid = vid.upper()
    try:
        result: Metadata = Metadata.get((Metadata.vid == vid) |
                                        (Metadata.vid == vid.replace('-', '_')) |
                                        (Metadata.vid == vid.replace('_', '-')))
    except DoesNotExist:
        return
    return _M(result.__data__)


def StoreMetadata(metadata: _M, update: bool = False):
    (Metadata
     .insert(**metadata.toDict())
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())


def GetActressByName(name: str) -> Optional[_A]:
    try:
        result: Actress = Actress.get((Actress.name == name))
    except DoesNotExist:
        return
    return _A(**result.__data__)


def StoreActress(actress: _A, update: bool = False):
    (Actress
     .insert(**actress.toDict())
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())


def GetCoverByVID(vid: str) -> Optional[tuple[str, bytes]]:
    vid = vid.upper()
    try:
        result: Cover = Cover.get((Cover.vid == vid) |
                                  (Cover.vid == vid.replace('-', '_')) |
                                  (Cover.vid == vid.replace('_', '-')))
    except DoesNotExist:
        return
    return result.format, result.data


def StoreCover(vid: str, data: bytes, fmt: Optional[str] = None, update: bool = False):
    (Cover
     .insert(vid=vid,
             data=data,
             format=fmt or getRawImageFormat(data))
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())
