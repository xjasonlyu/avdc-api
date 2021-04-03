import json
from typing import Optional, Iterator, Any


class BaseModel:

    def __init__(self,
                 source: Optional[str] = None,
                 provider: Optional[str] = None,
                 **kwargs):
        self.sources: list[str] = kwargs.pop('sources', [])
        self.providers: list[str] = kwargs.pop('providers', [])

        if source:
            assert isinstance(source, str)
            self.sources.append(source)

        if provider:
            assert isinstance(provider, str)
            self.providers.append(provider)

    def __str__(self) -> str:
        return self.toJSON()

    def __iter__(self) -> Iterator:
        return ((k, v) for k, v in vars(self).items()
                if not k.startswith('_'))

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        for k in dict(self).keys():
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'invalid type to add: {type(other)}')

        m = {}
        for k, v in dict(other).items():
            if k in ('sources', 'providers'):
                m[k] = self.get(k) + v
            else:
                m[k] = self.get(k) or v

        return self.__class__(**m)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def toJSON(self) -> str:
        return json.dumps(
            dict(self),
            ensure_ascii=False,
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )

    def toDict(self) -> dict:
        return dict(self)
