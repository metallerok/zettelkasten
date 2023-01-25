import abc
from typing import List
from dataclasses import dataclass
from src.message_bus.types import Event
from src.message_bus import events
from src.models.note import Note, NoteToNoteRelation

from uuid import uuid4, UUID


@dataclass()
class NoteRelationCreationInput:
    parent_note: Note
    child_note: Note
    description: str = None


class NoteRelationCreationError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class NoteRelationCreatorABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def create(
            self,
            data: NoteRelationCreationInput,
            user_id: UUID,
    ) -> Note:
        raise NotImplementedError


class NoteRelationCreator(NoteRelationCreatorABC):
    def __init__(
            self,
    ):
        super().__init__()

    def create(
            self,
            data: NoteRelationCreationInput,
            user_id: UUID,
    ) -> Note:
        if (data.parent_note.user_id != user_id) or (data.child_note.user_id != user_id):
            raise NoteRelationCreationError(
                message="Wrong user"
            )

        children_notes = {nr.child_note_id: nr for nr in data.parent_note.notes_relations}

        if data.child_note.id in children_notes:
            children_notes[data.child_note.id].description = data.description

            return data.parent_note

        data.parent_note.notes_relations.append(
            NoteToNoteRelation(
                id=uuid4(),
                child_note=data.child_note,
                parent_note=data.parent_note,
                description=data.description,
            )
        )

        self._events.append(
            events.NoteRelationCreated(
                id=data.parent_note.id,
                child_note_id=data.child_note.id,
                user_id=user_id,
            )
        )

        return data.parent_note
