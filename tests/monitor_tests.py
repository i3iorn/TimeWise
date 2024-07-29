import unittest

from src import EventChannel, Event
from src.monitor import Monitor


class TestMonitor(unittest.TestCase):

    def test_initializes_with_default_channel_and_empty_events(self):
        monitor = Monitor()
        self.assertEqual(monitor.channels, {EventChannel.GENERAL})
        self.assertEqual(monitor.received_events, [])

    def test_raises_not_implemented_error_for_handle_event(self):
        monitor = Monitor()
        event = Event(message="Test event")
        with self.assertRaises(NotImplementedError):
            monitor.handle_event(event)

    def test_receives_event_and_appends_to_received_events(self):
        class MockMonitor(Monitor):
            def handle_event(self, event):
                pass

        monitor = MockMonitor()
        event = Event(message="Test event")
        monitor.receive_event(event)
        self.assertIn(event, monitor.received_events)

    def test_does_not_receive_event_if_handle_event_raises_error(self):
        class MockMonitor(Monitor):
            def handle_event(self, event):
                raise ValueError("Error in handling event")

        monitor = MockMonitor()
        event = Event(message="Test event")
        with self.assertRaises(ValueError):
            monitor.receive_event(event)
        self.assertNotIn(event, monitor.received_events)

    def test_does_not_receive_event_if_channel_not_in_channels(self):
        class MockMonitor(Monitor):
            def handle_event(self, event):
                pass

        monitor = MockMonitor()
        event = Event(message="Test event", channel=EventChannel.TASK)
        monitor.receive_event(event)
        self.assertNotIn(event, monitor.received_events)
