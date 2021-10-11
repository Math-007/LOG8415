import logging
from threading import Thread
from time import sleep

import requests

logger = logging.getLogger("Benchmark App")


def _send1(endpoint):
    for i in range(1000):
        response = requests.get(endpoint)

    logger.info("Done scenario 1 part 1/1")


def _send2(endpoint):
    for i in range(500):
        response = requests.get(endpoint)

    logger.info("Done scenario 2 part 1/2, sleeping")
    sleep(60)

    for i in range(1000):
        response = requests.get(endpoint)

    logger.info("Done scenario 2 part 2/2")


def benchmark(endpoint: str) -> None:
    """
    TODO : The container runs locally on your laptop and sends two separate threads:
    1000 GET requests sequentially.
    500 GET requests, then one minute sleep, followed by 1000 GET requests.
    """

    thread1 = Thread(target=_send1, kwargs={'endpoint': endpoint})
    thread2 = Thread(target=_send2, kwargs={'endpoint': endpoint})

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
