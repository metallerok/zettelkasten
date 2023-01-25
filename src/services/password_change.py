import abc
import datetime as dt
import sqlalchemy as sa
from secrets import token_hex
from src.lib.hashing import EncoderABC

from src.repositories.password_change_tokens import PasswordChangeTokensRepoABC
from src.repositories.users import UsersRepoABC
from src.repositories.auth_sessions import AuthSessionsRepoABC

from src.services.auth import revoke_access_tokens

from src.models.password_change_token import PasswordChangeToken, TOKEN_LIFETIME
from src.models.user import User

from src.message_bus import events
from uuid import uuid4


class PasswordChangeTokenCreatorABC(abc.ABC):
    def make(self, user_id: str) -> PasswordChangeToken:
        raise NotImplementedError


class PasswordChangeTokenCreator(PasswordChangeTokenCreatorABC):
    def __init__(
            self,
            password_change_tokens_repo: PasswordChangeTokensRepoABC,
            encoder: EncoderABC
    ):
        self._password_change_tokens_repo = password_change_tokens_repo
        self._encoder = encoder
        self._events = []

    def make(self, user: User) -> str:
        token = token_hex(32)
        token_hash = self._encoder.encode(token)

        model = PasswordChangeToken(
            id=uuid4(),
            token=token_hash,
            user_id=user.id,
            email=user.email,
            expires_in=(dt.datetime.utcnow() + dt.timedelta(**TOKEN_LIFETIME))
        )

        self._password_change_tokens_repo.add(model)

        self._events.append(
            events.PasswordChangeRequestCreated(
                user_id=user.id,
                token_id=model.id,
                token=token,
                email=user.email,
            )
        )

        return token

    def get_events(self):
        return self._events


class ChangePasswordError(Exception):
    pass


class PasswordChangerABC(abc.ABC):
    @abc.abstractmethod
    def change_by_token(self, token: str, password: str):
        raise NotImplementedError

    @abc.abstractmethod
    def change_by_password(
            self,
            user: User,
            current_password: str,
            new_password: str,
    ):
        raise NotImplementedError


class PasswordChanger(PasswordChangerABC):
    def __init__(
            self,
            tokens_repo: PasswordChangeTokensRepoABC,
            users_repo: UsersRepoABC,
            auth_sessions_repo: AuthSessionsRepoABC,
    ):
        self._tokens_repo = tokens_repo
        self._users_repo = users_repo
        self._auth_sessions_repo = auth_sessions_repo
        self._events = []

    def change_by_token(self, token: str, password: str):
        token = self._tokens_repo.get(token)

        if not token:
            raise ChangePasswordError("Wrong password change token")

        user = self._users_repo.get(token.user_id)

        if not user:
            raise ChangePasswordError("User not found")

        user.password = user.make_password_hash(password)
        revoke_access_tokens(user)
        token.used = sa.func.now()

        self._auth_sessions_repo.remove_all_by_user(user.id)

        self._events.append(
            events.UserPasswordChanged(
                email=user.email,
                id=user.id,
            )
        )

    def change_by_password(
            self,
            user: User,
            current_password: str,
            new_password: str,
    ):
        if not user.is_password_valid(current_password):
            raise ChangePasswordError("Wrong current password")

        user.password = user.make_password_hash(new_password)

        self._events.append(
            events.UserPasswordChanged(
                email=user.email,
                id=user.id,
            )
        )

    def get_events(self):
        return self._events
