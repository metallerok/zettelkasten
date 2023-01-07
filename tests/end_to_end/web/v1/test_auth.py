from uuid import uuid4
from src.entrypoints.web.api.v1 import url
from src.repositories.auth_sessions import SAAuthSessionsRepo
from src.repositories.users import SAUsersRepo
from src.services.auth import (
    TokenSessionMaker,
    AuthSessionInput,
    TokenSession,
)
# from src.entrypoints.web.errors.user import HTTPWrongUserData
from falcon import (
    HTTP_200,
    HTTP_401,
    HTTP_400,
)
from config import TestConfig
# from src.message_bus import events
# from src.message_bus.factory import default_events_handlers
# from tests.helpers.message_bus import DryRunMessageBus

from src.models.user import User

from src.lib.hashing import TokenEncoder

TEST_USER_PASSWORD = "querty123"

AUTH_URL = url("/auth/sign-in")
AUTH_REFRESH_URL = url("/auth/refresh")


def make_test_user(db_session):
    password_hash = User.make_password_hash(TEST_USER_PASSWORD)

    user = User(
        id=str(uuid4()),
        email=f"{str(uuid4())}@mail.com",
        password=password_hash,
    )

    SAUsersRepo(db_session).add(user)

    return user


def make_test_auth_session(db_session, user: User, device_id: str) -> TokenSession:
    tokens_repo = SAAuthSessionsRepo(db_session, TokenEncoder())
    session_maker = TokenSessionMaker(
        sessions_repo=tokens_repo,
        encoder=TokenEncoder(),
        config=TestConfig,
    )

    session = session_maker.make(
        AuthSessionInput(
            user_id=user.id,
            device_id=device_id,
            credential_version=user.credential_version,
        )
    )

    return session


def test_try_getting_auth_session_with_wrong_credentials(api, db_session):
    user = make_test_user(db_session)
    db_session.commit()

    req_body = {
        "email": user.email,
        "password": "wrong_pass",
        "device_id": str(uuid4()),
    }

    result = api.simulate_post(AUTH_URL, json=req_body)

    assert result.status == HTTP_400


def test_getting_auth_session(api, db_session):
    user = make_test_user(db_session)
    db_session.commit()

    req_body = {
        "email": user.email,
        "password": TEST_USER_PASSWORD,
        "device_id": str(uuid4()),
    }

    result = api.simulate_post(AUTH_URL, json=req_body)

    assert result.status == HTTP_200

    resp_body = result.json

    assert "access_token" in resp_body
    assert "refresh_token" in resp_body

    created_session = SAAuthSessionsRepo(db_session, TokenEncoder()).get(resp_body["refresh_token"])

    assert created_session is not None


def test_try_refresh_session_without_params(api, db_session):
    result = api.simulate_post(AUTH_REFRESH_URL)

    assert result.status == HTTP_401


def test_try_refresh_session_with_wrong_session_token(api, db_session):
    req_body = {
        "refresh_token": str(uuid4()),
        "device_id": str(uuid4()),
    }

    result = api.simulate_post(AUTH_REFRESH_URL, json=req_body)

    assert result.status == HTTP_401


def test_refresh_session_by_manual_credentials(api, db_session):
    user = make_test_user(db_session)
    db_session.commit()

    device_id = str(uuid4())

    session = make_test_auth_session(db_session, user, device_id)
    db_session.commit()

    req_body = {
        "refresh_token": session.refresh_token,
        "device_id": device_id,
    }

    result = api.simulate_post(AUTH_REFRESH_URL, json=req_body)

    assert result.status == HTTP_200

    received_refresh_token = result.json.get("refresh_token")
    received_access_token = result.json.get("access_token")

    assert received_refresh_token is not None
    assert received_refresh_token != session.refresh_token

    assert received_access_token is not None
    assert received_access_token != session.access_token

    created_session = SAAuthSessionsRepo(db_session, TokenEncoder()).get(received_refresh_token)
    assert created_session is not None

    old_session = SAAuthSessionsRepo(db_session, TokenEncoder()).get(session.refresh_token)
    assert old_session is None
