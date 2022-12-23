import typing
import json
from typing import List, Dict
from src.entrypoints.web.errors.base import HTTPUnprocessableEntity
from src.lib.pagination import PaginationABC
from marshmallow import Schema, fields


def pagination_dump(items: List, pagination: PaginationABC) -> Dict:
    return {
        "data": items,
        "meta": {
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": pagination.total_pages
        }
    }


class BasePaginationSchema(Schema):
    page = fields.Integer(default=1, allow_none=False, missing=1)
    page_size = fields.Integer(default=20, allow_none=False, missing=20)


class JSON(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if type(value) in [dict, list]:
            try:
                json.dumps(value)
            except ValueError:
                raise HTTPUnprocessableEntity(
                    description={
                        attr: [{
                            "value": "Invalid json",
                        }],
                    }
                )
            return value

        if value:
            try:
                return json.loads(value)
            except ValueError:
                return None

        return None

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value:
            if type(value) in [dict, list]:
                try:
                    json.dumps(value)
                    return value
                except ValueError:
                    raise HTTPUnprocessableEntity(
                        description={
                            attr: [{
                                "value": "Invalid json",
                            }],
                        }
                    )

        return None
