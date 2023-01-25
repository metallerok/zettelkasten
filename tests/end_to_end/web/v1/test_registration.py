from uuid import uuid4
from src.models.primitives.user import (
    Email,
)
from src.entrypoints.web.api.v1 import url
from src.repositories.users import SAUsersRepo
from src.entrypoints.web.errors.user import HTTPWrongUserData
from falcon import (
    HTTP_200,
    HTTP_400,
)
from src.message_bus import events
from tests.helpers.message_bus import DryRunMessageBus
from tests.helpers.users import make_test_user

AUTH_REGISTRATION_URL = url("/auth/registration")


def test_try_registration_but_user_with_same_email_already_exists(api, db_session):
    user = make_test_user(db_session)
    user.email = Email("testmail@mail.com")

    db_session.commit()

    req_body = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "email": user.email.value,
        "password": "123",
    }

    result = api.simulate_post(AUTH_REGISTRATION_URL, json=req_body)

    assert result.status == HTTP_400
    assert result.json["error"]["code"] == HTTPWrongUserData.code


def test_registration(api_factory, db_session):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.UserCreated: []
        }
    )

    api = api_factory(message_bus=message_bus)

    req_body = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "email": f"{str(uuid4())}@mail.com",
        "password": "123",
    }

    result = api.simulate_post(AUTH_REGISTRATION_URL, json=req_body)

    assert result.status == HTTP_200
    assert "user" in result.json

    users_repo = SAUsersRepo(db_session)

    user = users_repo.get_by_email(Email(result.json["user"]["email"]))
    assert user
    assert user.first_name.value == req_body["first_name"]
    assert user.last_name.value == req_body["last_name"]
    assert user.middle_name.value == req_body["middle_name"]
    assert user.is_password_valid(req_body["password"])

    emitted_messages = message_bus.messages
    emitted_messages_types = [type(m["message"]) for m in emitted_messages]
    assert events.UserCreated in emitted_messages_types
