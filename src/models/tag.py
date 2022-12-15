import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from src.models.meta import Base

from src.models.primitives.tag import (
    TagTitle,
    SATagTitle,
)

from uuid import uuid4


class Tag(Base):
    __tablename__ = "tag"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    title: TagTitle = sa.Column(SATagTitle, nullable=False)

    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    deleted = sa.Column(sa.DateTime, nullable=True)
