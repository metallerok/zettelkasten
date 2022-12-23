from sqlalchemy.orm import Session
from src.models.user import User
from src.models.primitives.user import (
    FirstName,
    LastName,
    MiddleName,
)
from uuid import uuid4


def make_test_user(db_session: Session) -> User:
    user = User(
        id=str(uuid4()),
        email=f"{str(uuid4())}@mail.com",
        first_name=FirstName("First"),
        last_name=LastName("Last"),
        middle_name=MiddleName("Middle"),
    )

    db_session.add(user)

    return user
