import abc
import time
import datetime as dt
from dataclasses import dataclass, field
from uuid import uuid4
from typing import Optional, Type
from src.lib.hashing import EncoderABC
from src.lib.jwt import JWTToken
from src.repositories.users import UsersRepoABC
from src.repositories.auth_sessions import AuthSessionsRepoABC
from src.models.primitives.user import (
    Email,
)
from src.models.user import User
from src.models.auth_session import AuthSession, SESSION_LIFETIME
from config import Config
from uuid import UUID

ACCESS_TOKEN_LIFETIME = {"minutes": 10}


@dataclass
class AuthSessionInput:
    user_id: UUID
    device_id: str
    credential_version: UUID
    device_type: str = None
    device_name: str = None
    device_os: str = None
    ip: str = None
    user_agent = None
    data: dict = field(default_factory=dict)


@dataclass
class TokenSession:
    access_token: str
    refresh_token: str


@dataclass
class RefreshSessionInput:
    uuid: str
    device_id: str


class AuthError(Exception):
    pass


class AuthSessionRefreshError(AuthError):
    pass


class SessionMakerABC(abc.ABC):
    @abc.abstractmethod
    def make(self, data: AuthSessionInput):
        raise NotImplementedError


class TokenSessionMaker(SessionMakerABC):
    def __init__(
            self,
            sessions_repo: AuthSessionsRepoABC,
            encoder: EncoderABC,
            config: Type[Config],
    ):
        self._sessions_repo = sessions_repo
        self._config = config
        self._encoder = encoder

    def make(self, data: AuthSessionInput) -> TokenSession:
        token_payload = {
            "object_id": str(data.user_id),
            "credential_version": str(data.credential_version),
            "created": int(time.time()),
            "exp": time.time() + dt.timedelta(**ACCESS_TOKEN_LIFETIME).total_seconds()
        }

        access_token = JWTToken.create(token_payload, self._config.jwt_secret)
        refresh_token = str(uuid4())

        token_hash = self._encoder.encode(refresh_token)

        auth_session = AuthSession(
            token=token_hash,
            user_id=data.user_id,
            device_id=data.device_id,
            device_type=data.device_type,
            device_name=data.device_name,
            device_os=data.device_os,
            ip=data.ip,
            user_agent=data.user_agent,
            created=dt.datetime.utcnow(),
            expires_in=(dt.datetime.utcnow() + dt.timedelta(**SESSION_LIFETIME)),
        )

        self._sessions_repo.remove_by_user_device(user_id=data.user_id, device_id=data.device_id)
        self._sessions_repo.add(auth_session)

        return TokenSession(
            access_token=access_token,
            refresh_token=refresh_token,
        )


class TokenSessionRefresher:
    def __init__(
            self,
            sessions_repo: AuthSessionsRepoABC,
            users_repo: UsersRepoABC,
            encoder: EncoderABC,
            config: Type[Config]
    ):
        self._sessions_repo = sessions_repo
        self._users_repo = users_repo
        self._config = config
        self._encoder = encoder

    def refresh(self, data: RefreshSessionInput) -> TokenSession:
        session = self._sessions_repo.get(data.uuid)

        if session is None:
            raise AuthSessionRefreshError

        if session.device_id != data.device_id:
            raise AuthSessionRefreshError

        user = self._users_repo.get(session.user_id)

        if user is None:
            raise AuthSessionRefreshError

        refresh_token = str(uuid4())
        session.token = self._encoder.encode(refresh_token)
        session.expires_in = (dt.datetime.utcnow() + dt.timedelta(**SESSION_LIFETIME))

        token_payload = {
            "object_id": str(user.id),
            "credential_version": str(user.credential_version),
            "created": int(time.time()),
            "exp": time.time() + dt.timedelta(**ACCESS_TOKEN_LIFETIME).total_seconds()
        }

        access_token = JWTToken.create(token_payload, self._config.jwt_secret)

        return TokenSession(
            access_token=access_token,
            refresh_token=refresh_token,
        )


class AuthenticatorABC(abc.ABC):

    @abc.abstractmethod
    def authenticate(self, *args, **kwargs) -> bool:
        raise NotImplementedError


class UserAuthenticator(AuthenticatorABC):

    def __init__(
            self,
            password_encoder: EncoderABC,
            users_repo: UsersRepoABC,
    ):
        self._users_repo = users_repo
        self._password_encoder = password_encoder

    def authenticate(
            self,
            email: Email,
            password: str,
    ) -> Optional[User]:
        user = self._users_repo.get_by_email(email)

        if not user:
            return None

        is_password_valid = self._password_encoder.validate(
            password,
            user.password,
        )

        if is_password_valid:
            return user


def close_session(session_uuid: str, sessions_repo: AuthSessionsRepoABC):
    sessions_repo.remove(session_uuid)


def revoke_access_tokens(user: User):
    user.credential_version = uuid4()
