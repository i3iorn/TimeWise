import unittest

from src.base import BaseComponent


class TestBaseComponent(unittest.TestCase):

    def test_initializes_with_unique_id(self):
        component = BaseComponent()
        self.assertIsNotNone(component._id)

    def test_calls_setup_methods_for_all_bases(self):
        class MockMixin1:
            def __setup__(self):
                self.setup_called_1 = True

        class MockMixin2:
            def __setup__(self):
                self.setup_called_2 = True

        class TestComponent(BaseComponent, MockMixin1, MockMixin2):
            pass

        component = TestComponent()
        self.assertTrue(component.setup_called_1)
        self.assertTrue(component.setup_called_2)

    def test_does_not_call_setup_if_not_defined(self):
        class MockMixin:
            pass

        class TestComponent(BaseComponent, MockMixin):
            pass

        component = TestComponent()
        self.assertFalse(hasattr(component, 'setup_called'))

    def test_initializes_with_args_and_kwargs(self):
        class MockMixin:
            def __setup__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        class TestComponent(BaseComponent, MockMixin):
            pass

        component = TestComponent(1, 2, key="value")
        self.assertEqual(component.args, (1, 2))
        self.assertEqual(component.kwargs, {"key": "value"})

    def test_calls_teardown_methods_for_all_bases(self):
        class MockMixin1:
            def __teardown__(self):
                self.teardown_called_1 = True

        class MockMixin2:
            def __teardown__(self):
                self.teardown_called_2 = True

        class TestComponent(BaseComponent, MockMixin1, MockMixin2):
            pass

        component = TestComponent()
        component.teardown()
        self.assertTrue(component.teardown_called_1)
        self.assertTrue(component.teardown_called_2)