from .database.engine import Engine as Database
from .secrets_manager import SecretsManager
from threading import Lock


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

    def __init__(self, database: "Database", secrets_manager: "SecretsManager"):
        self.database = database
        self.secrets_manager = secrets_manager
