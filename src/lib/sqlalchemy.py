from sqlalchemy.orm import Query
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum


def filters(model, query=None, **params) -> Query:
    query = query or model.query

    filter_field = getattr(model, model.filter_field, None) if model.filter_field is not None \
        else getattr(model, 'name', None)

    if filter_field is not None:
        if model.desc:
            query = query.order_by(filter_field.desc())
        else:
            query = query.order_by(filter_field)

    for key, value in params.items():
        is_not_valid_filter = (
                not hasattr(model, key) or
                value is None
        )

        if is_not_valid_filter:
            continue

        field = getattr(model, key, None)

        if isinstance(value, str):
            query = query.filter(field.ilike('%{}%'.format(value)))
        elif isinstance(value, UUID):
            query = query.filter(field == str(value))
        elif isinstance(value, Enum):
            query = query.filter(field == value.name)
        else:
            query = query.filter(field == value)

    return query
