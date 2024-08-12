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
        scores = []
        if task.due_time is not None:
            diff = task.due_time - datetime.now()
            due_score = self.__map_to_range(diff.days)
            scores.append(due_score)
        else:
            scores.append(self.__map_to_range(5))

        if task.start_time is not None:
            start_diff = task.start_time - datetime.now()
            start_score = self.__map_to_range(start_diff.days)
            scores.append(start_score)

        if task.category == "Health":
            scores.append(self.__map_to_range(-1))

        scores.append(self.__map_to_range((int(task.priority) or 5) - 1))

        print(task.id, sum(scores) / len(scores))
        return sum(scores)
