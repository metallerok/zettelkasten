import abc
from typing import List
from dataclasses import dataclass
from src.message_bus.types import Event
from src.message_bus import events
from src.models.note import Note
from src.models.folder import Folder
from src.models.primitives.note import (
    NoteTitle,
    NoteColor,
)
from src.repositories.notes import NotesRepoABC

from uuid import uuid4, UUID


@dataclass()
class NoteCreationInput:
    title: NoteTitle
    color: NoteColor = None
    text: str = None


class NoteCreationError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class NoteCreatorABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def create(
            self,
            data: NoteCreationInput,
            user_id: UUID,
            folder: Folder = None,
    ) -> Note:
        raise NotImplementedError


class NoteCreator(NoteCreatorABC):
    def __init__(
            self,
            notes_repo: NotesRepoABC,
    ):
        self._notes_repo = notes_repo

        super().__init__()

    def create(
            self,
            data: NoteCreationInput,
            user_id: UUID,
            folder: Folder = None,
    ) -> Note:
        note = Note(
            id=str(uuid4()),
            title=data.title,
            color=data.color,
            text=data.text,
            folder=folder,
            user_id=str(user_id),
        )

        self._notes_repo.add(folder)

        self._events.append(
            events.NoteCreated(
                id=str(folder.id),
                user_id=str(user_id),
            )
        )

        return note
