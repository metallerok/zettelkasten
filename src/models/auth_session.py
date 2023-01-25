import sqlalchemy as sa
import datetime as dt
from src.models.primitives.base import SAUUID
from uuid import uuid4, UUID
from .meta import Base

SESSION_LIFETIME = {"days": 30}


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: UUID = sa.Column(SAUUID, primary_key=True, default=lambda: uuid4())
    token = sa.Column(sa.String, nullable=False, index=True, default=lambda: str(uuid4()))
    user_id: UUID = sa.Column(SAUUID, nullable=False, index=True)
    device_id = sa.Column(sa.String, nullable=False, index=True)
    device_type = sa.Column(sa.String, nullable=True)
    device_os = sa.Column(sa.String, nullable=True)
    device_name = sa.Column(sa.String, nullable=True)
    ip = sa.Column(sa.String, nullable=True)
    user_agent = sa.Column(sa.String, nullable=True)
    created = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    expires_in = sa.Column(
        sa.DateTime,
        nullable=True,
        default=lambda: (dt.datetime.utcnow() + dt.timedelta(**SESSION_LIFETIME)),
    )
    deleted = sa.Column(sa.DateTime, nullable=True)
