import importlib
from typing import List, Dict, Optional, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from src.timewise import TaskCollection
    from src.models.task import Task


class TaskSorter:
    def __init__(self, sort_plugin: str):
        self.__sort_plugin = importlib.import_module(f"src.sort.plugins.{sort_plugin}").SortPlugin()

    @property
    def sort_plugin(self):
        return self.__sort_plugin

    def sort(self, tasks: List[Type['Task']]) -> "TaskCollection":
        from src.timewise import TaskCollection
        return TaskCollection(sorted(tasks, key=self.__sort_plugin.score, reverse=self.__sort_plugin.reverse))
