import abc
import datetime as dt
from typing import Optional
from src.models.user import User
from src.models.primitives.user import (
    Email,
)
from sqlalchemy.orm import Session
from uuid import UUID


class UsersRepoABC(abc.ABC):
    def get(self, id_: UUID, with_deleted: bool = False) -> Optional[User]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_email(self, email: Email, with_deleted: bool = False) -> Optional[User]:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, user: User):
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, user: User):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create(cls, *args, **kwargs):
        return cls()


class SAUsersRepo(UsersRepoABC):
    def __init__(self, db_session: Session):
        self._db_session = db_session

    @classmethod
    def create(cls, db_session: Session) -> 'SAUsersRepo':
        return cls(db_session)

    def add(self, user: User):
        self._db_session.add(user)

    def get_by_email(self, email: Email, with_deleted: bool = False) -> User:
        query = self._db_session.query(
            User
        ).filter(
            User.email == email,
        )

        if not with_deleted:
            query = query.filter(
                User.deleted.is_(None)
            )

        return query.one_or_none()

    def get(self, id_: UUID, with_deleted: bool = False) -> Optional[User]:
        query = self._db_session.query(
            User
        ).filter(
            User.id == str(id_),
        )

        if not with_deleted:
            query = query.filter(
                User.deleted.is_(None)
            )

        return query.one_or_none()

    def remove(self, user: User):
        if user.deleted is None:
            user.deleted = dt.datetime.utcnow()
