from typing import Callable, Optional, Union

from requests import sessions, Response
from requests.structures import CaseInsensitiveDict

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                     '(KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'


def default_headers(user_agent: Optional[str] = None) -> CaseInsensitiveDict:
    return CaseInsensitiveDict({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                  'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Dnt': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent or DEFAULT_USER_AGENT,
    })


class Session(sessions.Session):

    def __init__(self, user_agent: Optional[str] = None):
        super(Session, self).__init__()

        # update default headers
        self.headers.update(default_headers(user_agent))


def request(method: str,
            url: str,
            user_agent: Optional[str] = None,
            raise_for_status: Union[bool, Callable[[Response], bool]] = False,
            **kwargs) -> Response:
    # By using the 'with' statement we are sure the session is closed, thus we
    # avoid leaving sockets open which can trigger a ResourceWarning in some
    # cases, and look like a memory leak in others.
    with Session(user_agent) as session:
        # do http request
        response = session.request(method=method, url=url, **kwargs)

        # status code check
        if isinstance(raise_for_status, bool) and raise_for_status \
                or callable(raise_for_status) and raise_for_status(response):
            response.raise_for_status()

        return response


def head(url: str, **kwargs) -> Response:
    return request('head', url, **kwargs)


def get(url: str, **kwargs) -> Response:
    return request('get', url, **kwargs)


def post(url: str, **kwargs) -> Response:
    return request('post', url, **kwargs)


def get_blob(url: str, **kwargs) -> bytes:
    return get(url, **kwargs).content


def get_html(url: str, **kwargs) -> str:
    return get(url, **kwargs).text


def post_html(url: str, **kwargs) -> str:
    return post(url, **kwargs).text


if __name__ == '__main__':
    print(get_html('http://httpbin.org/headers'))
