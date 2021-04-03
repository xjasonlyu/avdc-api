import json
from datetime import date, datetime
from typing import Any, Optional, Union


class BaseMetadata:

    def __init__(self,
                 source: Optional[str] = None,
                 provider: Optional[str] = None,
                 **kwargs):
        self.sources: list[str] = kwargs.get('sources', [])
        self.providers: list[str] = kwargs.get('providers', [])

        if source:
            assert isinstance(source, str)
            self.sources.append(source)

        if provider:
            assert isinstance(provider, str)
            self.providers.append(provider)

    def __str__(self) -> str:
        return self.toJSON()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        for k in self.toDict().keys():
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'invalid type to add: {type(other)}')

        m = {}
        for k, v in other.toDict().items():
            if k in ('sources', 'providers'):
                m[k] = self.get(k) + v
            else:
                m[k] = self.get(k) or v

        return self.__class__(**m)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

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


class Actress(BaseMetadata):

    def __init__(self,
                 name: str,
                 birthday: Optional[Union[str, date]] = None,
                 measurements: Optional[str] = None,
                 cup_size: Optional[str] = None,
                 av_activity: Optional[Union[str, date]] = None,
                 sign: Optional[str] = None,
                 blood_type: Optional[str] = None,
                 height: Optional[str] = None,
                 nationality: Optional[str] = None,
                 images: Optional[list[str]] = None,
                 **kwargs):
        self.name = name
        self.birthday = self.parseDate(birthday)
        self.measurements = measurements
        self.av_activity = self.parseDate(av_activity)
        self.sign = sign
        self.blood_type = blood_type
        self.height = height
        self.nationality = nationality
        self.images = images
        self.cup_size = cup_size.upper().removesuffix('CUP').strip() \
            if isinstance(cup_size, str) else None

        super().__init__(**kwargs)

    @staticmethod
    def parseDate(d: Union[str, date]) -> Optional[str]:
        if isinstance(d, date):
            return str(d)

        for fmt in ('%Y年%m月%d日', '%Y年%m月', '%Y年',
                    '%Y-%m-%d', '%Y/%m/%d',
                    '%B %d, %Y', '%B %Y', '%Y'):
            try:
                return datetime.strptime(d, fmt).strftime('%Y-%m-%d')
            except TypeError:
                break
            except ValueError:
                continue


class Metadata(BaseMetadata):

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
