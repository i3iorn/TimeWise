import datetime
import logging
from dataclasses import dataclass, field
from typing import Union, Literal

from typeguard import typechecked

from src.datatypes.collection import TagSet, ReminderSet, ParticipantSet, AttachmentSet, TaskSet
from src.datatypes.types import TaskTitle, Location, Project, Category
from src import Status, Priority, Description, Notes
from src.user import User

logger = logging.getLogger(__name__)

RECURRING_FROM_TYPES = Literal["due_date", "start_date", "completion_date", "creation_date", "last_modified_date"]
DEFAULT_STATUS = Status.NOT_STARTED
DEFAULT_PRIORITY = Priority.NORMAL


@dataclass
@typechecked
class Task:
    """
    A class to represent a task in the TimeWise application.

    :param owner: The user who owns the task.
    :type owner: src.user.User
    :param title: The title of the task.
    :type title: str
    :param description: The description of the task.
    :type description: str
    :param status: The status of the task.
    :type status: Status
    :param priority: The priority of the task.
    :type priority: Priority
    :param tags: The tags associated with the task.
    :type tags: src.collection.TagSet
    :param reminders: The reminders set for the task.
    :type reminders: src.collection.ReminderSet
    :param location: The location of the task.
    :type location: src.datatypes.types.Location
    :param participants: The participants involved in the task.
    :type participants: src.collection.ParticipantList
    :param attachments: The attachments associated with the task.
    :type attachments: src.collection.AttachmentList
    :param notes: The notes associated with the task.
    :type notes: src.Notes
    :param recurring_from: The type of date from which the task recurs.
    :type recurring_from: Union[RECURRING_FROM_TYPES, None]
    :param category: The category to which the task belongs.
    :type category: Union[src.datatypes.types.Category, None]
    :param project: The project to which the task belongs.
    :type project: Union[src.datatypes.types.Project, None]
    :param require: The tasks required for this task to be completed.
    :type require: src.collection.TaskSet
    :param start_time: The start time of the task.
    :type start_time: datetime.datetime
    :param duration: The duration of the task.
    :type duration: datetime.timedelta
    :param due_time: The due time of the task.
    :type due_time: datetime.datetime
    :param completion_time: The completion time of the task.
    :type completion_time: datetime.datetime
    :param creation_time: The creation time of the task.
    :type creation_time: datetime.datetime
    :param last_modified_time: The last modified time of the task.
    :type last_modified_time: datetime.datetime
    """
    owner: "User"
    title: "TaskTitle"
    description: "Description" = field(default_factory=Description)
    status: "Status" = DEFAULT_STATUS
    priority: "Priority" = DEFAULT_PRIORITY
    tags: "TagSet" = field(default_factory=TagSet)
    reminders: "ReminderSet" = field(default_factory=ReminderSet)
    location: "Location" = field(default=None)
    participants: "ParticipantSet" = field(default_factory=ParticipantSet)
    attachments: "AttachmentSet" = field(default_factory=AttachmentSet)
    notes: "Notes" = field(default_factory=Notes)
    recurring_from: Union[RECURRING_FROM_TYPES, None] = field(default=None)
    category: Union["Category", None] = field(default=None)
    project: Union["Project", None] = field(default=None)
    require: "TaskSet" = field(default_factory=TaskSet)

    start_time: datetime.datetime = field(default=None)
    duration: datetime.timedelta = field(default=None)
    due_time: datetime.datetime = field(default=None)
    completion_time: datetime.datetime = field(default=None)
    creation_time: datetime.datetime = field(default=None)
    last_modified_time: datetime.datetime = field(default=None)

    def __post_init__(self) -> None:
        """
        Initializes the task with the current time if the creation time is not set.
        """
        if self.creation_time is None:
            self.creation_time = datetime.datetime.now()
        if self.last_modified_time is None:
            self.last_modified_time = self.creation_time
        if self.due_time is not None and self.completion_time is not None:
            self.duration = self.completion_time - self.due_time

        # Do sanity-checks on input data
        if self.due_time is not None and self.completion_time is not None:
            if self.due_time > self.completion_time:
                raise ValueError("Due time cannot be after completion time")

        if self.start_time is not None and self.due_time is not None:
            if self.start_time > self.due_time:
                raise ValueError("Start time cannot be after due time")

        if self.start_time is not None and self.completion_time is not None:
            if self.start_time > self.completion_time:
                raise ValueError("Start time cannot be after completion time")
