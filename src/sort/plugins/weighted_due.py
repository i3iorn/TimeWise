from datetime import datetime, timedelta

from .interface import IPlugin


class SortPlugin(IPlugin):
    @property
    def reverse(self):
        return True

    def score(self, task):
        try:
            delta = task.due_time - datetime.now()
        except TypeError:
            delta = timedelta(days=365)

        try:
            start_delta = task.start_time - datetime.now()
        except TypeError:
            start_delta = datetime.now() - datetime.now()

        if start_delta.days == 0 or delta.days == 0:
            return 0

        return delta.days / start_delta.days
