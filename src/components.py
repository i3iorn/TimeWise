from enum import Enum

MONTH_LENGTH = 30.4375  # Days in a month on average
YEAR_LENGTH = 365.25    # Days in a year on average


class TimeWiseValue:
    @classmethod
    def save(cls, db, value_type, value):
        db.insert("timewise_values", name=cls.__name__, value_type=value_type, value=value)


class Duration:
    TIME_UNITS = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    MAX_VALUES = {'years': float('inf'), 'months': 12, 'days': 30.4375, 'hours': 24, 'minutes': 60, 'seconds': 60}
    CONVERSION_FACTORS = {'years': YEAR_LENGTH * 86400, 'months': MONTH_LENGTH * 86400, 'days': 86400, 'hours': 3600, 'minutes': 60, 'seconds': 1}

    def __init__(self, **kwargs):
        self.time_units = {unit: 0 for unit in self.TIME_UNITS}
        for unit, value in kwargs.items():
            if unit in self.time_units:
                self._adjust_time_units(unit, value)

    def _adjust_time_units(self, unit, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Duration values must be positive integers")
        while value >= self.MAX_VALUES[unit]:
            if unit == 'seconds':
                value -= self.MAX_VALUES[unit]
                self.time_units['minutes'] += 1
            elif unit == 'minutes':
                value -= self.MAX_VALUES[unit]
                self.time_units['hours'] += 1
            elif unit == 'hours':
                value -= self.MAX_VALUES[unit]
                self.time_units['days'] += 1
            elif unit == 'days':
                value -= self.MAX_VALUES[unit]
                self.time_units['months'] += 1
            elif unit == 'months':
                value -= self.MAX_VALUES[unit]
                self.time_units['years'] += 1
        self.time_units[unit] += value

    def __add__(self, other):
        if not isinstance(other, Duration):
            raise ValueError("Can only add Duration objects")
        result = Duration()
        for unit in self.TIME_UNITS:
            result._adjust_time_units(unit, self.time_units[unit] + other.time_units[unit])
        return result

    def __sub__(self, other):
        self_seconds = self.as_seconds()
        other_seconds = other.as_seconds()
        result_seconds = self_seconds - other_seconds

        if result_seconds < 0:
            raise ValueError("Resulting duration cannot have negative values")

        return Duration.from_seconds(result_seconds)

    @classmethod
    def from_seconds(cls, total_seconds):
        time_units_values = {'years': 0, 'months': 0, 'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
        # Conversion factors need to be in descending order of duration
        conversion_factors = reversed(cls.CONVERSION_FACTORS.items())

        for unit, factor in conversion_factors:
            unit_value, total_seconds = divmod(total_seconds, factor)
            time_units_values[unit] = int(unit_value)

        return cls(**time_units_values)

    def as_seconds(self):
        return sum(self.time_units[unit] * factor for unit, factor in self.CONVERSION_FACTORS.items())

    def __str__(self):
        return ''.join(f"{value}{unit[0].upper()}" for unit, value in self.time_units.items() if value > 0)


class Title(TimeWiseValue, str):
    """
    Title of a task
    """
    def __new__(cls, value):
        if not value:
            raise ValueError("Title cannot be empty")
        if len(value) > 127:
            raise ValueError("Title cannot exceed 255 characters")

        return super().__new__(cls, value)


class Description(TimeWiseValue, str):
    """
    Description of a task
    """
    def __new__(cls, value):
        if not value:
            raise ValueError("Description cannot be empty")
        if len(value) > 1024:
            raise ValueError("Description cannot exceed 1024 characters")

        return super().__new__(cls, value)


class CustomField(TimeWiseValue):
    def __new__(cls, *args, **kwargs):
        try:
            name = kwargs.pop('name')
            value = kwargs.pop('value')
            value_type = kwargs.pop('type')
        except KeyError:
            raise ValueError("CustomField requires 'name', 'value', and 'type' arguments")

        if not name:
            raise ValueError("CustomField name cannot be empty")
        if not value:
            raise ValueError("CustomField value cannot be empty")
        if not value_type:
            raise ValueError("CustomField type cannot be empty")

        if len(args) > 0:
            raise ValueError("CustomField only accepts keyword arguments")
        if len(kwargs) > 0:
            raise ValueError("CustomField only accepts 'name', 'value', and 'type' keyword arguments")

        try:
            type_function = getattr(__builtins__, value_type)
        except AttributeError:
            raise ValueError(f"CustomField type {value_type} is not a valid type")

        try:
            value = type_function(value)
        except ValueError:
            raise ValueError(f"CustomField value {value} is not a valid {value_type}")

        return super().__new__(cls, name, value, value_type)

    def __init__(self, name, value, value_type):
        self._name = name
        self._value = value
        self._value_type = value_type

    def __str__(self):
        return f"{self.name}: {self.value}"

    def __repr__(self):
        return f"{self.name}: {self.value}"

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value and self.value_type == other.value_type

    def __set__(self, instance, value):
        raise AttributeError("CustomField values cannot be altered. Create a new CustomField instead or set the value.")

    def __get__(self, instance, owner):
        return self._value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            value = self.value_type(value)
        except ValueError:
            raise ValueError(f"CustomField value {value} is not a valid {self.value_type}")
        self._value = value

    @property
    def value_type(self):
        return self._value_type


class RecurFrom(TimeWiseValue, Enum):
    DUE_DATE = "Due Date"
    COMPLETION_DATE = "Completion Date"
    START_DATE = "Start Date"


class Tag(TimeWiseValue, str):
    def __new__(cls, value):
        if not value:
            raise ValueError("Tag cannot be empty")
        if len(value) > 127:
            raise ValueError("Tag cannot exceed 127 characters")

        return super().__new__(cls, value)


class Status(TimeWiseValue, str):
    def __new__(cls, value):
        if not value:
            raise ValueError("Status cannot be empty")
        if len(value) > 127:
            raise ValueError("Status cannot exceed 127 characters")

        return super().__new__(cls, value)


class Priority(TimeWiseValue):
    pass


class Category(TimeWiseValue):
    pass