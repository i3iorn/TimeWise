import os
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from src.components.base import BaseTimeWiseComponent, String, Time, DateTime


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


@dataclass
class Task(BaseTimeWiseComponent):
    title: Title
    description: Description = None
    category: Category = None
    status: Status = Status("Not Started")
    created_at: Time = DateTime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: Time = DateTime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    deleted_at: Time = None

    def __post_init__(self):
        """
        Individual values are validated when set in each property. This method is used to validate relationships between
        values.
        """
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
                dictionary[key] = Status(value)

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
