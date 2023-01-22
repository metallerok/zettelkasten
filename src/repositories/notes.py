import abc
import datetime as dt
import sqlalchemy as sa
from typing import Optional, List
from src.models.note import Note
from sqlalchemy.orm import Session
from uuid import UUID


class NotesRepoABC(abc.ABC):
    def get(
            self,
            id_: UUID,
            with_deleted: bool = False,
            user_id: UUID = None,
    ) -> Optional[Note]:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, note: Note):
        raise NotImplementedError

    @abc.abstractmethod
    def list(
            self,
            title: str = None,
            by_folder: bool = False,
            folder_id: UUID = None,
            user_id: UUID = None,
            with_deleted: bool = False
    ) -> List[Note]:
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, note: Note):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create(cls, *args, **kwargs):
        return cls()


class SANotesRepo(NotesRepoABC):
    def __init__(self, db_session: Session):
        self._db_session = db_session

    @classmethod
    def create(cls, db_session: Session) -> 'SANotesRepo':
        return cls(db_session)

    def get(
            self,
            id_: UUID,
            with_deleted: bool = False,
            user_id: UUID = None,
    ) -> Optional[Note]:
        query = self._db_session.query(
            Note
        ).filter(
            Note.id == str(id_),
        )

        if user_id:
            query = query.filter(
                Note.user_id == str(user_id),
            )

        if not with_deleted:
            query = query.filter(
                Note.deleted.is_(None)
            )

        return query.one_or_none()

    def list(
            self,
            title: str = None,
            by_folder: bool = False,
            folder_id: UUID = None,
            user_id: UUID = None,
            with_deleted: bool = False
    ) -> List[Note]:
        query = self._db_session.query(
            Note
        )

        if title:
            query = query.filter(
                sa.type_coerce(Note.title, sa.String).ilike(f"%{title}%"),
            )

        if by_folder:
            query = query.filter(
                Note.folder_id.is_(str(folder_id)),
            )

        if user_id:
            query = query.filter(
                Note.user_id == str(user_id),
            )

        if not with_deleted:
            query = query.filter(
                Note.deleted.is_(None)
            )

        result = query.all()

        return result

    def add(self, note: Note):
        self._db_session.add(note)

    def remove(self, note: Note):
        if note.deleted is None:
            note.deleted = dt.datetime.utcnow()
