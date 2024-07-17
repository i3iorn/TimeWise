import datetime
from dataclasses import dataclass, field
from typing import List

from src.category import Category
from src.components import Duration, Status, Tag, Priority, CustomField, Title, Description, RecurFrom


@dataclass
class Task:
    title: Title
    description: Description
    status: Status
    priority: Priority
    category: Category
    estimated_time: Duration = None
    tags: List[Tag] = None
    interval: Duration = None
    recur_from: RecurFrom = None
    custom_fields: List[CustomField] = None
    time_spent: Duration = None
    created_at: datetime.datetime = field(default=datetime.datetime.now())
    due_time: datetime.datetime = None
    updated_at: datetime.datetime = None
    completed_at: datetime.datetime = None
    start_time: datetime.datetime = None

    def __post_init__(self):
        """
        Individual values are validated when set in each property. This method is used to validate the entire task.
        """
        if self.due_time and self.start_time and self.due_time < self.start_time:
            raise ValueError("Due time cannot be before start time")

        if self.completed_at and self.completed_at < self.created_at:
            raise ValueError("Completed time cannot be before created time")

        if self.updated_at and self.updated_at < self.created_at:
            raise ValueError("Updated time cannot be before created time")

        if self.start_time and self.start_time < self.created_at:
            raise ValueError("Start time cannot be before created time")

        if self.due_time and self.due_time < self.created_at:
            raise ValueError("Due time cannot be before created time")

        if self.completed_at and self.completed_at < self.created_at:
            raise ValueError("Completed time cannot be before created time")

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    def __eq__(self, other):
        return all([self.title == other.title, self.category == other.category])
