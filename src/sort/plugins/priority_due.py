import math
from datetime import timedelta, datetime

from .interface import IPlugin


class SortPlugin(IPlugin):
    @property
    def reverse(self):
        return False

    def __map_to_range(self, x):
        return math.tanh(x)

    def score(self, task):
        dt = (task.due_time or datetime.now() + timedelta(days=31))
        diff = dt - datetime.now()

        due_score = self.__map_to_range(diff.days) - (math.pow(diff.seconds, 0.05 / int(task.priority)) if dt < datetime.now() else 0)

        priority_score = self.__map_to_range((int(task.priority) or 5) - 1)

        print(task.id, priority_score, due_score)
        return priority_score + due_score
