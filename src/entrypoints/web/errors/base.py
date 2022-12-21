import logging

from falcon import (
    HTTP_400,
    HTTP_401,
    HTTP_403,
    HTTP_404,
    HTTP_408,
    HTTP_409,
    HTTP_422,
    HTTP_500,
    HTTPError,
)

logger = logging.getLogger(__name__)


def validation_error_handler(ex, req, resp, params):
    raise HTTPUnprocessableEntity(description=ex.messages)


def no_result_found_handler(ex, req, resp, params):
    raise HTTPNotFound(description=ex.args[0])


async def async_validation_error_handler(req, resp, ex, params, ws=None):
    raise HTTPUnprocessableEntity(description=ex.messages)


async def async_no_result_found_handler(req, resp, ex, params, ws=None):
    raise HTTPNotFound(description=ex.args[0])


async def async_base_exception(req, resp, ex, params, ws=None):
    logger.exception(ex)
    raise HTTP_500


class BaseHTTPError(HTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self, obj=dict):
        return {
            'error': self.description
        }


class HTTPUnauthorized(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_401, *args, **kwargs)


class HTTPUnprocessableEntity(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_422, *args, **kwargs)


class HTTPNotFound(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_404, *args, **kwargs)


class HTTPBadRequest(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_400, *args, **kwargs)


class HTTPForbidden(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_403, code=403, *args, **kwargs)


class HTTPAlreadyExists(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_409, code=409, *args, **kwargs)


class HTTPRequestTimeout(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_408, code=403, *args, **kwargs)


class HTTPInternalServerError(BaseHTTPError):
    def __init__(self, *args, **kwargs):
        super().__init__(HTTP_500, code=500, *args, **kwargs)


class HTTPWrongCredentials(HTTPBadRequest):
    code = 1111001

    def __init__(self):
        message = "Wrong credentials"

        super().__init__(
            description={
                "code": self.code,
                "message": message,
            }
        )


class HTTPFileMissing(HTTPBadRequest):
    code = 1111002

    def __init__(self):
        message = "File is missing"

        super().__init__(
            description={
                "code": self.code,
                "message": message,
            }
        )
