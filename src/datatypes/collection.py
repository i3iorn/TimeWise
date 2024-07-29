from typing import List, Set, TYPE_CHECKING, Union
import logging

from typeguard import typechecked

from src.base import BaseComponent
from src.datatypes.base import TMValueMixin

if TYPE_CHECKING:
    from src.datatypes.types import Tag, Reminder, Participant, Attachment
    from src.task import Task

logger = logging.getLogger(__name__)


@typechecked
class TimeWiseCollection(BaseComponent):
    """
    A class to represent a collection of TimeWise datatypes.
    Inherits from BaseComponent to provide unique ComponentID and setup/teardown methods.
    """
    pass


@typechecked
class TimeWiseSet(TMValueMixin, TimeWiseCollection):
    """
    A class to represent a set of TimeWise datatypes. Inherits from TimeWiseCollection and TMValueMixin to provide
    unique ComponentID and value management with validation. It also has most of the same functions as a set.
    """
    PRIMITIVE_TYPE = set

    def __add__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Adds two sets together and returns a new set.

        :param other: The other set to add.
        :type other: TimeWiseSet
        :return: The combined set.
        :rtype: TimeWiseSet
        """
        return TimeWiseSet(self._value.union(other._value))

    def __sub__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Subtracts one set from another and returns a new set.

        :param other: The other set to subtract.
        :type other: TimeWiseSet
        :return: The subtracted set.
        :rtype: TimeWiseSet
        """
        return TimeWiseSet(self._value.difference(other._value))

    def __or__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the union of two sets.

        :param other: The other set to union.
        :type other: TimeWiseSet
        :return: The union of the two sets.
        :rtype: TimeWiseSet
        """
        return TimeWiseSet(self._value.union(other._value))

    def __and__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the intersection of two sets.

        :param other: The other set to intersect.
        :type other: TimeWiseSet
        :return: The intersection of the two sets.
        :rtype: TimeWiseSet
        """
        return TimeWiseSet(self._value.intersection(other._value))

    def __xor__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the symmetric difference of two sets.

        :param other: The other set to compare.
        :type other: TimeWiseSet
        :return: The symmetric difference of the two sets.
        :rtype: TimeWiseSet
        """
        return TimeWiseSet(self._value.symmetric_difference(other._value))

    def __contains__(self, item: BaseComponent) -> bool:
        """
        Checks if an item is in the set.

        :param item: The item to check.
        :type item: BaseComponent
        :return: True if the item is in the set, False otherwise.
        :rtype: bool
        """
        return item in self._value

    def add(self, item: BaseComponent) -> None:
        """
        Adds an item to the set.

        :param item: The item to add.
        :type item: BaseComponent
        """
        self._value.add(item)

    def remove(self, item: BaseComponent) -> None:
        """
        Removes an item from the set.

        :param item: The item to remove.
        :type item: BaseComponent
        """
        self._value.remove(item)

    def clear(self) -> None:
        """
        Clears the set.
        """
        self._value.clear()

    def copy(self) -> "TimeWiseSet":
        """
        Returns a shallow copy of the set.

        :return: A shallow copy of the set.
        :rtype: TimeWiseSet
        """
        return TimeWiseSet(self._value.copy())

    def difference(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the difference between two sets.

        :param other: The other set to compare.
        :type other: TimeWiseSet
        :return: The difference between the two sets.
        :rtype: TimeWiseSet
        """
        return TimeWiseSet(self._value.difference(other._value))
    

@typechecked
class TagSet(TimeWiseSet):
    """
    A class to represent a list of tags in the TimeWise application.
    """

    @classmethod
    def _validate(cls, value: List["Tag"]) -> None:
        """
        Validates the provided list of tags.

        :param value: List of tags to validate.
        :type value: List[Tag]
        """
        logger.debug("Validating TagList with value: %s", value)
        # TODO: Implement validation logic


@typechecked
class TaskSet(TimeWiseSet):
    """
    A class to represent a list of tasks in the TimeWise application.
    """

    @classmethod
    def _validate(cls, value: List["Task"]) -> None:
        """
        Validates the provided list of tasks.

        :param value: List of tasks to validate.
        :type value: List[Task]
        """
        logger.debug("Validating TaskList with value: %s", value)
        # TODO: Implement validation logic


@typechecked
class ReminderSet(TimeWiseCollection):
    """
    A class to represent a set of reminders in the TimeWise application
    """

    @classmethod
    def _validate(cls, value: Set["Reminder"]) -> None:
        """
        Validates the provided set of reminders.

        :param value: Set of reminders to validate.
        :type value: Set[Reminder]
        """
        logger.debug("Validating ReminderSet with value: %s", value)
        # TODO: Implement validation logic


@typechecked
class ParticipantSet(TimeWiseCollection):
    """
    A class to represent a set of participants in the TimeWise application.
    """

    @classmethod
    def _validate(cls, value: Set["Participant"]) -> None:
        """
        Validates the provided set of participants.

        :param value: Set of participants to validate.
        :type value: Set[Participant]
        """
        logger.debug("Validating ParticipantSet with value: %s", value)
        # TODO: Implement validation logic


@typechecked
class AttachmentSet(TimeWiseCollection):
    @classmethod
    def _validate(cls, value: List["Attachment"]) -> None:
        """
        Validates the provided set of attachments.

        :param value: Set of attachments to validate.
        :type value: Set[Attachment]
        """
        logger.debug("Validating AttachmentSet with value: %s", value)
        # TODO: Implement validation logic
