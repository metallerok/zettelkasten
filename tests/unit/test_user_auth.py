import pytest
import datetime as dt

from src.models.user import User
from src.models.auth_session import AuthSession
from src.models.primitives.user import (
    Email,
)
from src.repositories.auth_sessions import SAAuthSessionsRepo
from src.services.auth import (
    UserAuthenticator,
    AuthSessionInput,
    TokenSessionMaker,
    TokenSessionRefresher,
    RefreshSessionInput,
    AuthSessionRefreshError,
    TokenSession,
    close_session,
)
from src.lib.hashing import PasswordEncoder, TokenEncoder
from src.lib.jwt import JWTToken
from src.repositories.users import SAUsersRepo
from config import TestConfig
from uuid import uuid4

TEST_USER_NAME = "test_user"
TEST_USER_PASSWORD = "querty123"


def make_test_user(db_session):
    password_hash = User.make_password_hash(TEST_USER_PASSWORD)

    user = User(
        id=str(uuid4()),
        email=Email(f"{str(uuid4())}@mail.com"),
        password=password_hash,
        credential_version=str(uuid4()),
    )

    db_session.add(user)

    return user


def make_test_auth_session(db_session) -> (TokenSession, User):
    user = make_test_user(db_session)
    sessions_repo = SAAuthSessionsRepo(db_session, encoder=TokenEncoder())
    session_maker = TokenSessionMaker(
        sessions_repo=sessions_repo,
        encoder=TokenEncoder(),
        config=TestConfig,
    )

    device_id = str(uuid4())

    session = session_maker.make(
        AuthSessionInput(
            user_id=user.id,
            device_id=device_id,
            credential_version=user.credential_version,
        )
    )

    return session, user


def test_success_user_authentication_by_email_and_password(db_session):
    user = make_test_user(db_session)
    users_repo = SAUsersRepo(db_session)

    user_auth = UserAuthenticator(
        password_encoder=PasswordEncoder(),
        users_repo=users_repo,
    )

    authenticated_user = user_auth.authenticate(
        email=user.email,
        password=TEST_USER_PASSWORD,
    )

    assert authenticated_user.id == user.id


def test_unsuccessful_user_authentication_by_email_and_wrong_password(db_session):
    user = make_test_user(db_session)
    users_repo = SAUsersRepo(db_session)

    user_auth = UserAuthenticator(
        password_encoder=PasswordEncoder(),
        users_repo=users_repo,
    )

    assert user_auth.authenticate(
        email=user.email,
        password="wrong_password",
    ) is None


def test_unsuccessful_user_authentication_by_wrong_email_and_right_password(db_session):
    users_repo = SAUsersRepo(db_session)

    user_auth = UserAuthenticator(
        password_encoder=PasswordEncoder(),
        users_repo=users_repo,
    )

    assert user_auth.authenticate(
        email=Email("wrong_mail@mail.com"),
        password=TEST_USER_PASSWORD,
    ) is None


def test_make_auth_session(db_session):
    auth_sessions_query = db_session.query(AuthSession)

    auth_sessions_query.delete()

    user = make_test_user(db_session)
    sessions_repo = SAAuthSessionsRepo(db_session, encoder=TokenEncoder())
    session_maker = TokenSessionMaker(
        sessions_repo=sessions_repo,
        encoder=TokenEncoder(),
        config=TestConfig,
    )

    device_id = str(uuid4())
    session = session_maker.make(
        AuthSessionInput(
            user_id=user.id,
            device_id=device_id,
            credential_version=user.credential_version,
        )
    )

    assert session is not None
    assert session.access_token is not None
    assert session.refresh_token is not None

    assert auth_sessions_query.filter(AuthSession.deleted.is_(None)).count() == 1
    assert sessions_repo.get(session.refresh_token) is not None

    auth_session = sessions_repo.get_by_user_device(user_id=user.id, device_id=device_id)
    assert auth_session is not None


def test_only_one_auth_session_for_device(db_session):
    auth_sessions_query = db_session.query(AuthSession)

    auth_sessions_query.delete()

    user = make_test_user(db_session)
    tokens_repo = SAAuthSessionsRepo(db_session, encoder=TokenEncoder())
    session_maker = TokenSessionMaker(
        sessions_repo=tokens_repo,
        encoder=TokenEncoder(),
        config=TestConfig,
    )

    device_id = str(uuid4())

    # first device session
    session_maker.make(
        AuthSessionInput(
            user_id=user.id,
            device_id=device_id,
            credential_version=user.credential_version,
        )
    )

    # second device session
    session_maker.make(
        AuthSessionInput(
            user_id=user.id,
            device_id=device_id,
            credential_version=user.credential_version,
        )
    )

    assert auth_sessions_query.filter(AuthSession.deleted.is_(None)).count() == 1

    auth_session = tokens_repo.get_by_user_device(user_id=user.id, device_id=device_id)
    assert auth_session is not None


