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


def _send_demo(endpoint, request_count):
    for i in range(request_count):
        response = requests.get(endpoint)

    logger.info(f"Done {request_count} requests demo on endpoint: {endpoint}")

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

def benchmark_demo(endpoint: str, cluster_id: int) -> None:
    """
    50 GET requests on cluster1 and 150 GET requests on cluster2
    """
    logger.info(f"Benchmark: demo mode on cluster{cluster_id} @ {endpoint}")
    request_count = 50 if cluster_id == 1 else 150
    _send_demo(endpoint, request_count)
    