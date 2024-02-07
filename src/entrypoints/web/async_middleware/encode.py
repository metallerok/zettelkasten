import json
import sys

from src.entrypoints.web.errors.base import HTTPBadRequest

JSON_CONTENT_TYPE = 'application/json'
CHARSET = 'utf-8'


class EncodeMiddleware:
    @classmethod
    async def process_request(cls, req, resp):
        content_type = req.content_type or ''

        if JSON_CONTENT_TYPE in content_type:
            body = await req.stream.read(sys.maxsize).decode(CHARSET)

            try:
                req.text = json.loads(body or '{}')
            except ValueError:
                raise HTTPBadRequest(description={
                    "message": 'Not valid JSON'
                })
        else:
            req.text = json.loads('{}')

    @classmethod
    async def process_response(cls, req, resp, resource, is_success):
        if not is_success:
            return

        if isinstance(resp.text, (dict, list)):
            resp.content_type = JSON_CONTENT_TYPE
            resp.text = json.dumps(resp.text)
