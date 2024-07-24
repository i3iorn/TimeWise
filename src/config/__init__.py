# Setup and Configuration for the application
import json
import os
from pathlib import Path
from typing import List, Tuple, Any

import yaml

import src.exceptions as exceptions

CONFIG_FOLDER = Path("config")

with open(CONFIG_FOLDER.joinpath("value_types").absolute(), "r", encoding="utf8") as f:
    VALUE_TYPES = {key: eval(value) for key, value in [line.strip().split("=") for line in f.readlines()]}


# Read all config files and set the environment variables
class Config:
    def __init__(self, *args, load_files: bool = True):
        self._config = {}

        if args:
            if not isinstance(args[0], dict):
                raise exceptions.InitializationValueTypeError("Config", "dict", type(args[0]))
            elif len(args) > 1:
                raise exceptions.ToManyArgumentsError("Config", 1, len(args))
        if args:
            self._config.update(args[0])
        if load_files:
            self._read_config_files()
        self._load_user_env_files()

    def _read_config_files(self):
        for file in [
            f
            for f in os.listdir(CONFIG_FOLDER)
            if CONFIG_FOLDER.joinpath(f).is_file() and
               CONFIG_FOLDER.joinpath(f).suffix in [".json", ".env", ".yaml"]
        ]:
            try:
                with open(CONFIG_FOLDER.joinpath(file).absolute(), "r") as f:
                    if file.endswith(".json"):
                        conf = json.load(f)
                    elif file.endswith(".env"):
                        conf = {key: value for key, value in [line.strip().split("=") for line in f.readlines()]}
                    elif file.endswith(".yaml"):
                        conf = yaml.safe_load(f)
            except PermissionError as e:
                raise exceptions.ConfigFilePermissionError(file) from e

            for key, value in conf.items():
                self._validate_new_value(key, value)

            self._config.update(conf)

    @classmethod
    def _validate_new_value(cls, key: str, value: str, parent: str = "") -> None:
        vtk = f"{parent}.{key}" if parent else key
        if vtk in VALUE_TYPES:
            if not isinstance(value, VALUE_TYPES[vtk]):
                raise exceptions.ConfigValueTypeError(vtk, VALUE_TYPES[vtk], type(value))
        elif not parent and vtk not in VALUE_TYPES:
            raise exceptions.ConfigKeyNotRecognizedError(vtk)
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                cls._validate_new_value(sub_key, sub_value, vtk)

    def _load_user_env_files(self):
        env_file = Path(os.environ.get("ROOT")).joinpath(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in [l for l in f.readlines() if l.strip() and not l.strip().startswith("#")]:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
        else:
            raise exceptions.EnvFileNotFoundError(env_file)

    def as_dict(self) -> dict:
        return self._config

    def items(self) -> dict.items:
        return self.as_dict().items()

    def keys(self) -> dict.keys:
        return self.as_dict().keys()

    def values(self) -> dict.values:
        return self.as_dict().values()

    def __getitem__(self, item):
        try:
            value = self._config[item.lower()]
            if isinstance(value, dict):
                return Config(value, load_files=False)
            return value
        except KeyError:
            raise exceptions.ConfigurationNotSet(item)

    def __setitem__(self, key, value):
        key = key.lower()
        if key in self._config:
            raise exceptions.ConfigurationNameCollisionError(key)
        self._validate_new_value(key, value)
        self._config[key] = value.lower()

    def __delitem__(self, key):
        del self._config[key]

    def __contains__(self, item):
        return item in self._config
