import unittest

import typeguard

from src.monitor import MonitorableMixin
from src.user import User


class TestUser(unittest.TestCase):

    def test_initializes_with_monitorable_mixin(self):
        user = User()
        self.assertIsInstance(user, MonitorableMixin)

    def test_validates_string_value_correctly(self):
        user = User()
        try:
            user._validate("valid_string")
        except Exception as e:
            self.fail(f"_validate raised {type(e).__name__} unexpectedly!")

    def test_raises_error_for_non_string_value(self):
        user = User()
        with self.assertRaises(typeguard.TypeCheckError):
            user._validate(123)

    def test_raises_error_for_empty_string_value(self):
        user = User()
        with self.assertRaises(ValueError):
            user._validate("")

