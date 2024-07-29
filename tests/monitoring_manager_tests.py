import unittest

from src import MonitoringManager, EventChannel, Event
from src.base import BaseComponent
from src.monitor import Monitor


class TestMonitoringManager(unittest.TestCase):

    def test_singleton_instance_is_created(self):
        instance1 = MonitoringManager()
        instance2 = MonitoringManager()
        self.assertIs(instance1, instance2)

    def test_initializes_with_empty_dictionaries(self):
        manager = MonitoringManager()
        self.assertNotEqual(manager._components, {})
        self.assertNotEqual(manager._monitors, {})

    def test_adds_component_correctly(self):
        manager = MonitoringManager()
        component = BaseComponent()
        manager.add_component(component)
        self.assertIn(component._id, manager._components)

    def test_removes_component_correctly(self):
        manager = MonitoringManager()
        component = BaseComponent()
        manager.add_component(component)
        manager.remove_component(component)
        self.assertNotIn(component._id, manager._components)

    def test_adds_monitor_correctly(self):
        manager = MonitoringManager()
        monitor = Monitor()
        monitor.receive_event = lambda event: None
        manager.add_monitor(monitor)
        self.assertIn(monitor._id, manager._monitors)

    def test_removes_monitor_correctly(self):
        manager = MonitoringManager()
        monitor = Monitor()
        manager.add_monitor(monitor)
        manager.remove_monitor(monitor)
        self.assertNotIn(monitor._id, manager._monitors)

    def test_emits_event_to_all_monitors(self):
        class MockMonitor(Monitor):
            def __init__(self):
                super().__init__()
                self.channels = {EventChannel.GENERAL}
                self.received_events = []

            def receive_event(self, event):
                self.received_events.append(event)

        manager = MonitoringManager()
        monitor1 = MockMonitor()
        monitor2 = MockMonitor()
        manager.add_monitor(monitor1)
        manager.add_monitor(monitor2)
        event = Event(message="Test event")
        manager.emit_event(event)
        self.assertIn(event, monitor1.received_events)
        self.assertIn(event, monitor2.received_events)

    def test_does_not_emit_event_to_monitors_with_different_channels(self):
        class MockMonitor(Monitor):
            def __init__(self):
                super().__init__()
                self.channels = {EventChannel.GENERAL}
                self.received_events = []

            def receive_event(self, event):
                self.received_events.append(event)

        manager = MonitoringManager()
        monitor = MockMonitor()
        monitor.channels = {EventChannel.GENERAL}
        manager.add_monitor(monitor)
        event = Event(message="Test event", channel=EventChannel.GENERAL)
        manager.emit_event(event)
        self.assertIn(event, monitor.received_events)

        event_different_channel = Event(message="Test event", channel=EventChannel.TASK)
        manager.emit_event(event_different_channel)
        self.assertNotIn(event_different_channel, monitor.received_events)
