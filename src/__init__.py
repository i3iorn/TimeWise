from src import exceptions

import custom_logging
from src.config import Config
from database.engine import Engine as Database
from secrets_manager import SecretsManager
from src.timewise import TimeWise

logger = custom_logging.get_logger(name="main")


def main():
    Config()
    app = TimeWise(
        Database(),
        SecretsManager("TimeWise")
    )


if __name__ == "__main__":
    main()
