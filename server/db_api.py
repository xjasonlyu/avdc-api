from typing import Optional

from peewee import DoesNotExist

from avdc.utility.image import getRawImageFormat
from avdc.utility.metadata import Actress as _A
from avdc.utility.metadata import Metadata as _M
from server.database import Metadata, Actresses, Covers


def GetMetadataByVID(vid: str) -> Optional[_M]:
    vid = vid.upper()
    try:
        result: Metadata = Metadata.get((Metadata.vid == vid) |
                                        (Metadata.vid == vid.replace('-', '_')) |
                                        (Metadata.vid == vid.replace('_', '-')))
    except DoesNotExist:
        return
    return _M(**result.__data__)


def StoreMetadata(metadata: _M, update: bool = False):
    (Metadata
     .insert(**dict(metadata))
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())


def GetActressByName(name: str) -> Optional[_A]:
    try:
        result: Actresses = Actresses.get((Actresses.name == name))
    except DoesNotExist:
        return
    return _A(**result.__data__)


def StoreActress(actress: _A, update: bool = False):
    (Actresses
     .insert(**dict(actress))
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())


def GetCoverByVID(vid: str) -> Optional[tuple[str, bytes, float]]:
    vid = vid.upper()
    try:
        result: Covers = Covers.get((Covers.vid == vid) |
                                    (Covers.vid == vid.replace('-', '_')) |
                                    (Covers.vid == vid.replace('_', '-')))
    except DoesNotExist:
        return
    return result.format, result.data, result.pos


def StoreCover(vid: str, data: bytes, fmt: Optional[str] = None, pos: float = -1, update: bool = False):
    (Covers
     .insert(vid=vid,
             data=data,
             format=fmt or getRawImageFormat(data),
             pos=pos)
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())
