from dataclasses import dataclass
from dataclasses_serialization.json import JSONSerializer
from src.models.primitives.user import (
    Email
)
from uuid import UUID


class Event:
    def serialize(self) -> dict:
        return JSONSerializer.serialize(self)

    @classmethod
    def deserialize(cls, data: dict) -> 'Event':
        return JSONSerializer.deserialize(cls, data)


@dataclass()
class UserCreated(Event):
    id: UUID


@dataclass
class AuthSessionClosed(Event):
    id: UUID


@dataclass
class PasswordChangeRequestCreated(Event):
    token: str
    token_id: UUID
    user_id: UUID
    email: Email


@dataclass
class UserPasswordChanged(Event):
    id: UUID
    email: Email


@dataclass
class FolderCreated(Event):
    id: UUID
    user_id: UUID


@dataclass
class FolderUpdated(Event):
    id: UUID
    updated_fields: dict
    user_id: UUID


@dataclass
class FolderRemoved(Event):
    id: UUID
    user_id: UUID


@dataclass
class NoteCreated(Event):
    id: UUID
    user_id: UUID


@dataclass
class NoteUpdated(Event):
    id: UUID
    updated_fields: dict
    user_id: UUID


@dataclass
class NoteRemoved(Event):
    id: UUID
    user_id: UUID


@dataclass
class NoteRelationCreated(Event):
    id: UUID
    child_note_id: UUID
    user_id: UUID


@dataclass
class NoteRelationRemoved(Event):
    id: UUID
    child_note_id: UUID
    user_id: UUID
