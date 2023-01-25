import sqlalchemy as sa
import datetime as dt
from uuid import uuid4
from secrets import token_hex
from .meta import Base
from src.models.primitives.base import SAUUID
from src.models.primitives.user import (
    SAEmail,
    Email
)

from uuid import UUID

TOKEN_LIFETIME = {"hours": 2}


class PasswordChangeToken(Base):
    __tablename__ = "password_change_tokens"

    id: UUID = sa.Column(SAUUID, primary_key=True, default=lambda: uuid4())

    # todo: make custom token primitive type
    token = sa.Column(sa.String, nullable=False, index=True, default=lambda: str(token_hex(24)))
    user_id: UUID = sa.Column(SAUUID, nullable=False, index=True)
    email: Email = sa.Column(SAEmail, nullable=False)

    created = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    expires_in = sa.Column(
        sa.DateTime,
        nullable=True,
        default=lambda: (dt.datetime.utcnow() + dt.timedelta(**TOKEN_LIFETIME)),
    )
    used = sa.Column(sa.DateTime, nullable=True)
    deleted = sa.Column(sa.DateTime, nullable=True)
