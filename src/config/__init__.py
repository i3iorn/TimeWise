"""

The config module is a configuration module that reads all configuration files in the CONFIG_FOLDER directory and stores
the configuration values in a dictionary. The configuration values can be accessed by name and are case insensitive. The
configuration values can be nested dictionaries.

"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Union

import yaml

import src.exceptions as exceptions

CONFIG_FOLDER = Path("src/config")

TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict
}

with open(CONFIG_FOLDER.joinpath("value_types").absolute(), "r", encoding="utf8") as f:
    VALUE_TYPES = {key: TYPE_MAPPING[value] for key, value in [line.strip().split("=", 1) for line in f.readlines()]}


class ConfigFlag(Enum):
    ALLOW_NONE = 1
    DEEP_VALIDATION = 2


# Read all config files and set the environment variables
class Config:
    """
    The Config class is a configuration class that reads all configuration files in the CONFIG_FOLDER directory and
    stores the configuration values in a dictionary. The configuration values can be accessed by name and are case
    insensitive. The configuration values can be nested dictionaries.
    """
    def __init__(self, *args, load_files: bool = True, **kwargs) -> None:
        self._config = {}
        self.flags = set()

        # Find the root directory and set the environment variable
        os.environ["ROOT"] = str(Path(__file__).parent.parent.absolute())

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

        for key, value in kwargs.items():
            if key in ConfigFlag:
                if value:
                    self.flags.add(ConfigFlag[key])
                else:
                    self.flags.remove(ConfigFlag[key])

    def _read_config_files(self) -> None:
        """
        Read all configuration files in the CONFIG_FOLDER directory and update the configuration dictionary with the
        new values.

        :raises ConfigFilePermissionError: If a configuration file cannot be read
        :raises ConfigFileFormatError: If a configuration file is not in the correct format
        :raises ConfigValueTypeError: If a configuration value is not the correct type
        :raises ConfigKeyNotRecognizedError: If a configuration key is not recognized
        :raises ConfigurationNameCollisionError: If a configuration key already exists in the configuration

        :return: None
        :rtype: None
        """
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
            except (json.JSONDecodeError, yaml.YAMLError) as e:
                raise exceptions.ConfigFileFormatError(file) from e

            for key, value in conf.items():
                self._validate_new_value(key, value)

            self._config.update(conf)

    def _validate_new_value(self, key: str, value: str, parent: str = "") -> None:
        """
        Validate a new configuration value before adding it to the configuration dictionary. This method is recursive
        and will validate nested dictionaries.

        :param key: Configuration key
        :type key: str
        :param value: Configuration value
        :type value: str
        :param parent: Parent key
        :type parent: str

        :raises ConfigValueTypeError: If the value type is not correct
        :raises ConfigKeyNotRecognizedError: If the key is not recognized
        :raises ConfigurationNameCollisionError: If the key already exists in the configuration

        :return: None
        :rtype: None
        """
        # TODO: Add better support for nested dictionaries
        # TODO: Add support for range checking and other validation
        vtk = f"{parent}.{key}" if parent else key
        if vtk in VALUE_TYPES:
            if not isinstance(value, VALUE_TYPES[vtk]):
                raise exceptions.ConfigValueTypeError(vtk, VALUE_TYPES[vtk], type(value))
        elif (not parent or ConfigFlag.DEEP_VALIDATION in self.flags) and vtk not in VALUE_TYPES:
            raise exceptions.ConfigKeyNotRecognizedError(vtk)
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                self._validate_new_value(sub_key, sub_value, vtk)

    @staticmethod
    def _load_user_env_files() -> None:
        """
        Load the user environment file if it exists

        :raises EnvFileNotFoundError: If the environment file is not found

        :return: None
        :rtype: None
        """
        env_file = Path(os.environ.get("ROOT")).joinpath(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in [l for l in f.readlines() if l.strip() and not l.strip().startswith("#")]:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
        else:
            raise exceptions.EnvFileNotFoundError(env_file)

    def as_dict(self) -> dict:
        """
        Return the configuration as a dictionary
        :return:
        """
        return self._config

    def items(self) -> dict.items:
        """
        Return all configuration items as a list of dict.items
        :return:
        """
        return self.as_dict().items()

    def keys(self) -> dict.keys:
        """
        Return all configuration keys as a list of dict.keys
        :return:
        """
        return self.as_dict().keys()

    def values(self) -> dict.values:
        """
        Return all configuration values as a list of dict.values

        :return:
        """
        return self.as_dict().values()

    def __getitem__(self, item) -> Union[str, "Config", None]:
        """
        Get a configuration item by name and return it as a Config object if it is a dictionary. The item name is
        case-insensitive.

        :param item: The name of the configuration item
        :type item: str

        :raises ConfigurationNotSet: If the configuration item is not set

        :return: The configuration item
        :rtype: Union[str, "Config", None]
        """
        try:
            value = self._config[item.lower()]
            if isinstance(value, dict):
                return Config(value, load_files=False, **{flag.name: True for flag in self.flags})
            return value
        except KeyError:
            if ConfigFlag.ALLOW_NONE in self.flags:
                return None
            raise exceptions.ConfigurationNotSet(item)

    def __setitem__(self, key, value):
        """
        Set a new configuration item or update an existing one with a new value. The key is case-insensitive.

        :param key:
        :param value:
        :return:
        """
        key = key.lower()
        if key in self._config:
            raise exceptions.ConfigurationNameCollisionError(key)
        self._validate_new_value(key, value)
        self._config[key] = value.lower()

    def __delitem__(self, key):
        del self._config[key]

    def __contains__(self, item):
        return item in self._config
