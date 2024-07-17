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
