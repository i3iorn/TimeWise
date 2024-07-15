import logging


def add_logging_level(level_name, level_num, method_name=None):
    """Add a new logging level to the logging module"""
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise ValueError(f"Logging level {level_name} already exists")

    if hasattr(logging, method_name):
        raise ValueError(f"Logging method {method_name} already exists")

    logging.addLevelName(level_num, level_name)

    def log(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    setattr(logging.Logger, method_name, log)

    def log_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    setattr(logging, method_name, log_root)


add_logging_level("NOTICE", 25)
add_logging_level("VERBOSE", 15)
add_logging_level("TRACE", 5)


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;5;8m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            5: self.grey + self.fmt + self.reset,
            logging.DEBUG: self.grey + self.fmt + self.reset,
            15: self.blue + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            25: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    def formatException(self, ei):
        result = super().formatException(ei)
        return f"{self.red}{result}{self.reset}"

    def formatMessage(self, record):
        result = super().formatMessage(record)
        return f"{self.blue}{result}{self.reset}"

    def formatStack(self, stack_info):
        result = super().formatStack(stack_info)
        return f"{self.red}{result}{self.reset}"

    def formatTime(self, record, datefmt=None):
        result = super().formatTime(record, datefmt)
        return f"{self.grey}{result}{self.reset}"


class CustomConsoleHandler(logging.StreamHandler):
    """Logging colored console handler, adapted from https://stackoverflow.com/a/56944256/3638629"""

    def __init__(self):
        super().__init__()
        self.setFormatter(CustomFormatter(fmt="%(asctime)s - %(levelname)8s - %(message)s"))


class CustomLogger(logging.Logger):
    """Logging colored logger, adapted from https://stackoverflow.com/a/56944256/3638629"""

    def __init__(self, name):
        super().__init__(name)
        self.addHandler(CustomConsoleHandler())


def get_logger(name, level: int = logging.INFO):
    new_logger = CustomLogger(name)
    new_logger.setLevel(level)
    new_logger.info(f"Logger '{name}' created")
    return new_logger
