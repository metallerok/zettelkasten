import abc
from typing import List
from src.message_bus.types import Event
from src.message_bus import events
from src.models.note import Note

from uuid import UUID


class NoteRelationRemoveError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class NoteRelationRemoverABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def remove(
            self,
            parent_note: Note,
            child_note: Note,
            user_id: UUID,
    ) -> Note:
        raise NotImplementedError


class NoteRelationRemover(NoteRelationRemoverABC):
    def __init__(
            self,
    ):
        super().__init__()

    def remove(
            self,
            parent_note: Note,
            child_note: Note,
            user_id: UUID,
    ) -> Note:
        children_notes = {nr.child_note_id: nr for nr in parent_note.notes_relations}

        if child_note.id not in children_notes:
            return parent_note

        parent_note.notes_relations.remove(
            children_notes[child_note.id]
        )

        self._events.append(
            events.NoteRelationRemoved(
                id=parent_note.id,
                child_note_id=child_note.id,
                user_id=user_id,
            )
        )

        return parent_note
