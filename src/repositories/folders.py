import abc
import datetime as dt
import sqlalchemy as sa
from sqlalchemy.orm import aliased
from typing import Optional, List
from src.models.folder import Folder
from sqlalchemy.orm import Session
from uuid import UUID


class FoldersRepoABC(abc.ABC):
    def get(
            self,
            id_: UUID,
            with_deleted: bool = False,
            user_id: UUID = None,
    ) -> Optional[Folder]:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, folder: Folder):
        raise NotImplementedError

    @abc.abstractmethod
    def list(
            self,
            title: str = None,
            parent_id: UUID = None,
            user_id: UUID = None,
            with_deleted: bool = False
    ) -> List[Folder]:
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

    def get(
            self,
            id_: UUID,
            with_deleted: bool = False,
            user_id: UUID = None,
    ) -> Optional[Folder]:
        query = self._db_session.query(
            Folder
        ).filter(
            Folder.id == id_,
        )

        if user_id:
            query = query.filter(
                Folder.user_id == user_id,
            )

        if not with_deleted:
            query = query.filter(
                Folder.deleted.is_(None)
            )

        return query.one_or_none()

    def list(
            self,
            title: str = None,
            parent_id: UUID = None,
            user_id: UUID = None,
            with_deleted: bool = False
    ) -> List[Folder]:
        query = self._db_session.query(
            Folder
        )

        if title:
            query = query.filter(
                sa.type_coerce(Folder.title, sa.String).ilike(f"%{title}%"),
            )

        if parent_id is not None:
            parent = aliased(Folder)

            query = query.join(
                parent,
                sa.and_(
                    parent.id == Folder.parent_id,
                    parent.deleted.is_(None),
                )
            ).filter(
                Folder.parent_id == parent_id,
            )
        else:
            query = query.filter(
                Folder.parent_id.is_(None),
            )

        if user_id:
            query = query.filter(
                Folder.user_id == user_id,
            )

        if not with_deleted:
            query = query.filter(
                Folder.deleted.is_(None)
            )

        result = query.all()

        return result

    def add(self, folder: Folder):
        self._db_session.add(folder)

    def remove(self, folder: Folder):
        if folder.deleted is None:
            folder.deleted = dt.datetime.utcnow()
