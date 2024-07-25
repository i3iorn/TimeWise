from dataclasses import dataclass, field
from typing import Any


class EventType:
    def __new__(cls, *args, **kwargs):
        raise TypeError("Cannot instantiate EventType class")


@dataclass
class Event:
    """
    This class is used to represent an event in the application.

    # Properties
    - value_id: The ID of the value that triggered the event.
    """
    value_id: int


@dataclass
class ValueChange(Event):
    """
    This class is used to represent a value change event in the application.

    # Properties
    - value_id: The ID of the value that triggered the event.
    - old_value: The old value of the value that triggered the event.
    - new_value: The new value of the value that triggered the event.
    """
    old_value: Any
    new_value: Any
