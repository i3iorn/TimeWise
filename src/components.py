from enum import Enum

MONTH_LENGTH = 30.4375  # Days in a month on average
YEAR_LENGTH = 365.25    # Days in a year on average


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


class Title:
    pass


class Description:
    pass


class CustomField:
    pass


class RecurFrom(Enum):
    DUE_DATE = "Due Date"
    COMPLETION_DATE = "Completion Date"
    START_DATE = "Start Date"


class Tag(str):
    pass


class Status(str):
    pass


class Priority(int):
    pass