from .interface import IPlugin


class SortPlugin(IPlugin):
    @property
    def reverse(self):
        return False

    def score(self, task):
        return task.priority or 5