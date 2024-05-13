"""
    Логгер
"""
import logging
import sys
from logs.CustomFormatter import CustomFormatter
class CustomLogger:

    @staticmethod
    def getLogger(name):
        logger = logging.getLogger(name)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(CustomFormatter())
        logger.addHandler(handler)

        handler_file = logging.FileHandler('logs.log')
        handler_file.setLevel(logging.DEBUG)
        handler_file.setFormatter(logging.Formatter("%(asctime)s - %(message)s (%(filename)s:%(lineno)d)",datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(handler_file)

        logger.setLevel(logging.DEBUG)

        return logger