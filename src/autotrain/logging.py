import sys
import logging
from dataclasses import dataclass

try:
    from loguru import logger as _loguru_logger
    LOGURU_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - fallback when loguru is missing
    LOGURU_AVAILABLE = False
    _loguru_logger = logging.getLogger("autotrain")


IS_ACCELERATE_AVAILABLE = False

try:
    from accelerate.state import PartialState

    IS_ACCELERATE_AVAILABLE = True
except ImportError:
    pass


@dataclass
class Logger:
    """
    A custom logger class that sets up and manages logging configuration.

    Methods
    -------
    __post_init__():
        Initializes the logger with a specific format and sets up the logger.

    _should_log(record):
        Determines if a log record should be logged based on the process state.

    setup_logger():
        Configures the logger to output to stdout with the specified format and filter.

    get_logger():
        Returns the configured logger instance.
    """

    def __post_init__(self):
        if LOGURU_AVAILABLE:
            self.log_format = (
                "<level>{level: <8}</level> | "
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )
        else:
            self.log_format = (
                "%(levelname)-8s | %(asctime)s | %(name)s:%(funcName)s:%(lineno)d - "
                "%(message)s"
            )
        self.logger = _loguru_logger
        self.setup_logger()

    def _should_log(self, record):
        if not IS_ACCELERATE_AVAILABLE:
            return None
        return PartialState().is_main_process

    def setup_logger(self):
        if LOGURU_AVAILABLE:
            self.logger.remove()
            self.logger.add(
                sys.stdout,
                format=self.log_format,
                filter=lambda x: self._should_log(x) if IS_ACCELERATE_AVAILABLE else None,
            )
        else:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(self.log_format))
            if not self.logger.handlers:
                self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_logger(self):
        return self.logger
