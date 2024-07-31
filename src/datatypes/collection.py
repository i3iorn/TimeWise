from typing import List, Set, TYPE_CHECKING, Union
import logging

from typeguard import typechecked

from src.base import BaseComponent
from src.datatypes.mixins import TMValueMixin

if TYPE_CHECKING:
    from src.datatypes.types import Tag, Reminder, Participant, Attachment
    from src.task import Task

logger = logging.getLogger(__name__)


@typechecked
class TimeWiseSet(TMValueMixin, BaseComponent):
    """
    A class to represent a set of TimeWise datatypes. Inherits from TimeWiseCollection and TMValueMixin to provide
    unique ComponentID and value management with validation. It also has most of the same functions as a set.

    # Example usage:

    from src.datatypes.collection import TimeWiseSet
    from src.datatypes.types import Tag

    tag_set = TimeWiseSet({Tag("tag1"), Tag("tag2")})
    tag_set.add(Tag("tag3"))
    tag_set.remove(Tag("tag1"))
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
        return self.__class__(self._value.union(other._value))

    def __sub__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Subtracts one set from another and returns a new set.

        :param other: The other set to subtract.
        :type other: TimeWiseSet
        :return: The subtracted set.
        :rtype: TimeWiseSet
        """
        return self.__class__(self._value.difference(other._value))

    def __or__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the union of two sets.

        :param other: The other set to union.
        :type other: TimeWiseSet
        :return: The union of the two sets.
        :rtype: TimeWiseSet
        """
        return self.__class__(self._value.union(other._value))

    def __and__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the intersection of two sets.

        :param other: The other set to intersect.
        :type other: TimeWiseSet
        :return: The intersection of the two sets.
        :rtype: TimeWiseSet
        """
        return self.__class__(self._value.intersection(other._value))

    def __xor__(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the symmetric difference of two sets.

        :param other: The other set to compare.
        :type other: TimeWiseSet
        :return: The symmetric difference of the two sets.
        :rtype: TimeWiseSet
        """
        return self.__class__(self._value.symmetric_difference(other._value))

    def __contains__(self, item: BaseComponent) -> bool:
        """
        Checks if an item is in the set.

        :param item: The item to check.
        :type item: BaseComponent
        :return: True if the item is in the set, False otherwise.
        :rtype: bool
        """
        return item in self._value

    def __len__(self):
        """
        Returns the length of the set.

        :return: The length of the set.
        :rtype: int
        """
        return len(self._value)

    def __iter__(self):
        """
        Returns an iterator for the set.

        :return: An iterator for the set.
        :rtype: Iterator
        """
        return iter(self._value)

    def __getitem__(self, item: int) -> BaseComponent:
        """
        Returns an item from the set by index.

        :param item: The index of the item.
        :type item: int
        :return: The item at the index.
        :rtype: BaseComponent
        """
        return list(self._value)[item]

    def __setitem__(self, key: int, value: BaseComponent) -> None:
        """
        Sets an item in the set by index.

        :param key: The index of the item.
        :type key: int
        :param value: The value to set.
        :type value: BaseComponent

        :raises NotImplementedError: Always raised to indicate that items cannot be set in a set.
        """
        raise NotImplementedError("Cannot set items in a set.")

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
        return self.__class__(self._value.copy())

    def difference(self, other: Union["TimeWiseSet", Set[BaseComponent]]) -> "TimeWiseSet":
        """
        Returns the difference between two sets.

        :param other: The other set to compare.
        :type other: TimeWiseSet
        :return: The difference between the two sets.
        :rtype: TimeWiseSet
        """
        return self.__class__(self._value.difference(other._value))
    

@typechecked
class TagSet(TimeWiseSet):
    """
    A class to represent a list of tags in the TimeWise application.
    """
    pass


@typechecked
class TaskSet(TimeWiseSet):
    """
    A class to represent a list of tasks in the TimeWise application.
    """
    pass


@typechecked
class ReminderSet(TimeWiseSet):
    """
    A class to represent a set of reminders in the TimeWise application
    """
    pass


@typechecked
class ParticipantSet(TimeWiseSet):
    """
    A class to represent a set of participants in the TimeWise application.
    """
    pass


@typechecked
class AttachmentSet(TimeWiseSet):
    """
    A class to represent a set of attachments in the TimeWise application.
    """
    pass
