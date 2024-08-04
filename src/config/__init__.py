import yaml
from pathlib import Path
from typeguard import typechecked


@typechecked
class Config:
    def __init__(self):
        self.__config = {}

        for file in Path(__file__).parent.iterdir():
            if file.suffixes == ['.conf', '.yaml']:
                with open(file, 'r', encoding="utf8") as f:
                    self.__config.update(yaml.safe_load(f))

    @property
    def config(self):
        return self.__config

    def get(self, key, default=None):
        return self.__config.get(key, default)

    def __getitem__(self, item):
        return self.__config[item]

    def __setitem__(self, key, value):
        if not isinstance(value, type(self.__config[key])):
            raise TypeError(f"Expected {type(self.__config[key])}, got {type(value)}")

        self.__config[key] = value
