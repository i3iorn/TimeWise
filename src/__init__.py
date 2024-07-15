import os
from pathlib import Path

import exceptions

import custom_logging
from database.sqlite import SQLite
from secrets_manager import SecretsManager

logger = custom_logging.get_logger(name="main")


def load_evironment_variables():
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


def setup_database():
    logger.info("Setting up database")
    # Verify that the database is setup
    try:
        SQLite(os.environ["DB_HOST"]).connect()
    except Exception as e:
        raise exceptions.DatabaseSetupError("Database setup failed") from e


def verify_secrets_access():
    logger.info("Verifying Secrets access")
    # Verify that the secrets are accessible
    try:
        SecretsManager("TimeWise")
    except Exception as e:
        raise exceptions.SecretsAccessError("Secrets access failed") from e


def setup():
    # Read environment variables
    load_evironment_variables()

    # Verify Secrets access
    verify_secrets_access()

    # Verify that the database is setup
    setup_database()

    # Verify that the required directories are present
    # setup_directories()

    # Verify that the required files are present
    # setup_files()

    # Verify that the required environment variables are set
    # setup_environment_variables()

    # Verify that the required services are running
    # setup_services()

    # Verify that the required packages are installed
    # setup_packages()


def main():
    try:
        setup()
    except Exception as e:
        raise exceptions.SetupError("Setup failed") from e


if __name__ == "__main__":
    main()
