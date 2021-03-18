from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any, Union


class MetadataError(Exception):
    pass


class Metadata:

    def __init__(self, raw: dict[str, Any]):
        # raw metadata
        self._raw: dict[str, Any] = raw

        # required fields
        self.vid: str = self._get('vid', '').strip().upper()
        self.title: str = self._get('title', '')

        # info fields
        self.overview: str = self._get('overview', '')
        self.release: str = str(self._get('release', ''))
        self.runtime: int = self._get_runtime()
        self.label: str = self._get('label', '')
        self.studio: str = self._get('studio', '')
        self.series: str = self._get('series', '')
        self.genres: list[str] = self._get('genres', [])

        # cast fields
        self.stars: list[str] = self._get('stars', [])
        self.director: str = self._get('director', '')

        # image fields
        self.cover: str = self._get('cover', '')
        self.images: list[str] = self._get('images', [])

        # source fields
        self.source: list[str] = self._to_list(self._get('source'))
        self.website: list[str] = self._to_list(self._get('website'))

        if not self.vid:
            raise MetadataError('metadata missing vid')
        if not self.title:
            raise MetadataError('metadata missing title')
        if not self.cover:
            raise MetadataError('metadata missing cover')

    def __eq__(self, m) -> bool:
        if not isinstance(m, Metadata):
            return False
        for k in vars(self).keys():
            if getattr(self, k) != getattr(m, k):
                return False
        return True

    def __str__(self) -> str:
        return self.toJSON()

    def __add__(self, other: Metadata) -> Metadata:
        if not isinstance(other, Metadata):
            raise TypeError(f'invalid type to add: {type(other)}')

        m = {}
        for k, v in other.toDict().items():
            if k in ('source', 'website'):
                m[k] = self.get(k) + v
            else:
                m[k] = self.get(k) or v

        return Metadata(m)

    @staticmethod
    def _to_list(v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str):
            return [v]
        elif isinstance(v, Iterable):
            return [i for i in v]
        else:
            return []

    def _get(self, key: str, default: Any = None) -> Any:
        return self._raw.get(key) or default

    def _get_runtime(self) -> int:
        try:
            return int(self._get('runtime'))
        except ValueError:
            return 0

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


def test():
    m1 = Metadata({'vid': '0', 'title': 't', 'cover': 'n', 'source': 'ss'})
    m2 = Metadata({'vid': '0', 'title': 't', 'cover': 'n', 'source': 'ss'})
    m3 = Metadata({'vid': '1', 'title': 't', 'cover': 'm', 'source': 'ss'})
    m4 = Metadata({'vid': '0', 'title': 'tt', 'source': 'test', 'website': 'http'})

    assert m1 == m1 == m2
    assert m1 != m3 and m2 != m3
    assert m1 + m4 == m2 + m4


if __name__ == '__main__':
    test()
