from typing import Any
from dataclasses import dataclass
from enum import Enum


class ValueID:
    """
    This class is used to generate unique IDs for values.
    """
    _id = 0

    @classmethod
    def generate_id(cls) -> int:
        """
        Generate a unique ID.
        """
        cls._id += 1
        return cls._id


class TimeWiseValueManager:
    """
    This class is used to manage the values of the application. All values in the application register with this class.

    # Features
    - Singleton
    - Value registration

    # Properties
    - values: A dictionary of all values in the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs) -> "TimeWiseValueManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self) -> None:
        self.values = {}
        self.monitors = []

    def register_value(self, value: "BaseTimeWiseComponent") -> None:
        """
        Register a value with the value manager.
        """
        self.values[value.id] = value

    def emit_event(self, event_type: "EventType", value_id: int, old_value: Any, new_value: Any) -> None:
        """
        Emit an event to all registered monitors.
        """
        event = Event(event_type, value_id, old_value, new_value)
        for monitor in self.monitors:
            monitor.handle_event(event)

    def register_monitor(self, monitor: "Monitor") -> None:
        """
        Register a monitor with the value manager.
        """
        self.monitors.append(monitor)

    def unregister_monitor(self, monitor: "Monitor") -> None:
        """
        Unregister a monitor with the value manager.
        """
        self.monitors.remove(monitor)


class EventType(Enum):
    VALUE_CHANGED = "value_changed"
    VALUE_DELETED = "value_deleted"
    VALUE_ADDED = "value_added"


@dataclass
class Event:
    """
    This class is used to represent an event in the application.

    # Properties
    - event: The type of event.
    - value_id: The ID of the value that triggered the event.
    - new_value: The new value of the value that triggered the event.
    """
    event: EventType
    value_id: int
    old_value: Any
    new_value: Any


class BaseTimeWiseComponent:
    """
    This component is the base for all values and components in the application. It is used to enable event handling.

    # Features
    - Event handling
    - Value validation
    - Value setting
    - Value getting
    """
    def __init__(self, value: Any) -> None:
        self._manager = TimeWiseValueManager()
        self._id = ValueID.generate_id()
        self._value = value
        self._manager.register_value(self)

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        raise AttributeError("ID cannot be changed")

    def __get__(self, instance, owner) -> Any:
        return self._value

    def __set__(self, instance, value) -> None:
        self._value = value
        self._manager.emit_event(EventType.VALUE_CHANGED, self.id, self._value, value)


class Monitor:
    """
    This class is used to monitor the values of the application. It listens for events and updates the UI accordingly.

    # Features
    - Event listening
    """
    def __init__(self) -> None:
        self._manager = TimeWiseValueManager()
        self._manager.register_monitor(self)

    def event_handler(self, event: "Event") -> None:
        raise NotImplementedError("Event handler must be implemented in subclass")
