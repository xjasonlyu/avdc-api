from datetime import datetime
from typing import Optional

from peewee import DoesNotExist

from avdc.utility.image import getRawImageFormat
from avdc.utility.metadata import Metadata as _M
from server.database import Metadata, People, Cover


def GetMetadataByVID(vid: str) -> Optional[_M]:
    vid = vid.upper()
    try:
        result: Metadata = Metadata.get((Metadata.vid == vid) |
                                        (Metadata.vid == vid.replace('-', '_')) |
                                        (Metadata.vid == vid.replace('_', '-')))
    except DoesNotExist:
        return
    return _M(result.__data__)


def UpdateMetadata(metadata: _M):
    m = metadata.toDict()
    m.update(updated=datetime.now())

    (Metadata
     .update(m)
     .where(Metadata.vid == metadata.vid)
     .execute())


def StoreMetadata(metadata: _M):
    (Metadata
     .insert(**metadata.toDict())
     .on_conflict_ignore()
     .execute())


def GetPeopleByName(name: str) -> Optional[list[str]]:
    try:
        results: People = People.get((People.name == name))
    except DoesNotExist:
        return
    return results.images


def StorePeople(name: str, images: list[str]):
    (People
     .insert(name=name, images=images)
     .on_conflict_ignore()
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


def StoreCover(vid: str, data: bytes, fmt: Optional[str] = None):
    (Cover
     .insert(vid=vid,
             data=data,
             format=fmt or getRawImageFormat(data))
     .on_conflict_ignore()
     .execute())
