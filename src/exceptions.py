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
