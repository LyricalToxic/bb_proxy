from mitmproxy.http import Request, Response


def calculate_http_obj_size(http_object):
    if isinstance(http_object, (Response, Request)):
        header_size = len(http_object.headers)
        body_size = len(http_object.raw_content)
        url_size = len(getattr(http_object, "url", ""))
        return header_size + body_size + url_size
    else:
        return 0
