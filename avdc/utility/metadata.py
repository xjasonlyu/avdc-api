import json
from collections import Iterable
from typing import Any, Callable, Union

from requests.exceptions import RequestException
from retrying import retry


class MetadataError(Exception):
    pass


class Metadata:

    def __init__(self, *raws: Any):
        self.id = self._get_id(raws)

        # raw metadata
        self._raws: tuple[Any] = raws

        # required fields
        self.title: str = self._get('title', '')

        if not self.id:
            raise MetadataError('metadata missing id')
        if not self.title:
            raise MetadataError('metadata missing title')

        # info fields
        self.overview: str = self._get('overview', '')
        self.release: str = str(self._get('release', ''))
        self.runtime: int = int(self._get('runtime', 0))
        self.label: str = self._get('label', '')
        self.studio: str = self._get('studio', '')
        self.series: str = self._get('series', '')
        self.tags: list[str] = self._get('tags', [])

        # cast fields
        self.stars: list[str] = self._get('stars', [])
        self.director: str = self._get('director', '')

        # image fields
        self.cover: str = self._get('cover', '')
        self.small_cover: str = self._get('small_cover', '')
        self.images: list[str] = self._get('images', [])
        # self.star_photos: dict[str, str] = self._get('star_photos', {})

        # source fields
        self.source: list[str] = self._get_list('source')
        self.website: list[str] = self._get_list('website')

    def __eq__(self, m) -> bool:
        if not isinstance(m, Metadata):
            return False
        for k in vars(self).keys():
            if getattr(self, k) != getattr(m, k):
                return False
        return True

    def __str__(self) -> str:
        return self.toJSON()

    @staticmethod
    def _get_id(raws: Any):
        if not raws:
            raise MetadataError('empty raw metadata')

        _id: Union[str, None] = None
        for r in raws:
            i: str = r.get('id', '').upper().strip()
            i = i.replace('_', '-')

            if _id is None:
                _id = i

            if _id == i:
                continue

            x = i.replace('-', '').replace('_', '')
            y = _id.replace('-', '').replace('_', '')

            if x == y \
                    or x in y \
                    or y in x:
                continue

            try:
                o, p = i.split('-', maxsplit=1)
                m, n = _id.split('-', maxsplit=1)
                if m == o and int(n) == int(p):
                    continue
            except:
                pass

            raise MetadataError(f'mismatched id: {_id} != {i}')

        for r in raws:
            i: str = r.get('id', '').upper().strip()
            if '-' in i or '_' in i:
                return i  # prefer `-` in id
        return raws[0].get('id', '').upper().strip()

    def _get(self, key: str, default: Any = None) -> Any:
        for r in self._raws:
            value = r.get(key)
            if not value:
                continue
            return value
        else:
            return default

    def _get_list(self, key: str) -> list[str]:
        results = []
        for r in self._raws:
            value = r.get(key)
            if not value:
                continue
            if isinstance(value, str):
                results.append(value)
            elif isinstance(value, Iterable):
                results.extend(value)
        return results

    def get(self, key: str, default: Any = None) -> Any:
        if not hasattr(self, key):
            return default
        return getattr(self, key)

    def toJSON(self) -> str:
        return json.dumps(
            self.toDict(),
            ensure_ascii=False,
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )

    def toDict(self) -> dict:
        return {k: v for k, v in vars(self).items()
                if not k.startswith('_')}


def joinMetadataCall(*functions: Callable[[str], Metadata]) -> Callable[[str], Metadata]:
    def wrapper(v: str) -> Metadata:
        ml: list[Metadata] = []
        for fn in functions:
            try:
                m = fn(v)
            except:  # ignore all
                pass
            else:
                ml.append(m)
        return Metadata(*ml)

    return wrapper


def toMetadata(fn: Callable[[str], dict[str, Any]]) -> Callable[[str], Metadata]:
    @retry(stop_max_attempt_number=3, retry_on_exception=lambda e: isinstance(e, RequestException))
    def wrapper(s: str) -> Metadata:
        return Metadata(fn(s))

    return wrapper


if __name__ == '__main__':
    m1 = Metadata({'id': '0', 'title': 't', 'cover': 'n', 'source': 'ss'})
    m2 = Metadata({'id': '0', 'title': 't', 'cover': 'n', 'source': 'ss'})
    m3 = Metadata({'id': '1', 'title': 't', 'cover': 'm', 'source': 'ss'})
    m4 = Metadata({'id': '0', 'title': 'tt', 'source': 'test', 'website': 'http'})

    assert (m1 == m1 == m2)
    assert (m1 != m3 and m2 != m3)

    print(Metadata(m1, m4))
