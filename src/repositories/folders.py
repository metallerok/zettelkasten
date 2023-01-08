import abc
import datetime as dt
from typing import Optional
from src.models.folder import Folder
from sqlalchemy.orm import Session
from uuid import UUID


class FoldersRepoABC(abc.ABC):
    def get(self, id_: UUID, with_deleted: bool = False) -> Optional[Folder]:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, folder: Folder):
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, folder: Folder):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create(cls, *args, **kwargs):
        return cls()


class SAFoldersRepo(FoldersRepoABC):
    def __init__(self, db_session: Session):
        self._db_session = db_session

    @classmethod
    def create(cls, db_session: Session) -> 'SAFoldersRepo':
        return cls(db_session)

    def get(self, id_: UUID, with_deleted: bool = False) -> Optional[Folder]:
        query = self._db_session.query(
            Folder
        ).filter(
            Folder.id == str(id_),
        )

        if not with_deleted:
            query = query.filter(
                Folder.deleted.is_(None)
            )

        return query.one_or_none()

    def add(self, folder: Folder):
        self._db_session.add(folder)

    def remove(self, folder: Folder):
        if folder.deleted is None:
            folder.deleted = dt.datetime.utcnow()
