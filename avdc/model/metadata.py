from typing import Any

from avdc.model import BaseModel


class Metadata(BaseModel):

    def __init__(self, **kwargs):
        # raw metadata
        self._raw: dict[str, Any] = kwargs

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
        self.actresses: list[str] = self._get('actresses', [])
        self.director: str = self._get('director', '')

        # image fields
        self.cover: str = self._get('cover', '')
        self.images: list[str] = self._get('images', [])

        super().__init__(**kwargs)

        if not self.vid:
            raise ValueError('metadata missing vid')
        if not self.title:
            raise ValueError('metadata missing title')
        if not self.cover:
            raise ValueError('metadata missing cover')

    def _get(self, key: str, default: Any = None) -> Any:
        return self._raw.get(key) or default

    def _get_runtime(self) -> int:
        try:
            return int(self._get('runtime', 0))
        except ValueError:
            return 0


def test():
    m1 = Metadata(**{'vid': '0', 'title': 't', 'cover': 'n', 'source': 'ss', 'provider': 'ab'})
    m2 = Metadata(**{'vid': '0', 'title': 't', 'cover': 'n', 'source': 'ss', 'provider': 'ab'})
    m3 = Metadata(**{'vid': '1', 'title': 't', 'cover': 'm', 'source': 'ss', 'provider': 'ab'})
    m4 = Metadata(**{'vid': '0', 'title': 'tt', 'cover': 'k', 'source': 'test', 'provider': 'abc'})
    # m5 = Metadata(**{'vid': '0', 'title': 'nn', 'cover': 'v', 'source': 'test2', 'provider': 'abcd'})

    assert m1 == m1 == m2
    assert m1 != m3 and m2 != m3
    assert m1 + m4 == m2 + m4


if __name__ == '__main__':
    test()
