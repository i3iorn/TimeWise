import datetime
from dataclasses import dataclass
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
    estimated_time: Duration
    time_spent: Duration
    tags: List[Tag]
    interval: Duration
    recur_from: RecurFrom
    custom_fields: List[CustomField]

    # Timestamps
    due_time: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    completed_at: datetime.datetime
    start_time: datetime.datetime
