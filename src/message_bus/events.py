from dataclasses import dataclass


class Event:
    pass


@dataclass()
class TestEvent(Event):
    message: str


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
    email: str


@dataclass
class UserPasswordChanged(Event):
    id: str
    email: str


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
