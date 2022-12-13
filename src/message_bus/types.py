from typing import Union
from .events import Event
from .commands import Command

Message = Union[Event, Command]
