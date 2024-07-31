from typeguard import typechecked

from src.base import BaseComponent
from src.monitor import MonitorableMixin


@typechecked
class User(MonitorableMixin, BaseComponent):
    """
    A class to represent a user in the TimeWise application.
    """

    @classmethod
    def _validate(cls, value: str) -> None:
        """
        Validates the user.

        :param value: The user to validate.
        :type value: str
        """
        if not isinstance(value, str):
            raise TypeError("User must be a string")
        if not value:
            raise ValueError("User cannot be empty")
