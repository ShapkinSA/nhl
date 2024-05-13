"""
    Форматтер для логгера (консоль и файл)
"""
import logging
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    green = '\x1b[32m'
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    # format = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = "%(asctime)s - %(message)s (%(filename)s:%(lineno)d)"


    FORMATS = {
        logging.DEBUG: yellow + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: red + format + reset,
        # logging.ERROR: bold_red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt,datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)