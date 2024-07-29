import logging

from typeguard import typechecked
from src.datatypes.collection import TagSet, TaskSet, ReminderSet, ParticipantSet, AttachmentSet

from src.datatypes.types import Description, Notes
from src.datatypes.enums import Status, Priority
from src.monitor.event import EventChannel, Event
from src.monitor import MonitoringManager

logger = logging.getLogger(__name__)


@typechecked
class TimeWise:
    """
    A class to represent the TimeWise application.
    """
    def __init__(self):
        """
        Initializes the TimeWise application with empty collections and monitoring manager.
        """
        self.monitoring_manager = MonitoringManager()
        self._tasks = TaskSet()

    @property
    def tasks(self) -> TaskSet:
        """
        Property to access the list of tasks in the TimeWise application.

        :return: The list of tasks.
        :rtype: TaskSet
        """
        return self._tasks

    def add_task(self, task):
        """
        Adds a task to the TimeWise application.

        :param task: The task to be added.
        :type task: Task
        """
        self._tasks.add(task)
        self.monitoring_manager.emit_event(Event(f"Task '{task.title}' added", EventChannel.TASK))
