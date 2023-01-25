import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from src.models.meta import Base
from uuid import uuid4
from src.lib.hashing import PasswordEncoder
from src.models.primitives.user import (
    FirstName,
    SAFirstName,
    LastName,
    SALastName,
    MiddleName,
    SAMiddleName,
    Email,
    SAEmail,
)


class User(Base):
    __tablename__ = "user"

    id = sa.Column(UUID, primary_key=True, default=lambda: str(uuid4()))
    email: Email = sa.Column(SAEmail, nullable=False, unique=True, index=True)
    password = sa.Column(sa.String, nullable=True)

    first_name: FirstName = sa.Column(SAFirstName, nullable=True)
    last_name: LastName = sa.Column(SALastName, nullable=True)
    middle_name: MiddleName = sa.Column(SAMiddleName, nullable=True)

    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    deleted = sa.Column(sa.DateTime, nullable=True)

    is_admin = sa.Column(sa.Boolean, server_default="false", nullable=False)

    credential_version = sa.Column(UUID, nullable=False, default=lambda: str(uuid4()))

    @classmethod
    def make_password_hash(cls, password):
        return PasswordEncoder().encode(password)

    def is_password_valid(self, password):
        return PasswordEncoder().validate(password, self.password)
