import unittest

from src.datatypes.base import TimeWiseDatatype, TMValueMixin


class TestTimeWiseDatatype(unittest.TestCase):
    def setUp(self):
        class MockTimeWiseDatatype(TimeWiseDatatype):
            PRIMITIVE_TYPE = str
            ALLOW_NONE = True
            ALLOW_EMPTY = True
            MAX_LENGTH = 12
            MIN_LENGTH = 2

        self.datatype = MockTimeWiseDatatype()

    def test_validates_value_correctly(self):
        self.datatype._validate("valid_value")

    def test_raises_error_for_invalid_type(self):
        with self.assertRaises(TypeError):
            self.datatype._validate(123)

    def test_raises_error_for_exceeding_max_length(self):
        with self.assertRaises(ValueError):
            self.datatype._validate("a" * 13)

    def test_raises_error_for_not_meeting_min_length(self):
        with self.assertRaises(ValueError):
            self.datatype._validate("a")

    def test_allows_none_value(self):
        self.datatype._validate(None)

    def test_allows_empty_value(self):
        self.datatype._validate("")

    def test_allows_value_within_length_limits(self):
        self.datatype._validate("a" * 10)


class TestTMValueMixin(unittest.TestCase):
    def setUp(self):
        class MockTMValueMixin(TMValueMixin):
            PRIMITIVE_TYPE = str
            ALLOW_NONE = True
            ALLOW_EMPTY = True

        self.mixin = MockTMValueMixin()

    def test_sets_value_correctly(self):
        self.mixin.__setup__("test_value")
        self.assertEqual(self.mixin._value, "test_value")

    def test_raises_error_for_invalid_type(self):
        with self.assertRaises(TypeError):
            self.mixin.__setup__(123)

    def test_allows_none_value(self):
        self.mixin.__setup__(None)
        self.assertIsNone(self.mixin._value)

    def test_allows_empty_value(self):
        self.mixin.__setup__("")
        self.assertEqual(self.mixin._value, "")

    def test_get_returns_correct_value(self):
        self.mixin.__setup__("test_value")
        self.assertEqual(self.mixin.__get__(None, None), "test_value")
