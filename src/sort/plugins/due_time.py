from datetime import datetime, timedelta

from .interface import IPlugin


class SortPlugin(IPlugin):
    @property
    def reverse(self):
        return False

    def score(self, task):
        return task.due_time or (datetime.now()+timedelta(days=365))
