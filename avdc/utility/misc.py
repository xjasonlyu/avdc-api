import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional


def concurrentMap(fn, *args, timeout=None, max_workers=None):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return tuple(executor.map(fn, *args, timeout=timeout))


def extractID(_s: str) -> tuple[str, bool]:
    _s = _s.strip()
    _s = _s.split('.', maxsplit=1)[0]
    _r = re.findall(r'(.*?)([\-._]CD\d)', _s, re.IGNORECASE)
    if _r:
        _s = _r[0][0]

    if _s[-2:].upper() == '-C':
        return _s[:-2], True
    return _s, False


def extractYear(_s: str) -> Optional[int]:
    try:
        return datetime.strptime(_s, '%Y-%m-%d').year
    except (ValueError, TypeError):
        return


if __name__ == '__main__':
    print(extractID('abp-113'))
    print(extractID('abp-113.mp4'))
    print(extractID('abp-113-c-cd1.mp4'))
    print(extractID('abp-113-C.cd2.mkv'))
