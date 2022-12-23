from dataclasses import dataclass


class Event:
    pass


@dataclass()
class TestEvent(Event):
    message: str


@dataclass()
class UserCreated(Event):
    id: str
