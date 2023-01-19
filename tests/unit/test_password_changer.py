import pytest
from src.services.password_change import (
    PasswordChanger,
    ChangePasswordError,
)

from src.repositories.password_change_tokens import SAPasswordChangeTokensRepo
from src.repositories.auth_sessions import SAAuthSessionsRepo
from src.services.password_change import PasswordChangeTokenCreator
from src.repositories.users import SAUsersRepo
from src.lib.hashing import TokenEncoder
from src.message_bus import events

from tests.helpers.users import make_test_user


def test_try_change_password_by_current_password_but_wrong_pass(db_session):
    current_password = "current_pass"

    user = make_test_user(db_session, password=current_password)

    db_session.commit()

    password_changer = PasswordChanger(
        tokens_repo=SAPasswordChangeTokensRepo(db_session, encoder=TokenEncoder()),
        users_repo=SAUsersRepo(db_session),
        auth_sessions_repo=SAAuthSessionsRepo(db_session, encoder=TokenEncoder()),
    )

    with pytest.raises(ChangePasswordError):
        password_changer.change_by_password(
            user=user,
            current_password="wrong_pass",
            new_password="new_pass",
        )


def test_change_password_by_current_password(db_session):
    current_password = "current_pass"
    new_password = "new_pass"
    user = make_test_user(db_session, password=current_password)

    db_session.commit()

    password_changer = PasswordChanger(
        tokens_repo=SAPasswordChangeTokensRepo(db_session, encoder=TokenEncoder()),
        users_repo=SAUsersRepo(db_session),
        auth_sessions_repo=SAAuthSessionsRepo(db_session, encoder=TokenEncoder()),
    )

    password_changer.change_by_password(
        user=user,
        current_password=current_password,
        new_password=new_password,
    )

    db_session.commit()
    db_session.flush(user)

    assert user.is_password_valid(new_password)

    emitted_events = password_changer.get_events()
    assert len(emitted_events) > 0

    emitted_events_types = [type(e) for e in emitted_events]

    assert events.UserPasswordChanged in emitted_events_types


def test_password_change_token_creator(db_session):
    tokens_repo = SAPasswordChangeTokensRepo(db_session, encoder=TokenEncoder())
    user = make_test_user(db_session)

    creator = PasswordChangeTokenCreator(
        password_change_tokens_repo=tokens_repo,
        encoder=TokenEncoder(),
    )

    token = creator.make(user)

    db_session.commit()

    assert token

    model = tokens_repo.get(token)

    assert model
    assert model.user_id == user.id


def test_change_password_by_token(db_session):
    tokens_repo = SAPasswordChangeTokensRepo(db_session, encoder=TokenEncoder())
    user = make_test_user(db_session)
    credential_version_before_change = user.credential_version

    creator = PasswordChangeTokenCreator(
        password_change_tokens_repo=tokens_repo,
        encoder=TokenEncoder(),
    )

    token = creator.make(user)

    db_session.commit()

    password_changer = PasswordChanger(
        tokens_repo=tokens_repo,
        users_repo=SAUsersRepo(db_session),
        auth_sessions_repo=SAAuthSessionsRepo(db_session, encoder=TokenEncoder()),
    )

    new_password = "new_pass"

    password_changer.change_by_token(
        token=token,
        password=new_password,
    )

    db_session.commit()
    db_session.flush(user)

    assert user.is_password_valid(new_password)
    assert user.credential_version != credential_version_before_change
