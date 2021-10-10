import logging
import os
from threading import Thread
from time import sleep

import requests

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("Benchmark App")

host = os.getenv("ELB_HOST")
cluster_id = os.getenv("CLUSTER_ID")

endpoint = f'http://{host}/cluster{cluster_id}'


def main():
    """
    TODO : The container runs locally on your laptop and sends two separate threads:
    1000 GET requests sequentially.
    500 GET requests, then one minute sleep, followed by 1000 GET requests.
    """
    logger.info("Starting benchmark")

    thread1 = Thread(target=send1)
    thread2 = Thread(target=send2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    logger.info("Ending benchmark")


def send1():
    for i in range(1000):
        response = requests.get(endpoint)

    logger.info("Done send 1")


def send2():
    for i in range(500):
        response = requests.get(endpoint)

    logger.info("Done send 2 part 1/2, sleeping")
    sleep(60)

    for i in range(1000):
        response = requests.get(endpoint)

    logger.info("Done send 2 part 2/2")


if __name__ == '__main__':
    main()

