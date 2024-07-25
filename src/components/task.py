import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from src.components.base import BaseTimeWiseComponent, String, Time, DateTime
from src.helpers import get_app


class Title(String):
    """
    This class is used to represent the title of a task.
    """
    def __init__(self, value: Union[str, "String"]) -> None:
        super().__init__(value)

    def __set__(self, instance, value) -> None:
        super().__set__(instance, value)

    def _validate_value(self, value: Union[str, "String"]) -> None:
        super()._validate_value(value)
        if "TITLE_MAX_LENGTH" in os.environ:
            if len(value) > int(os.environ["TITLE_MAX_LENGTH"]):
                raise ValueError("Title must be less than 100 characters")


class Description(String):
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


class TimeWiseEnum:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __iter__(self):
        return iter({key for key in self.__dict__ if not key.startswith("__")})

    def __call__(self, item):
        if item in self.__dict__.values():
            return [key for key, value in self.__dict__.items() if value == item][0]
        else:
            return None

    def __str__(self):
        return str({key for key in self.__dict__ if not key.startswith("__")})


@dataclass
class Task(BaseTimeWiseComponent):
    title: Title
    description: Description = None
    category: str = None
    status: str = "Not Started"
    created_at: Time = DateTime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: Time = DateTime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    deleted_at: Time = None

    def __post_init__(self):
        """
        Individual values are validated when set in each property. This method is used to validate relationships between
        values.
        """

        categories = get_app().db.get_categories
        statuses = get_app().db.get_statuses

        Category = TimeWiseEnum(**{category.upper(): category for category in categories})
        Status = TimeWiseEnum(**{status.upper(): status for status in statuses})

        if self.category is not None:
            if self.category not in Category:
                raise ValueError(f"Category must be one of {Category}")

        if self.status is not None:
            if self.status not in Status:
                raise ValueError(f"Status must be one of {Status}")

        if self.created_at > self.updated_at:
            raise ValueError("Created at cannot be after updated at")

        if self.deleted_at is not None:
            if self.deleted_at < self.created_at:
                raise ValueError("Deleted at cannot be before created at")
            if self.deleted_at < self.updated_at:
                raise ValueError("Deleted at cannot be before updated at")

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Create a Task object from a dictionary.
        """
        dictionary = {}
        for i in range(0, len(data)):
            key, value = data.popitem()
            if key == "title":
                dictionary[key] = Title(value)
            elif key == "description":
                dictionary[key] = Description(value)
            elif key == "status":
                dictionary[key] = value

        if len(data) > 0:
            raise ValueError("Unknown keys in dictionary")

        return cls(**dictionary)

    def to_dict(self) -> dict:
        """
        Convert a Task object to a dictionary.
        """
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            **super().to_dict()
        }

    def __str__(self) -> str:
        return str(self.title)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title}|{self.status})"

    def __eq__(self, other):
        return all([self.title == other.title])
