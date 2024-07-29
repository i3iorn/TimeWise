import unittest

from src import Event, EventChannel


class TestEvent(unittest.TestCase):

    def test_initializes_with_default_channel(self):
        event = Event(message="Test message")
        self.assertEqual(event.channel, EventChannel.GENERAL)

    def test_initializes_with_custom_channel(self):
        event = Event(message="Test message", channel=EventChannel.GENERAL)
        self.assertEqual(event.channel, EventChannel.GENERAL)

    def test_initializes_with_message(self):
        message = "Test message"
        event = Event(message=message)
        self.assertEqual(event.message, message)

    def test_raises_type_error_for_invalid_channel(self):
        with self.assertRaises(TypeError):
            Event(message="Test message", channel="invalid_channel")

    def test_raises_type_error_for_missing_message(self):
        with self.assertRaises(TypeError):
            Event()

    def initializes_with_default_channel(self):
        event = Event(message="Test message")
        self.assertEqual(event.channel, EventChannel.GENERAL)

    def initializes_with_custom_channel(self):
        event = Event(message="Test message", channel=EventChannel.GENERAL)
        self.assertEqual(event.channel, EventChannel.GENERAL)

    def initializes_with_message(self):
        message = "Test message"
        event = Event(message=message)
        self.assertEqual(event.message, message)

    def raises_type_error_for_invalid_channel(self):
        with self.assertRaises(TypeError):
            Event(message="Test message", channel="invalid_channel")

    def raises_type_error_for_missing_message(self):
        with self.assertRaises(TypeError):
            Event()

    def initializes_with_empty_message(self):
        event = Event(message="")
        self.assertEqual(event.message, "")

    def raises_type_error_for_non_string_message(self):
        with self.assertRaises(TypeError):
            Event(message=123)

    def str_returns_correct_format(self):
        message = "Test message"
        event = Event(message=message)
        self.assertEqual(str(event), f"Event(message={message}, channel={EventChannel.GENERAL})")

    def initializes_with_different_channels(self):
        for channel in EventChannel:
            event = Event(message="Test message", channel=channel)
            self.assertEqual(event.channel, channel)
