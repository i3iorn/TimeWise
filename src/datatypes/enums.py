from enum import Enum

from typeguard import typechecked


@typechecked
class Status(Enum):
    """
    An enumeration class to represent the status of a task.
    """
    NOT_STARTED = "not_started"  # Task has not been started
    IN_PROGRESS = "in_progress"  # Task is currently in progress
    COMPLETED = "completed"  # Task has been completed
    CANCELLED = "cancelled"  # Task has been cancelled
    WONT_DO = "wont_do"  # Task will not be done


@typechecked
class Priority(Enum):
    """
    An enumeration class to represent the priority of a task.
    """
    LOW = "low"  # Low priority task
    NORMAL = "normal"  # Normal priority task
    HIGH = "high"  # High priority task
    URGENT = "urgent"  # Urgent priority task
