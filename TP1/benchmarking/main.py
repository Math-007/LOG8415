import logging
from threading import *   
import time
import asyncio
import aiohttp
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("Benchmark App")

sem = Semaphore(1)
get_url = 'https://api.github.com'

async def main():
    logger.info("Starting benchmark")
    """
    TODO : The container runs locally on your laptop and sends two separate threads:
    1000 GET requests sequentially.
    500 GET requests, then one minute sleep, followed by 1000 GET requests.
    """
    # y = Thread(target=send2, args=())
    # x = Thread(target=send1, args=())
    # y.start()
    # x.start()
    await asyncio.gather(send1(), send2())

async def send1():
    # sem.acquire()
    async with aiohttp.ClientSession() as session:
        for i in range(1000):
            async with session.get(get_url) as resp:
                answer = await resp.json()
                # print(answer)
                print('message '+str(i)+' de thread 1')
            # sem.release()

async def send2():
    # sem.acquire()
    async with aiohttp.ClientSession() as session:
        for i in range(500):
            async with session.get(get_url) as resp:
                answer = await resp.json()
                # print(answer)
                print('message '+str(i)+' de thread 2')
            # sem.release()
        time.sleep(60)
        # sem.acquire()
        for i in range(1000):
            async with session.get(get_url) as resp:
                answer = await resp.json()
                # print(answer)
                print('message '+str(i)+' de thread 2')
            # sem.release()

async def get():
    async with aiohttp.ClientSession() as session:
        for i in range(10):
            async with session.get(get_url) as resp:
                answer = await resp.json()
if __name__ == '__main__':
    asyncio.run(main())

