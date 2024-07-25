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
    """
    Raised when a configuration value is not the correct type.

    Adds the key and the expected type to the exception message.
    """
    def __init__(self, key, expected_type, value_type):
        super().__init__(f"Configuration key '{key}' must be of type {expected_type}, not {value_type}.")


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


class ConfigFileFormatError(ConfigurationError):
    """
    Raised when a configuration file is not in the correct format.
    """
    def __init__(self, file):
        super().__init__(f"Configuration file '{file}' is not in the correct format.")


class TitleException(ValueError):
    """
    Base class for exceptions related to the title of a task.
    """
    pass


class ToLongTitleException(TitleException):
    """
    Raised when a title is too long.
    """
    def __init__(self, title_length, max_length):
        super().__init__(f"Title is {title_length} characters long, but must be less than {max_length} characters.")


class IntegerException(ValueError):
    """
    Base class for exceptions related to integers.
    """
    pass


class DateTimeException(ValueError):
    pass


class DateTimeFormatException(DateTimeException):
    pass


class TimeException(ValueError):
    pass


class TimeFormatException(TimeException):
    pass


class DateException(ValueError):
    pass


class DateFormatException(DateException):
    pass


class ToLargeIntegerException(IntegerException):
    pass


class ToSmallIntegerException(IntegerException):
    pass


class StringException(ValueError):
    pass


class ToLongStringException(StringException):
    pass


class FloatException(ValueError):
    pass


class ToLargeFloatException(FloatException):
    pass


class ToSmallFloatException(FloatException):
    pass


class BooleanException(ValueError):
    pass


class ListException(ValueError):
    pass


class DictException(ValueError):
    pass


class ToLargeDictException(DictException):
    pass


class ToSmallDictException(DictException):
    pass


class ToDeepDictException(DictException):
    pass