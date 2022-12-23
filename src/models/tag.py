from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.meta import Base

from src.models.primitives.tag import (
    TagTitle,
    SATagTitle,
)

from uuid import uuid4

if TYPE_CHECKING:
    from src.models.user import User


class Tag(Base):
    __tablename__ = "tag"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    title: TagTitle = sa.Column(SATagTitle, nullable=False)

    user_id = sa.Column(UUID, sa.ForeignKey("user.id"), nullable=False, index=True)
    user: 'User' = relationship("User", foreign_keys=[user_id])

    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    deleted = sa.Column(sa.DateTime, nullable=True)
