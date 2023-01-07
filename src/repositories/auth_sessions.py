import datetime as dt
import sqlalchemy as sa
from sqlalchemy.orm import Session
from typing import Optional
import abc
from ..models.auth_session import AuthSession
from src.lib.hashing import EncoderABC


class AuthSessionsRepoABC(abc.ABC):
    @abc.abstractmethod
    def get(self, token: str) -> Optional[AuthSession]:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, session: AuthSession):
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, token: str) -> Optional[AuthSession]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_user_device(self, user_id: str, device_id: str) -> Optional[AuthSession]:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_by_user_device(self, user_id: str, device_id: str) -> Optional[AuthSession]:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_all_by_user(self, user_id: str):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create(cls, *args, **kwargs):
        return cls()


class SAAuthSessionsRepo(AuthSessionsRepoABC):
    def __init__(
            self,
            db_session: Session,
            encoder: EncoderABC,
    ):
        self._db_session = db_session
        self._encoder = encoder

    @classmethod
    def create(cls, db_session: Session, encoder: EncoderABC) -> 'SAAuthSessionsRepo':
        return cls(db_session, encoder)

    def get(self, token: str) -> Optional[AuthSession]:
        token_hash = self._encoder.encode(token)

        query = self._db_session.query(
            AuthSession
        ).filter(
            AuthSession.token == token_hash,
            AuthSession.expires_in > sa.func.now(),
            AuthSession.deleted.is_(None),
        )

        return query.one_or_none()

    def add(self, session: AuthSession):
        self._db_session.add(session)

    def remove(self, token: str) -> Optional[AuthSession]:
        session = self.get(token)

        if session:
            self._db_session.delete(session)

        return session

    def get_by_user_device(self, user_id: str, device_id: str) -> Optional[AuthSession]:
        query = self._db_session.query(
            AuthSession
        ).filter(
            AuthSession.user_id == user_id,
            AuthSession.device_id == device_id,
            AuthSession.expires_in > sa.func.now(),
            AuthSession.deleted.is_(None),
        )

        return query.one_or_none()

    def remove_by_user_device(self, user_id: str, device_id: str) -> Optional[AuthSession]:
        query = self._db_session.query(
            AuthSession
        ).filter(
            AuthSession.user_id == user_id,
            AuthSession.device_id == device_id,
            AuthSession.expires_in > sa.func.now(),
            AuthSession.deleted.is_(None),
        )

        sessions = query.all()

        for session in sessions:
            session.deleted = dt.datetime.utcnow()

        return sessions[0] if len(sessions) > 0 else None

    def remove_all_by_user(self, user_id: str):
        query = self._db_session.query(
            AuthSession
        ).filter(
            AuthSession.user_id == user_id,
            AuthSession.expires_in > sa.func.now(),
            AuthSession.deleted.is_(None),
        )

        sessions = query.all()

        for session in sessions:
            session.deleted = sa.func.now()