def test_auth_by_access_token(db_session):
    session, user = make_test_auth_session(db_session)

    token = JWTToken(session.access_token, TestConfig.jwt_secret)

    assert token.is_valid()
    assert token["object_id"] == user.id


def test_refresh_non_existed_session(db_session):
    sessions_repo = SAAuthSessionsRepo(db_session, encoder=TokenEncoder())
    users_repo = SAUsersRepo(db_session)
    session_refresher = TokenSessionRefresher(
        sessions_repo=sessions_repo,
        users_repo=users_repo,
        encoder=TokenEncoder(),
        config=TestConfig,
    )

    with pytest.raises(AuthSessionRefreshError):
        session_refresher.refresh(
            RefreshSessionInput(uuid=str(uuid4()), device_id=str(uuid4()))
        )


def test_refresh_session_with_wrong_device(db_session):
    user = make_test_user(db_session)
    sessions_repo = SAAuthSessionsRepo(db_session, encoder=TokenEncoder())
    users_repo = SAUsersRepo(db_session)
    session_maker = TokenSessionMaker(
        sessions_repo=sessions_repo,
        config=TestConfig,
        encoder=TokenEncoder(),
    )
    session_refresher = TokenSessionRefresher(
        sessions_repo=sessions_repo,
        users_repo=users_repo,
        encoder=TokenEncoder(),
        config=TestConfig,
    )

    device_id = str(uuid4())

    initial_session = session_maker.make(
        AuthSessionInput(
            user_id=user.id,
            device_id=device_id,
            credential_version=user.credential_version,
        )
    )

    with pytest.raises(AuthSessionRefreshError):
        session_refresher.refresh(
            RefreshSessionInput(
                uuid=initial_session.refresh_token,
                device_id=str(uuid4()),
            )
        )


def test_refresh_session(db_session):
    user = make_test_user(db_session)
    sessions_repo = SAAuthSessionsRepo(db_session, encoder=TokenEncoder())
    users_repo = SAUsersRepo(db_session)
    session_maker = TokenSessionMaker(
        sessions_repo=sessions_repo,
        config=TestConfig,
        encoder=TokenEncoder(),
    )
    session_refresher = TokenSessionRefresher(
        sessions_repo=sessions_repo,
        users_repo=users_repo,
        encoder=TokenEncoder(),
        config=TestConfig
    )

    device_id = str(uuid4())

    initial_session = session_maker.make(
        AuthSessionInput(
            user_id=user.id,
            device_id=device_id,
            credential_version=user.credential_version,
        )
    )

    new_session = session_refresher.refresh(
        RefreshSessionInput(
            uuid=initial_session.refresh_token,
            device_id=device_id,
        )
    )

    assert new_session.access_token != initial_session.access_token
    assert new_session.refresh_token != initial_session.refresh_token

    sessions_data = sessions_repo.get(new_session.refresh_token)

    assert sessions_data.user_id == user.id
    assert sessions_data.device_id == device_id

    assert sessions_repo.get(initial_session.refresh_token) is None


def test_close_session(db_session):
    session, _ = make_test_auth_session(db_session)
    sessions_repo = SAAuthSessionsRepo(db_session, encoder=TokenEncoder())

    close_session(session.refresh_token, sessions_repo)

    assert sessions_repo.get(session.refresh_token) is None


def test_get_expired_auth_session(db_session):
    encoder = TokenEncoder()
    token = str(uuid4())
    token_hash = encoder.encode(token)
    expired_session = AuthSession(
        token=token_hash,
        device_id=str(uuid4()),
        user_id=str(uuid4()),
        created=dt.datetime.utcnow(),
        expires_in=dt.datetime.utcnow() - dt.timedelta(days=1),
    )
    db_session.add(expired_session)
    db_session.commit()

    sessions_repo = SAAuthSessionsRepo(
        db_session,
        encoder=TokenEncoder(),
    )

    assert sessions_repo.get(token) is None


def test_try_refresh_expired_auth_session(db_session):
    encoder = TokenEncoder()
    token = str(uuid4())
    token_hash = encoder.encode(token)
    user = make_test_user(db_session)
    users_repo = SAUsersRepo(db_session)
    expired_session = AuthSession(
        token=token_hash,
        device_id=str(uuid4()),
        user_id=user.id,
        created=dt.datetime.utcnow(),
        expires_in=dt.datetime.utcnow() - dt.timedelta(days=1),
    )
    db_session.add(expired_session)
    db_session.commit()

    sessions_repo = SAAuthSessionsRepo(
        db_session,
        encoder=TokenEncoder(),
    )

    with pytest.raises(AuthSessionRefreshError):
        TokenSessionRefresher(
            sessions_repo=sessions_repo,
            users_repo=users_repo,
            encoder=TokenEncoder(),
            config=TestConfig,
        ).refresh(
            RefreshSessionInput(
                device_id=expired_session.device_id,
                uuid=token
            )
        )
