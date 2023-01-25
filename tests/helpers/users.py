from sqlalchemy.orm import Session
from src.models.user import User
from src.models.primitives.user import (
    FirstName,
    LastName,
    MiddleName,
    Email,
)
from uuid import uuid4


def make_test_user(
        db_session: Session,
        password: str = "default_pass",
) -> User:
    user = User(
        id=str(uuid4()),
        email=Email(f"{str(uuid4())}@mail.com"),
        first_name=FirstName("First"),
        last_name=LastName("Last"),
        middle_name=MiddleName("Middle"),
        password=User.make_password_hash(password),
        credential_version=str(uuid4()),
    )

    db_session.add(user)

    return user
