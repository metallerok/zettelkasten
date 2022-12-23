import pytest
from src.services.registration import (
    RegistrationService,
    UserCreationError,
    RegistrationInput,
)
from src.models.primitives.user import (
    FirstName,
    LastName,
    MiddleName,
)
from src.models.user import User
from src.message_bus import events

from src.repositories.users import SAUsersRepo
from tests.helpers.users import make_test_user


def test_registration_service(db_session):
    users_repo = SAUsersRepo(db_session)

    registration_service = RegistrationService(
        users_repo=users_repo,
    )

    data = RegistrationInput(
        first_name=FirstName("First"),
        last_name=LastName("Last"),
        middle_name=MiddleName("Middle"),
        email="testmail@mail.com",
        password="1234",
    )

    user = registration_service.register(data)

    db_session.commit()

    user = users_repo.get(id_=user.id)

    assert user and type(user) == User
    assert user.first_name == data.first_name
    assert user.middle_name == data.middle_name
    assert user.last_name == data.last_name
    assert user.email == data.email
    assert user.is_password_valid("1234")

    emitted_events = registration_service.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.UserCreated in emitted_events_types


def test_try_register_user_but_already_exists(db_session):
    user = make_test_user(db_session)

    users_repo = SAUsersRepo(db_session)

    registration_service = RegistrationService(
        users_repo=users_repo,
    )

    data = RegistrationInput(
        first_name=FirstName("First"),
        last_name=LastName("Last"),
        middle_name=MiddleName("Middle"),
        email=user.email,
        password="1234",
    )

    with pytest.raises(UserCreationError):
        registration_service.register(data)
