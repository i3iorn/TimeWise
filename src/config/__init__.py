import os
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
                    content = f.read()
                    if len(content) == 0:
                        continue

                    self.__config.update(yaml.safe_load(content))

        env_path = Path(__file__).parent.parent.parent.joinpath('.env')
        if env_path.exists():
            with open(env_path, 'r', encoding="utf8") as f:
                for line in f:
                    if line.startswith('#') or line.strip() == '':
                        continue
                    key, value = line.strip().split('=', 1)
                    os.environ[key.upper()] = value

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
