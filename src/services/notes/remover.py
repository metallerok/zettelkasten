import abc
from typing import List
from src.message_bus.types import Event
from src.message_bus import events
from src.models.note import Note
from src.repositories.notes import NotesRepoABC

from uuid import UUID


class NoteRemoveError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class NoteRemoverABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def remove(
            self,
            note: Note,
            user_id: UUID,
    ):
        raise NotImplementedError


class NoteRemover(NoteRemoverABC):
    def __init__(
            self,
            notes_repo: NotesRepoABC,
    ):
        self._notes_repo = notes_repo

        super().__init__()

    def remove(
            self,
            note: Note,
            user_id: UUID,
    ):
        self._notes_repo.remove(note)

        self._events.append(
            events.NoteRemoved(
                id=note.id,
                user_id=user_id,
            )
        )
