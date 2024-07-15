from enum import Enum


class Duration:
    def __init__(
            self,
            year: int = 0,
            months: int = 0,
            weeks: int = 0,
            days: int = 0,
            hours: int = 0,
            minutes: int = 0,
            seconds: int = 0
    ):
        all_input = [year, months, weeks, days, hours, minutes, seconds]
        for value in all_input:
            if value < 0:
                raise ValueError("Duration values cannot be negative")
            if not isinstance(value, int):
                try:
                    int(value)
                except ValueError:
                    raise ValueError("Duration values must be integers")

        self.year = year
        self.months = months
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def __str__(self):
        return f"{self.year}Y{self.months}M{self.weeks}W{self.days}D{self.hours}h{self.minutes}m{self.seconds}s"


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