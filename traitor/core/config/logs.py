import logging
import sys


import logging
import json
import traceback

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "message": record.getMessage(),
        }
        # include exception info if available
        if record.exc_info:
            log_record["exception_type"] = str(record.exc_info[0].__name__)
            log_record["exception_message"] = str(record.exc_info[1])
            log_record["stack_trace"] = "".join(traceback.format_exception(*record.exc_info))
        return json.dumps(log_record)


log_format = "[%(asctime)s] (%(threadName)s) <%(levelname)s>: %(message)s"


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
    file_handler.setFormatter(JsonFormatter())

    # Add handlers to logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
