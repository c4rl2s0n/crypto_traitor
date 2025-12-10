import logging
import sys

log_format = "{\"time\": \"%(asctime)s\", \"thread\": \"%(threadName)s\" \"level\": \"%(levelname)s\", \"message\": \"%(message)s\"}"


def setup():
    """
    Setup logging to file and stdout
    :return:
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # capture everything, handlers will filter

    # StreamHandler for stdout (e.g., INFO and below)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)  # logs INFO and above
    stdout_formatter = logging.Formatter(log_format)

    stdout_handler.setFormatter(stdout_formatter)

    # FileHandler for file (e.g., WARNING and above)
    file_handler = logging.FileHandler("log.jsonl")
    file_handler.setLevel(logging.WARNING)  # logs WARNING, ERROR, CRITICAL
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
