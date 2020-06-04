import logging

from rq import Worker as Worker

from .settings import WORKER_LOG_FILE, WORKER_LOG_LEVEL

logging.basicConfig(level=WORKER_LOG_LEVEL, filename=WORKER_LOG_FILE,
                    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')


class LogWorker(Worker):
    pass
