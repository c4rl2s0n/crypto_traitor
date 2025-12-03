import logging
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

stop_event = threading.Event()


class AgentBase(ABC):
    name: str
    interval: timedelta

    def run(self):
        """
        perform a task in a fixed interval
        :return:
        """
        while not stop_event.is_set():
            task_start = datetime.now()
            self._do_task()

            # compute the time for running the next iteration
            next_iteration = task_start + self.interval
            waiting = next_iteration - datetime.now()
            logging.debug(f"Pause: {waiting}")

            # TODO: maybe apply the interval after finishing the task, ignoring the duration of the task?
            if waiting.total_seconds() < 0:
                logging.warn(f"the task was slower than the expected interval!")

            # wait until the next iteration
            while next_iteration > datetime.now():
                if stop_event.is_set():
                    logging.debug("Agent stopped")
                    return
                time.sleep(0.5)


    @abstractmethod
    def _do_task(self):
        """
        perform the task the agent is supposed in each iteration
        :return:
        """
        pass