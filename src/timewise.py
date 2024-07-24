import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from . import custom_logging
from .database.engine import TimeWiseEngine as Database
from .secrets_manager import SecretsManager
from threading import Lock
from .config import Config


logger = custom_logging.get_logger(name="TimeWise")


class APIInterface:
    """
    APIInterface class is responsible for managing the API interface of the TimeWise application. It expects an instance
    of the TimeWise class.
    """

    def __init__(self, timewise: "TimeWise"):
        self.timewise = timewise

    def __getattr__(self, item):
        return {
            "api_version": self.timewise.version,
            item: getattr(self.timewise, item),
        }


class TimeWise:
    """
    TimeWise class is the main class for the TimeWise application. It is a singleton class that is responsible for
    managing the entire application.

    It expects a database instance of type Database and a secrets_manager instance of type SecretsManager. Also the
    environment variable dictionary.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        os.environ["ROOT"] = str(Path(__file__).parent.parent.absolute())
        self.conf = Config()
        logger.info("Config loaded")

        self.db = Database(self.conf)
        self.secrets_manager = SecretsManager(project_name="TimeWise")
        self._api_interface = APIInterface(self)

        logger.info("TimeWise initialized")

    @property
    def api(self, ):
        return self._api_interface

    @property
    def name(self):
        return "TimeWise"

    @property
    def tasks(self):
        return self.db.get_tasks()

    @property
    def version(self):
        return self.conf._config["version"]
