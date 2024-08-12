from abc import ABC, abstractmethod


class IPlugin(ABC):
    @property
    @abstractmethod
    def reverse(self):
        pass

    @abstractmethod
    def score(self, task):
        pass
