import os
from typing import Any
from dataclasses import dataclass
from enum import Enum

from src import exceptions


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
        self._validate_value(value)
        self._manager = TimeWiseValueManager()
        self._id = ValueID.generate_id()
        self._value = value
        self._manager.register_value(self)

    def _validate_value(self, value: Any) -> None:
        """
        Validate the value before setting it. Is called by default on all values.
        :param value: The value to validate.
        :type value: Any
        :return: None
        """
        raise NotImplementedError("_validate_value must be implemented in subclass")

    @property
    def id(self) -> int:
        """
        Get the ID of the value. The ID is unique to each value in the application.
        :return:
        """
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """
        Set the ID of the value. The ID cannot be changed.

        :param value:
        :return:
        """
        raise AttributeError("ID cannot be changed")

    def to_dict(self) -> dict:
        """
        Convert a value to a dictionary.
        """
        return {

        }

    def from_dict(self, data: dict) -> "BaseTimeWiseComponent":
        """
        Create a value from a dictionary.
        """
        raise NotImplementedError("from_dict must be implemented in subclass")

    def __get__(self, instance, owner) -> Any:
        return self._value

    def __set__(self, instance, value) -> None:
        self._validate_value(value)
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


class Integer(int, BaseTimeWiseComponent):
    """
    This class is used to represent an integer value in the application.
    """
    def __init__(self, value: int) -> None:
        super().__init__(value)

    def _validate_value(self, value: int) -> None:
        if not isinstance(value, int):
            raise exceptions.IntegerException("Value must be an integer")

        if "INTEGER_MAX" in os.environ:
            if value > int(os.environ["INTEGER_MAX"]):
                raise exceptions.ToLargeIntegerException(value, int(os.environ["INTEGER_MAX"]))

        if "INTEGER_MIN" in os.environ:
            if value < int(os.environ["INTEGER_MIN"]):
                raise exceptions.ToSmallIntegerException(value, int(os.environ["INTEGER_MIN"]))


class String(str, BaseTimeWiseComponent):
    """
    This class is used to represent a string value in the application.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def _validate_value(self, value: str) -> None:
        if not isinstance(value, str):
            raise exceptions.StringException("Value must be a string")

        if "STRING_MAX_LENGTH" in os.environ:
            if len(value) > int(os.environ["STRING_MAX_LENGTH"]):
                raise exceptions.ToLongStringException(len(value), int(os.environ["STRING_MAX_LENGTH"]))


class Float(float, BaseTimeWiseComponent):
    """
    This class is used to represent a float value in the application.
    """
    def __init__(self, value: float) -> None:
        super().__init__(value)

    def _validate_value(self, value: float) -> None:
        if not isinstance(value, float):
            raise exceptions.FloatException("Value must be a float")

        if "FLOAT_MAX" in os.environ:
            if value > float(os.environ["FLOAT_MAX"]):
                raise exceptions.ToLargeFloatException(value, float(os.environ["FLOAT_MAX"]))

        if "FLOAT_MIN" in os.environ:
            if value < float(os.environ["FLOAT_MIN"]):
                raise exceptions.ToSmallFloatException(value, float(os.environ["FLOAT_MIN"]))


class Boolean(bool, BaseTimeWiseComponent):
    """
    This class is used to represent a boolean value in the application.
    """
    def __init__(self, value: bool) -> None:
        super().__init__(value)

    def _validate_value(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise exceptions.BooleanException("Value must be a boolean")


class List(list, BaseTimeWiseComponent):
    """
    This class is used to represent a list value in the application. Tuples, lists, and sets are all valid values and
    will be converted to lists.
    """
    def __init__(self, value: list) -> None:
        super().__init__(value)
        self._value = list(value)

    def _validate_value(self, value: Any) -> None:
        if not isinstance(value, (list, tuple, set)):
            raise exceptions.ListException("Value must be a list")


class Dict(dict, BaseTimeWiseComponent):
    """
    This class is used to represent a dictionary value in the application.
    """
    def __init__(self, value: dict) -> None:
        super().__init__(value)

    def _validate_value(self, value: dict) -> None:
        if not isinstance(value, dict):
            raise exceptions.DictException("Value must be a dictionary")

        for key, value in value.items():
            if isinstance(key, callable):
                raise exceptions.DictException("Dictionary keys cannot be callable")
            if isinstance(value, callable):
                raise exceptions.DictException("Dictionary values cannot be callable")

        if "DICT_MAX_LENGTH" in os.environ:
            if len(value) > int(os.environ["DICT_MAX_LENGTH"]):
                raise exceptions.ToLargeDictException(len(value), int(os.environ["DICT_MAX_LENGTH"]))

        if "DICT_MIN_LENGTH" in os.environ:
            if len(value) < int(os.environ["DICT_MIN_LENGTH"]):
                raise exceptions.ToSmallDictException(len(value), int(os.environ["DICT_MIN_LENGTH"]))

        if "DICT_MAX_DEPTH" in os.environ:
            if self._get_depth(value) > int(os.environ["DICT_MAX_DEPTH"]):
                raise exceptions.ToDeepDictException(self._get_depth(value), int(os.environ["DICT_MAX_DEPTH"]))

    def _get_depth(self, dictionary: dict) -> int:
        """
        Get the depth of a dictionary.
        """
        if not isinstance(dictionary, dict) or not dictionary:
            return 0

        return 1 + max(self._get_depth(value) for value in dictionary.values())


class Title(String):
    """
    This class is used to represent the title of a task.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __set__(self, instance, value) -> None:
        super().__set__(instance, value)

    def _validate_value(self, value: str) -> None:
        super()._validate_value(value)
        if "TITLE_MAX_LENGTH" in os.environ:
            if len(value) > int(os.environ["TITLE_MAX_LENGTH"]):
                raise ValueError("Title must be less than 100 characters")


class Description:
    """
    This class is used to represent the description of a task.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __set__(self, instance, value) -> None:
        super().__set__(instance, value)

    def _validate_value(self, value: str) -> None:
        super()._validate_value(value)
        if "DESCRIPTION_MAX_LENGTH" in os.environ:
            if len(value) > int(os.environ["DESCRIPTION_MAX_LENGTH"]):
                raise ValueError("Description must be less than 1000 characters")


class Status(BaseTimeWiseComponent, metaclass=Enum):
    """
    This class is used to represent the status of a task. It behaves like and Enum but is created dynamically at runtime.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def _validate_value(self, value: str) -> None:
        if value not in os.environ.get("STATUSES", "").split(","):
            raise ValueError("Status not recognized")


@dataclass
class Task:
    title: Title
    description: Description
    status: Status

    def __post_init__(self):
        """
        Individual values are validated when set in each property. This method is used to validate relationships between
        values.
        """
        # TODO: Add validation for relationships between values

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Create a Task object from a dictionary.
        """
        return cls(
            Title(data["title"]),
            Description(data["description"]),
            Status(data["status"])
        )

    def to_dict(self) -> dict:
        """
        Convert a Task object to a dictionary.
        """
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status
        }

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    def __eq__(self, other):
        return all([self.title == other.title])
