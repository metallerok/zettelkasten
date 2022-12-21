from typing import Optional
from functools import partial
import venusian

PREFIX = "/api/v1"


def url(url_: Optional[str] = None) -> str:
    if url_ is None:
        return PREFIX
    else:
        return f"{PREFIX}{url_}"


def resource(resource_uri: str, prefix: str = '', postfix: str = ''):
    def wrapper(cls):
        def callback(scanner, name, ob):
            url_ = prefix + resource_uri + postfix
            scanner.api.add_route(url_, cls())

        cls.__resource_uri__ = resource_uri
        venusian.attach(cls, callback)
        return cls

    return wrapper


api_resource = partial(resource, prefix=PREFIX)
