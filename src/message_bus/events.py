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
class FolderCreated(Event):
    id: str
    user_id: str


@dataclass
class FolderUpdated(Event):
    id: str
    updated_fields: dict
    user_id: str
