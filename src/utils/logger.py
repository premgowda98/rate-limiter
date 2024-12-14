"""Logging Configuration Module"""

import logging
import logging.handlers
import sys

from colorama import Fore, Style


class ColorFormater(logging.Formatter):
    """
    Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629
    """

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.formats = {
            logging.DEBUG: Style.BRIGHT + Fore.CYAN + self.fmt + Style.RESET_ALL,
            logging.INFO: Style.BRIGHT + Fore.GREEN + self.fmt + Style.RESET_ALL,
            logging.WARNING: Style.BRIGHT + Fore.YELLOW + self.fmt + Style.RESET_ALL,
            logging.ERROR: Style.BRIGHT + Fore.RED + self.fmt + Style.RESET_ALL,
            logging.CRITICAL: Style.BRIGHT + Fore.MAGENTA + self.fmt + Style.RESET_ALL,
        }

    def format(self, record):
        """
        Over ridding the format method
        """
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class Logger:
    """
    Custom Logger
    """

    LOG_MSG_FORMAT = "[%(asctime)s-%(levelname)s-%(filename)s:%(lineno)s] %(message)s"

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.stream_handler = self._set_stream_handler()
        self.logger.addHandler(self.stream_handler)

    def get_logger(self):
        """
        Returns the logger instance
        """
        return self.logger

    def _set_stream_handler(self):
        """
        Set the streaming handler
        """

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)

        return self._set_formater(stream_handler, color=True)

    def _set_file_handler(self):
        """
        Set the file handler
        """

        file_handler = logging.handlers.RotatingFileHandler(
            f"{self.name}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            mode="a",
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)

        return self._set_formater(file_handler)

    def _set_formater(self, handler: logging.handlers, color: bool = False):
        """
        Sets teh formatter for the handler
        """

        formatter = (
            ColorFormater(self.LOG_MSG_FORMAT)
            if color
            else logging.Formatter(self.LOG_MSG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S.%f")
        )
        handler.setFormatter(formatter)

        return handler
