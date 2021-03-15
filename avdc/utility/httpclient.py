from typing import Any

import requests

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"


def request(method: str,
            url: str,
            data: Any = None,
            cookies: Any = None,
            user_agent: Any = None,
            ) -> requests.Response:
    r = requests.request(
        method=method,
        url=url,
        data=data,
        cookies=cookies,
        headers={
            "User-Agent": user_agent or USER_AGENT,
        },
        allow_redirects=True,
    )
    r.raise_for_status()
    return r


def get_blob(url: str, *args, **kwargs) -> bytes:
    return request(method='get', url=url, *args, **kwargs).content


def get_html(url: str, *args, **kwargs) -> str:
    return request(method='get', url=url, *args, **kwargs).text


def post_html(url: str, *args, **kwargs) -> str:
    return request(method='post', url=url, *args, **kwargs).text


if __name__ == '__main__':
    print(get_html('http://www.bing.com'))
