from itertools import chain

from mitmproxy.http import Request, Response


def calculate_http_obj_size(http_object):
    if isinstance(http_object, (Response, Request)):
        _header_size = len(http_object.headers)
        header_size = len(b"".join(list(chain.from_iterable(http_object.headers.get_state()))))
        body_size = len(http_object.raw_content)
        url_size = len(getattr(http_object, "url", ""))
        return header_size + body_size + url_size
    else:
        return 0
