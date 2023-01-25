from src.entrypoints.web.api.v1 import url
from falcon.status_codes import (
    HTTP_200,
    HTTP_400,
    HTTP_401,
    HTTP_422,
)
from tests.helpers.headers import Headers
from tests.helpers.users import make_test_user
from tests.helpers.message_bus import DryRunMessageBus
from src.lib.hashing import TokenEncoder
from src.message_bus import events
from src.repositories.password_change_tokens import SAPasswordChangeTokensRepo
from src.repositories.users import SAUsersRepo
from src.services.password_change import PasswordChangeTokenCreator
from src.entrypoints.web.errors.user import HTTPPasswordChangingError
from uuid import uuid4

CURRENT_USER_URL = url("/current-user")
USER_CHANGE_PASSWORD_URL = url("/user/change-password")
USER_CHANGE_PASSWORD_REQUEST_URL = url("/user/change-password-request")
CURRENT_USER_CHANGE_PASSWORD_URL = url("/current-user/change-password")


def test_get_current_user_without_auth(api):
    result = api.simulate_get(CURRENT_USER_URL)

    assert result.status == HTTP_401


def test_get_current_user(
        api,
        db_session,
        auth_session_factory,
        headers: Headers
):
    user = make_test_user(db_session)
    auth_session = auth_session_factory(db_session, user)
    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    result = api.simulate_get(CURRENT_USER_URL, headers=headers.get())

    assert result.status_code == 200
    assert result.json["user"]["id"] == user.id


def test_try_make_change_password_request_for_unauthorized_user(
        api_factory,
        db_session,
        headers: Headers,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.PasswordChangeRequestCreated: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)

    db_session.commit()

    req_body = {
        "email": user.email.value
    }

    result = api.simulate_post(USER_CHANGE_PASSWORD_REQUEST_URL, headers=headers.get(), json=req_body)

    assert result.status_code == 200

    tokens_repo = SAPasswordChangeTokensRepo(db_session, TokenEncoder())

    emitted_messages_types = [type(m["message"]) for m in message_bus.messages]
    assert events.PasswordChangeRequestCreated in emitted_messages_types
    event = next(m["message"] for m in message_bus.messages
                 if type(m["message"]) == events.PasswordChangeRequestCreated)

    token_model = tokens_repo.get(event.token)

    assert token_model
    assert token_model.expires_in is not None
    assert token_model.user_id == user.id


def test_try_change_user_password_without_params(api):

    result = api.simulate_post(USER_CHANGE_PASSWORD_URL)

    assert result.status == HTTP_422


def test_try_change_user_password_with_wrong_token(api):
    params = {
        "token": "wrong_token"
    }

    req_body = {
        "password": "new_pass"
    }

    result = api.simulate_post(USER_CHANGE_PASSWORD_URL, params=params, json=req_body)

    assert result.status == HTTP_400
    assert result.json["error"]["code"] == HTTPPasswordChangingError.code


def test_try_change_password(
        api_factory,
        db_session,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.UserPasswordChanged: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)
    default_password = user.password

    encoder = TokenEncoder()
    tokens_repo = SAPasswordChangeTokensRepo(db_session, encoder=encoder)
    users_repo = SAUsersRepo(db_session)

    creator = PasswordChangeTokenCreator(
        password_change_tokens_repo=tokens_repo,
        encoder=TokenEncoder(),
    )

    token = creator.make(user)

    db_session.commit()

    params = {
        "token": token
    }

    req_body = {
        "password": "new_pass"
    }

    result = api.simulate_post(USER_CHANGE_PASSWORD_URL, params=params, json=req_body)

    assert result.status == HTTP_200

    db_session.expire_all()

    user = users_repo.get(user.id)

    assert default_password != encoder.encode(req_body["password"])
    assert user.is_password_valid(req_body["password"])

    emitted_messages_types = [type(m["message"]) for m in message_bus.messages]
    assert events.UserPasswordChanged in emitted_messages_types
    event = next(m["message"] for m in message_bus.messages
                 if type(m["message"]) == events.UserPasswordChanged)
    assert event.email == user.email


def test_try_get_current_user_with_wrong_credential_version(
        api,
        db_session,
        auth_session_factory,
        headers: Headers
):
    user = make_test_user(db_session)
    auth_session = auth_session_factory(db_session, user)
    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    result = api.simulate_get(CURRENT_USER_URL, headers=headers.get())

    assert result.status_code == 200

    user.credential_version = str(uuid4())

    db_session.commit()

    result = api.simulate_get(CURRENT_USER_URL, headers=headers.get())

    assert result.status == HTTP_401


def test_current_user_change_password_without_auth(api):
    result = api.simulate_post(CURRENT_USER_CHANGE_PASSWORD_URL)

    assert result.status == HTTP_401


def test_current_user_change_password(
        api_factory,
        db_session,
        auth_session_factory,
        headers: Headers,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.UserPasswordChanged: []
        }
    )
    api = api_factory(message_bus=message_bus)

    current_password = "current_pass"

    user = make_test_user(db_session, password=current_password)
    auth_session = auth_session_factory(db_session, user)
    users_repo = SAUsersRepo(db_session)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_body = {
        "current_password": current_password,
        "new_password": "new_pass",
    }

    result = api.simulate_post(CURRENT_USER_CHANGE_PASSWORD_URL, headers=headers.get(), json=req_body)

    assert result.status == HTTP_200

    db_session.expire_all()

    user = users_repo.get(user.id)

    assert user.is_password_valid(req_body["new_password"])

    emitted_messages_types = [type(m["message"]) for m in message_bus.messages]
    assert events.UserPasswordChanged in emitted_messages_types
