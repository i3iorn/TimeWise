from typing import Optional, Type, Any, Tuple
import logging

from typeguard import typechecked

logger = logging.getLogger(__name__)


@typechecked
class ComponentID:
    """
    A class to represent a component ID. This class is used to uniquely identify a component and is used by the
    MonitoringManager to monitor the component. The ID is incremented every time a new component is created.
    """
    _id = 0  # Class variable to keep track of the last assigned ID

    def __init__(self) -> None:
        """
        Initializes a new ComponentID instance and assigns a unique ID.
        """
        self._id = ComponentID._id  # Assign the current ID to the instance
        ComponentID._id += 1  # Increment the class-level ID counter

    def __get__(self, instance: Optional[Type["BaseComponent"]], owner: Optional[Type["BaseComponent"]]) -> int:
        """
        Descriptor method to get the ID of the component.

        :param instance: The instance of the class where the descriptor is used.
        :type instance: type
        :param owner: The owner class of the instance.
        :type owner: type
        :return: The unique ID of the component.
        """
        return self._id

    def __set__(self, instance: Optional[Type["BaseComponent"]], value: Any) -> None:
        """
        Descriptor method to prevent setting the ID of the component.

        :param instance: The instance of the class where the descriptor is used.
        :param value: The value to set (not used).
        :raises AttributeError: Always raised to prevent setting the ID.
        """
        raise AttributeError("Cannot set the ID of a ComponentID")

    def __str__(self) -> str:
        """
        Returns a string representation of the ComponentID.

        :return: A string in the format 'ComponentID(<id>)'.
        """
        return f"ComponentID({self._id})"


@typechecked
class BaseComponent:
    """
    A base class for components that initializes a unique ComponentID and calls the __setup__ method for each class in its MRO.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes the component with a unique ComponentID and calls the __setup__ method for each class in its MRO.
        """
        self._id: ComponentID = ComponentID()
        for base in self.__class__.__mro__:
            if hasattr(base, '__setup__'):
                base.__setup__(self, *args, **kwargs)

    def teardown(self) -> None:
        """
        Calls the __teardown__ method for each class in the component's MRO if it is defined.
        """
        for base in self.__class__.__mro__:
            if hasattr(base, '__teardown__'):
                base.__teardown__(self)
