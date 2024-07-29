from dataclasses import dataclass
import logging
from enum import Enum

from typeguard import typechecked

logger = logging.getLogger(__name__)


class EventChannel(Enum):
    """
    An enumeration class to represent different event channels.
    """
    GENERAL = "general"
    TASK = "task"


@typechecked
@dataclass
class Event:
    """
    A class to represent an event that can be emitted by components and received by monitors.
    """
    message: str
    channel: EventChannel = EventChannel.GENERAL

    def __post_init__(self) -> None:
        """
        Validates the event channel and message.

        :raises TypeError: If the event channel is not a valid EventChannel or the message is not a string.
        """
        if not isinstance(self.channel, EventChannel):
            raise TypeError("Event channel must be a valid EventChannel")
        if not isinstance(self.message, str):
            raise TypeError("Event message must be a string")

    def __str__(self) -> str:
        """
        Returns a string representation of the Event.

        :return: A string in the format 'Event(name, payload)'.
        """
        return f"Event({self.channel}, {self.message})"
