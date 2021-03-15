from datetime import datetime
from typing import Optional

from peewee import DoesNotExist

from avdc.utility.image import getRawImageFormat
from avdc.utility.metadata import Metadata as _M
from server.database import Metadata, People, Cover


def GetMetadataByID(_id: str) -> Optional[_M]:
    _id = _id.upper()
    try:
        result: Metadata = Metadata.get((Metadata.id == _id) |
                                        (Metadata.id == _id.replace('-', '_')) |
                                        (Metadata.id == _id.replace('_', '-')))
    except DoesNotExist:
        return
    return _M(result.__data__)


def UpdateMetadata(metadata: _M):
    m = metadata.toDict()
    m.update(updated=datetime.now())

    (Metadata
     .update(m)
     .where(Metadata.id == metadata.id)
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


def GetCoverByID(_id: str) -> Optional[tuple[str, bytes]]:
    _id = _id.upper()
    try:
        result: Cover = Cover.get((Cover.id == _id) |
                                  (Cover.id == _id.replace('-', '_')) |
                                  (Cover.id == _id.replace('_', '-')))
    except DoesNotExist:
        return
    return result.format, result.data


def StoreCover(_id: str, data: bytes, fmt: Optional[str] = None):
    (Cover
     .insert(id=_id,
             data=data,
             format=fmt or getRawImageFormat(data))
     .on_conflict_ignore()
     .execute())
