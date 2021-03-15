from datetime import datetime
from typing import Union

from peewee import DoesNotExist

from avdc.utility.metadata import Metadata as _M
from server.database import Metadata, People


def GetMetadataByID(_id: str) -> Union[_M, None]:
    _id = _id.upper()
    try:
        results: Metadata = Metadata.get((Metadata.id == _id) |
                                         (Metadata.id == _id.replace('-', '')) |
                                         (Metadata.id == _id.replace('_', '')) |
                                         (Metadata.id == _id.replace('-', '_')) |
                                         (Metadata.id == _id.replace('_', '-')))
    except DoesNotExist:
        return None
    return _M(results.__data__)


def UpdateMetadata(metadata: _M) -> None:
    m = metadata.toDict()
    m.update(updated=datetime.now())

    (Metadata
     .update(m)
     .where(Metadata.id == metadata.id)
     .execute())


def StoreMetadata(metadata: _M) -> None:
    (Metadata
     .insert(**metadata.toDict())
     .on_conflict_ignore()
     .execute())


def GetPeopleByName(name: str) -> Union[list[str], None]:
    try:
        results: People = People.get((People.name == name))
    except DoesNotExist:
        return None
    return results.images


def StorePeople(name: str, images: list[str]) -> None:
    (People
     .insert(name=name, images=images)
     .on_conflict_ignore()
     .execute())
