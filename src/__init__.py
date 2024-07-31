import logging
from typing import Union

from typeguard import typechecked
from src.datatypes.collection import TagSet, TaskSet, ReminderSet, ParticipantSet, AttachmentSet

from src.datatypes.types import Description, Notes
from src.datatypes.enums import Status, Priority
from src.monitor.event import EventChannel, Event
from src.monitor import MonitoringManager
from src.task import Task

logger = logging.getLogger(__name__)


@typechecked
class TimeWise:
    """
    A class to represent the TimeWise application.
    """
    def __init__(self) -> None:
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

    def add_task(self, task: "Task") -> None:
        """
        Adds a task to the TimeWise application.

        :param task: The task to be added.
        :type task: Task
        """
        self._tasks.add(task)
        self.monitoring_manager.emit_event(Event(f"Task '{task.title}' added", EventChannel.TASK))

    def remove_task(self, task: "Task") -> None:
        """
        Removes a task from the TimeWise application.

        :param task:
        :return:
        """
        self._tasks.remove(task)
        self.monitoring_manager.emit_event(Event(f"Task '{task.title}' removed", EventChannel.TASK))

    def clear_tasks(self) -> None:
        """
        Clears the list of tasks in the TimeWise application.

        :return:
        """
        self._tasks.clear()
        self.monitoring_manager.emit_event(Event("Tasks cleared", EventChannel.TASK))

    def get_task(self, title: str) -> Union["Task", None]:
        """
        Gets a task from the TimeWise application by title.

        :param title:
        :return:
        """
        for task in self._tasks:
            if task.title == title:
                return task
            else:
                raise ValueError(f"Task with title '{title}' not found")
        return None
