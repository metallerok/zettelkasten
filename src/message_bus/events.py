from dataclasses import dataclass
from src.models.primitives.user import (
    Email
)


class Event:
    pass


@dataclass()
class UserCreated(Event):
    id: str


@dataclass
class AuthSessionClosed(Event):
    id: str


@dataclass
class PasswordChangeRequestCreated(Event):
    token: str
    token_id: str
    user_id: str
    email: Email


@dataclass
class UserPasswordChanged(Event):
    id: str
    email: Email


@dataclass
class FolderCreated(Event):
    id: str
    user_id: str


@dataclass
class FolderUpdated(Event):
    id: str
    updated_fields: dict
    user_id: str


@dataclass
class FolderRemoved(Event):
    id: str
    user_id: str


@dataclass
class NoteCreated(Event):
    id: str
    user_id: str


@dataclass
class NoteUpdated(Event):
    id: str
    updated_fields: dict
    user_id: str


@dataclass
class NoteRemoved(Event):
    id: str
    user_id: str


@dataclass
class NoteRelationCreated(Event):
    id: str
    child_note_id: str
    user_id: str


@dataclass
class NoteRelationRemoved(Event):
    id: str
    child_note_id: str
    user_id: str
