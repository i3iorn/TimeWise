import logging
from typing import Optional, Type, Any

import typeguard
from typeguard import typechecked

from src.base import BaseComponent

logger = logging.getLogger(__name__)


@typechecked
class TMValueMixin:
    """
    A mixin class to handle value management with validation for TimeWise components.
    """
    ALLOW_EMPTY = False
    ALLOW_NONE = False
    PRIMITIVE_TYPE = str

    def __setup__(self, *args, **kwargs) -> None:
        """
        Sets up the mixin with a given value after validation.

        :param args: The arguments to set the value.
        :type args: Any
        :param kwargs: The keyword arguments to set the value.
        :type kwargs: Any

        :raises ValueError: If the value is invalid.
        """
        value = args[0] if args else None
        try:
            self._validate(value)
        except typeguard.TypeCheckError as e:
            if not (self.ALLOW_NONE and value is None) and not (self.ALLOW_EMPTY and not value):
                raise TypeError(f"Invalid value for {self.__class__.__name__}: {e}")

        logger.debug(f"Setting value for {self.__class__.__name__} to {value}")
        self._value = value

    def __get__(self, instance: Optional[Type["BaseComponent"]], owner: Optional[Type]) -> Any:
        """
        Descriptor method to get the value.

        :param instance: The instance of the class where the descriptor is used.
        :type instance: type
        :param owner: The owner class of the instance.
        :type owner: type
        :return: The value of the component.
        :rtype: Any
        """
        return self._value

    def __set__(self, instance: type, value: Any) -> None:
        """
        Descriptor method to set the value.

        :param instance: The instance of the class where the descriptor is used.
        :type instance: type
        :param value: The value to be set.
        :type value: Any
        """
        self._value = value

    @classmethod
    def _validate(cls, value: Any) -> None:
        """
        Validates the given value. Must be implemented by subclasses.

        :param value: The value to be validated.
        :type value: Any
        :raises NotImplementedError: Always raised to indicate that subclasses must implement this method.
        """
        if (cls.ALLOW_NONE and value is None) or (cls.ALLOW_EMPTY and not value):
            return

        if not isinstance(value, cls.PRIMITIVE_TYPE):
            raise TypeError(f"Value must be of type {cls.PRIMITIVE_TYPE} not {type(value)}")

        if hasattr(cls, "MAX_LENGTH") and len(value) > cls.MAX_LENGTH:
            raise ValueError(f"Value exceeds maximum length of {cls.MAX_LENGTH}")
        if hasattr(cls, "MIN_LENGTH") and len(value) < cls.MIN_LENGTH:
            raise ValueError(f"Value does not meet minimum length of {cls.MIN_LENGTH}")


