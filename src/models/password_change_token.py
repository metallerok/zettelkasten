import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import datetime as dt
from uuid import uuid4
from secrets import token_hex
from .meta import Base

TOKEN_LIFETIME = {"hours": 2}


class PasswordChangeToken(Base):
    __tablename__ = "password_change_tokens"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))

    # todo: make custom token primitive type
    token = sa.Column(sa.String, nullable=False, index=True, default=lambda: str(token_hex(24)))
    user_id = sa.Column(UUID, nullable=False, index=True)
    email = sa.Column(sa.String, nullable=False)

    created = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    expires_in = sa.Column(
        sa.DateTime,
        nullable=True,
        default=lambda: (dt.datetime.utcnow() + dt.timedelta(**TOKEN_LIFETIME)),
    )
    used = sa.Column(sa.DateTime, nullable=True)
    deleted = sa.Column(sa.DateTime, nullable=True)
