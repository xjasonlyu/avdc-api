import requests
from typing import Any

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"

session = requests.Session()


def request(url: str, method: str = 'get', data: Any = None, cookies: Any = None) -> requests.Response:
    r = session.request(
        method=method,
        url=url,
        data=data,
        cookies=cookies,
        headers={
            "User-Agent": USER_AGENT,
        },
        allow_redirects=True,
    )
    r.raise_for_status()
    return r


def get_html(url: str, *args, **kwargs) -> str:
    return request(method='get', url=url, *args, **kwargs).text


def post_html(url: str, *args, **kwargs) -> str:
    return request(method='post', url=url, *args, **kwargs).text
