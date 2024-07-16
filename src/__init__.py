import os
from pathlib import Path

from src import exceptions

import custom_logging
from database.engine import Engine as Database
from secrets_manager import SecretsManager
from src.timewise import TimeWise

logger = custom_logging.get_logger(name="main")


def load_environment_variables():
    logger.info("Loading environment variables")
    # Load environment variables from .env file
    try:
        with open(Path(__file__).parent.parent.joinpath(".env"), "r") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue

                key, value = line.strip().split("=", 1)
                os.environ[key] = value

    except Exception as e:
        raise exceptions.EnvironmentVariableError("Environment variable loading failed") from e


def setup_directories():
    logger.info("Setting up directories")
    # Verify that the required directories are present
    try:
        Path(os.environ["DB_HOST"]).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise exceptions.ConfigurationError("Directory setup failed") from e


def main():
    load_environment_variables()
    app = TimeWise(
        Database(),
        SecretsManager("TimeWise")
    )


if __name__ == "__main__":
    main()
