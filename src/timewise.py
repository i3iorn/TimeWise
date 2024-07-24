import os
from pathlib import Path
from typing import TYPE_CHECKING

from . import custom_logging
from .database.engine import Engine as Database
from .secrets_manager import SecretsManager
from threading import Lock
from .config import Config


logger = custom_logging.get_logger(name="TimeWise")


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

        self.db = Database(self.conf),
        self.secrets_manager = SecretsManager(project_name="TimeWise")

        logger.info("TimeWise initialized")

    @property
    def version(self):
        return
