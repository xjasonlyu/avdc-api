from datetime import date, datetime
from typing import Optional, Union

from avdc.model import BaseModel


class Actress(BaseModel):

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
        _ = sign  # ignore
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
