from dataclasses import dataclass
from dataclasses_serialization.json import JSONSerializer
from src.models.primitives.user import (
    Email
)
from uuid import UUID


serializer = JSONSerializer
serializer.serialization_functions[UUID] = lambda uuid_: str(uuid_)
serializer.deserialization_functions[UUID] = lambda cls, uuid_: UUID(uuid_)


class Event:
    def serialize(self) -> dict:
        return serializer.serialize(self)

    @classmethod
    def deserialize(cls, data: dict) -> 'Event':
        return serializer.deserialize(cls, data)


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
