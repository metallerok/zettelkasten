import pytest
from src.message_bus import events
from dataclasses import dataclass
from uuid import uuid4
from src.entrypoints.celery.tasks import process_message_bus_event


@dataclass()
class SomeEvent(events.Event):
    id: int
    value: str


@dataclass()
class AnotherEvent(events.Event):
    id: int
    value: str
    flag: bool = False


def test_event_serialization():
    event = SomeEvent(id=1, value="test value")
    data = event.serialize()

    assert type(data) == dict
    data["random_value"] = 33

    restored_event = AnotherEvent.deserialize(data)

    assert restored_event.id == event.id
    assert restored_event.value == event.value
    assert restored_event.flag is False
    assert hasattr(restored_event, "random_value") is False


@pytest.mark.skip
def test_sending_event_to_celery():
    event = events.UserCreated(id=uuid4())

    process_message_bus_event.s(
        event_name=type(event).__name__,
        serialized_data=event.serialize(),
    ).apply_async(queue="events")
