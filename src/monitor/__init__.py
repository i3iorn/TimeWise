import logging
from typing import Dict, Any, List

from typeguard import typechecked

from src.monitor.event import EventChannel, Event
from src.base import BaseComponent

logger = logging.getLogger(__name__)


@typechecked
class MonitoringManager:
    """
    A singleton class to manage monitoring of components and monitors.
    """

    _instance = None  # Class variable to hold the singleton instance
    _initialized = False  # Class variable to track initialization

    def __new__(cls):
        """
        Creates a new instance of MonitoringManager if it doesn't exist.

        :return: The singleton instance of MonitoringManager.
        """
        if cls._instance is None:
            cls._instance = super(MonitoringManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the MonitoringManager instance with empty dictionaries for components and monitors.
        """
        if not self._initialized:
            self._components: Dict[int, BaseComponent] = {}
            self._monitors: Dict[int, Monitor] = {}
            self._initialized = True

    def add_component(self, component):
        """
        Adds a component to the monitoring manager.

        :param component: The component to be added.
        :type component: BaseComponent
        """
        if not hasattr(component, "_id"):
            raise AttributeError("Component must have an ID to be monitored")

        self._components[component._id] = component
        logger.debug(f"Component {component._id} added to MonitoringManager")

    def remove_component(self, component):
        """
        Removes a component from the monitoring manager.

        :param component: The component to be removed.
        :type component: BaseComponent
        """
        del self._components[component._id]
        logger.debug(f"Component {component._id} removed from MonitoringManager")

    def add_monitor(self, monitor: "Monitor") -> None:
        """
        Adds a monitor to the monitoring manager.

        :param monitor: The monitor to be added.
        :type monitor: Monitor
        """
        if not isinstance(monitor, Monitor):
            raise TypeError("Monitor must be an instance of the Monitor class")
        if not hasattr(monitor, "_id"):
            raise AttributeError("Monitor must have an ID to monitor components")
        if not hasattr(monitor, "receive_event"):
            raise AttributeError("Monitor must have a receive_event method to receive events")

        self._monitors[monitor._id] = monitor
        logger.debug(f"Monitor {monitor._id} added to MonitoringManager")

    def remove_monitor(self, monitor: "Monitor") -> None:
        """
        Removes a monitor from the monitoring manager.

        :param monitor: The monitor to be removed.
        :type monitor: Monitor
        """
        del self._monitors[monitor._id]
        logger.debug(f"Monitor {monitor._id} removed from MonitoringManager")

    def emit_event(self, event: Event) -> None:
        """
        Emits an event to all monitors in the monitoring manager.

        :param event: The event to be emitted.
        """
        logger.debug(f"Emitting event {event} to monitors")
        for monitor in self._monitors.values():
            if monitor.channels and event.channel in monitor.channels:
                monitor.receive_event(event)


@typechecked
class Monitor(BaseComponent):
    """
    A base class for monitors in the TimeWise application.
    """
    def __setup__(self, *args: Any, **kwargs: Any) -> None:
        """
        Sets up the monitor with default channels and an empty list of received events.

        :param args: The arguments to set up the monitor.
        :type args: Any
        :param kwargs: The keyword arguments to set up the monitor.
        :type kwargs: Any
        """
        self.channels = {EventChannel.GENERAL}
        self.received_events: List[Event] = []

    def handle_event(self, event: Event) -> None:
        """
        Handles an event. Must be implemented by subclasses.

        :param event: The event to handle.
        :type event: Event
        """
        raise NotImplementedError("Subclasses must implement this method")

    def receive_event(self, event: Event) -> None:
        """
        Receives an event and appends it to the list of received events.

        :param event: The event to receive.
        :type event: Event
        """
        if event.channel in self.channels:
            self.handle_event(event)
            self.received_events.append(event)
            logger.debug(f"Event {event} received by monitor {self._id}")


@typechecked
class MonitorableMixin:
    """
    A mixin class to make a component monitorable by adding it to the MonitoringManager.
    """

    def __setup__(self, *args: Any, **kwargs: Any) -> None:
        """
        Logs a debug message indicating the setup of the component for monitoring and adds the component to the MonitoringManager.

        :param args: The arguments to set up the component.
        :type args: Any
        :param kwargs: The keyword arguments to set up the component.
        :type kwargs: Any

        :raises NotImplementedError: If the method is not implemented by the subclass.
        """
        logger.debug(f"Setting up {self.__class__.__name__} for monitoring")
        MonitoringManager().add_component(self)
