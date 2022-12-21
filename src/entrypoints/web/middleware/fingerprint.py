from typing import Type
# import datetime as dt
from uuid import uuid4
from src.entrypoints.web.lib.cookies import (
    make_fingerprint_cookie,
)
from config import Config

FINGERPRINT_COOKIE_LIFETIME = {"days": 30}


class FingerprintMiddleware:
    def __init__(self, config: Type[Config]):
        self._config = config

    @classmethod
    def process_request(cls, req, resp):
        fingerprint = req.cookies.get(
            make_fingerprint_cookie()
        )

        if not fingerprint:
            fingerprint = str(uuid4())

        req.context["fingerprint"] = fingerprint

    # def process_response(self, req, resp, *args, **kwargs):
    #     fingerprint_cookie = make_fingerprint_cookie()
    #     fingerprint = req.context["fingerprint"]
    #
    #     resp.set_cookie(
    #         fingerprint_cookie,
    #         fingerprint,
    #         domain=self._config.cookie_domain,
    #         expires=dt.datetime.utcnow() + dt.timedelta(**FINGERPRINT_COOKIE_LIFETIME),
    #         max_age=dt.timedelta(**FINGERPRINT_COOKIE_LIFETIME).total_seconds(),
    #         http_only=True,
    #         secure=False,
    #     )
