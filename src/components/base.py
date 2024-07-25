import inspect
import os
from datetime import datetime
from typing import Any, Union

from src import exceptions
from src.timewise import TimeWise
from src.components.events import EventType, Event, ValueChange

__all__ = [
    "TimeWiseValueManager",
    "BaseTimeWiseComponent",
    "Monitor",
    "Integer",
    "String",
    "Float",
    "Boolean",
    "List",
    "Dict",
    "Time",
    "Date",
    "DateTime"
]


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

    def emit_event(self, event: "Event") -> None:
        """
        Emit an event to all registered monitors.
        """
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


class BaseTimeWiseComponent:
    """
    This component is the base for all values and components in the application. It is used to enable event handling.

    # Features
    - Event handling
    - Value validation
    - Value setting
    - Value getting
    """
    _app = None

    def __init__(self, value: Any) -> None:
        self._validate_value(value)
        self._manager = TimeWiseValueManager()
        self._id = ValueID.generate_id()
        self._value = value
        self._manager.register_value(self)

        if self._app is None:
            frame = inspect.currentframe()
            while frame is not None:
                frame = frame.f_back
                if "f_locals" not in frame.__dir__() or "self" not in frame.f_locals:
                    continue
                if frame.f_locals["self"].__class__.__name__ == "TimeWise":
                    break

            if frame is not None:
                self._app = frame.f_locals.get('self', None)

    def _validate_value(self, value: Any) -> None:
        """
        Validate the value before setting it. Is called by default on all values.
        :param value: The value to validate.
        :type value: Any
        :return: None
        """
        raise NotImplementedError("_validate_value must be implemented in subclass")

    @property
    def app(self) -> "TimeWise":
        """
        Get the TimeWise instance.
        """
        return self._app

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
            "id": self.id,
            "value": self._value
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
        self._manager.emit_event(
            ValueChange(self.id, self._value, value)
        )

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value})"

    # Aliases
    as_dict = to_dict


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


class Integer(BaseTimeWiseComponent):
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


class String(BaseTimeWiseComponent):
    """
    This class is used to represent a string value in the application.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def _validate_value(self, value: Union[str, "String"]) -> None:
        if not isinstance(value, (str, String)):
            raise exceptions.StringException("Value must be a string")

        if "STRING_MAX_LENGTH" in os.environ:
            if len(value) > int(os.environ["STRING_MAX_LENGTH"]):
                raise exceptions.ToLongStringException(len(value), int(os.environ["STRING_MAX_LENGTH"]))


class Float(BaseTimeWiseComponent):
    """
    This class is used to represent a float value in the application.
    """
    def __init__(self, value: Union[float, "Float"]) -> None:
        super().__init__(value)

    def _validate_value(self, value: Union[float, "Float"]) -> None:
        if not isinstance(value, (float, Float)):
            raise exceptions.FloatException("Value must be a float")

        if "FLOAT_MAX" in os.environ:
            if value > float(os.environ["FLOAT_MAX"]):
                raise exceptions.ToLargeFloatException(value, float(os.environ["FLOAT_MAX"]))

        if "FLOAT_MIN" in os.environ:
            if value < float(os.environ["FLOAT_MIN"]):
                raise exceptions.ToSmallFloatException(value, float(os.environ["FLOAT_MIN"]))


class Boolean(BaseTimeWiseComponent):
    """
    This class is used to represent a boolean value in the application.
    """
    def __init__(self, value: Union[bool, "Boolean"]) -> None:
        super().__init__(value)

    def _validate_value(self, value: Union[bool, "Boolean"]) -> None:
        if not isinstance(value, (bool, Boolean)):
            raise exceptions.BooleanException("Value must be a boolean")


class List(BaseTimeWiseComponent):
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


class Dict(BaseTimeWiseComponent):
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


class Time(BaseTimeWiseComponent):
    """
    This class is used to represent a time value in the application.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def _validate_value(self, value: str) -> None:
        if not isinstance(value, (str, datetime)):
            raise exceptions.TimeException("Value must be a time, either a string or a datetime object")

        if isinstance(value, str):
            try:
                datetime.strptime(value, "%H:%M:%S")
            except ValueError:
                raise exceptions.TimeFormatException("Value must be a time in the format HH:MM:SS")


class Date(BaseTimeWiseComponent):
    """
    This class is used to represent a date value in the application.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def _validate_value(self, value: str) -> None:
        if not isinstance(value, (str, datetime)):
            raise exceptions.DateException("Value must be a date, either a string or a datetime object")

        if isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise exceptions.DateFormatException("Value must be a date in the format YYYY-MM-DD")


class DateTime(BaseTimeWiseComponent):
    """
    This class is used to represent a datetime value in the application.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def _validate_value(self, value: str) -> None:
        if not isinstance(value, (str, datetime)):
            raise exceptions.DateTimeException("Value must be a datetime, either a string or a datetime object")

        if isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise exceptions.DateTimeFormatException("Value must be a datetime in the format YYYY-MM-DD HH:MM:SS")

    def __gt__(self, other):
        if isinstance(other, DateTime):
            return self._value > other._value
        elif isinstance(other, datetime):
            return self._value > other

        raise TypeError("Cannot compare DateTime with other types")

    def __lt__(self, other):
        if isinstance(other, DateTime):
            return self._value < other._value
        elif isinstance(other, datetime):
            return self._value < other

        raise TypeError("Cannot compare DateTime with other types")

    def __ge__(self, other):
        if isinstance(other, DateTime):
            return self._value >= other._value
        elif isinstance(other, datetime):
            return self._value >= other

        raise TypeError("Cannot compare DateTime with other types")

    def __le__(self, other):
        if isinstance(other, DateTime):
            return self._value <= other._value
        elif isinstance(other, datetime):
            return self._value <= other

        raise TypeError("Cannot compare DateTime with other types")
