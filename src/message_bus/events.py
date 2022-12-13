from dataclasses import dataclass


class Event:
    pass


@dataclass()
class TestEvent(Event):
    message: str
