class ApplicationError(Exception):
    pass


class SetupError(ApplicationError):
    pass


class ConfigurationError(ApplicationError):
    pass


class SecretsError(ApplicationError):
    pass


class SecretsAccessError(SecretsError):
    pass


class EnvironmentVariableError(ApplicationError):
    pass


class DatabaseSetupError(ApplicationError):
    pass


class DatabaseError(ApplicationError):
    pass


class QueryBuilderException(DatabaseError):
    pass


class ConfigurationNameCollisionError(ConfigurationError):
    """
    Raised when a configuration key is already in use.

    Adds the key to the exception message.
    """
    def __init__(self, key):
        super().__init__(f"Configuration key '{key}' already exists. Use the update method to change the value.")


class MissingConfigurationFilesError(ConfigurationError):
    pass


class ConfigFilePermissionError(ConfigurationError):
    """
    Raised when a configuration file cannot be read.

    Adds the file name to the exception message.
    """
    def __init__(self, file):
        super().__init__(f"Permission denied to read configuration file: '{file}'.")


class ConfigValueTypeError(ConfigurationError):
    pass


class ConfigKeyNotRecognizedError(ConfigurationError):
    """
    Raised when a configuration key is not present in the VALUE_TYPES dictionary.
    """
    def __init__(self, key):
        super().__init__(f"Configuration key '{key}' not recognized. Doublecheck your spelling. If correct, add the "
                         f"key to the VALUE_TYPES dictionary.")


class ConfigurationNotSet(ConfigurationError):
    """
    Raised when a configuration key is not set.
    """
    def __init__(self, key):
        super().__init__(f"Configuration key '{key}' not set, check for typos. Add the key to the configuration file"
                         f"if necessary.")


class InitializationValueTypeError(ApplicationError):
    """
    Raised when the Config class is initialized with a value that is not a dictionary.

    Adds the type of the value to the exception message.
    """
    def __init__(self, class_name, expected_type, value_type):
        super().__init__(f"{class_name} expects a {expected_type} as the first argument, not a {value_type}.")


class ToManyArgumentsError(ApplicationError):
    """
    Raised when the Config class is initialized with more than one value.

    Adds the number of values to the exception message.
    """
    def __init__(self, class_name, expected_values, actual_values):
        super().__init__(f"{class_name} expects {expected_values} values, not {actual_values}.")


class EnvFileNotFoundError(FileNotFoundError):
    pass