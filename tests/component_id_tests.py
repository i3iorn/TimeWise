import unittest

from src.base import ComponentID


class TestComponentID(unittest.TestCase):

    def test_initializes_with_unique_id(self):
        component1 = ComponentID()
        component2 = ComponentID()
        self.assertNotEqual(component1._id, component2._id)

    def test_increments_id_correctly(self):
        initial_id = ComponentID._id
        component = ComponentID()
        self.assertEqual(component._id, initial_id)
        self.assertEqual(ComponentID._id, initial_id + 1)

    def test_get_returns_correct_id(self):
        component = ComponentID()
        self.assertEqual(component.__get__(None, None), component._id)

    def test_set_raises_attribute_error(self):
        component = ComponentID()
        with self.assertRaises(AttributeError):
            component.__set__(None, 123)

    def test_str_returns_correct_format(self):
        component = ComponentID()
        self.assertEqual(str(component), f"ComponentID({component._id})")

    def test_multiple_instances_have_unique_ids(self):
        ids = {ComponentID()._id for _ in range(100)}
        self.assertEqual(len(ids), 100)

    def test_id_continues_incrementing_across_instances(self):
        initial_id = ComponentID._id
        for _ in range(10):
            ComponentID()
        self.assertEqual(ComponentID._id, initial_id + 10)

    def test_get_method_with_different_instances(self):
        component1 = ComponentID()
        component2 = ComponentID()
        self.assertNotEqual(component1.__get__(None, None), component2.__get__(None, None))

    def test_set_method_raises_error_on_different_instances(self):
        component1 = ComponentID()
        component2 = ComponentID()
        with self.assertRaises(AttributeError):
            component1.__set__(None, component2._id)
