from redis import Redis

from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from .settings import (WORKER_FAILURE_TTL, WORKER_RESULT_TTL, WORKER_TIMEOUT,
                       WORKER_TTL)
from .tasks import run_task
from .utils import get_hash, get_response

redis = Redis()


def create_job(paths, args):
    job_id = get_hash(paths, args)
    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)
    except NoSuchJobError:
        job = Job.create(run_task, id=job_id, args=[paths, args],
                         timeout=WORKER_TIMEOUT, ttl=WORKER_TTL,
                         result_ttl=WORKER_RESULT_TTL, failure_ttl=WORKER_FAILURE_TTL,
                         connection=redis)
        queue = Queue(connection=redis)
        queue.enqueue_job(job)
        return get_response(job, 201)


def fetch_job(job_id):
    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)

    except NoSuchJobError:
        return {
            'status': 'not found'
        }, 404


def delete_job(job_id):
    try:
        job = Job.fetch(job_id, connection=redis)
        job.delete()
        return '', 204

    except NoSuchJobError:
        return {
            'status': 'not found'
        }, 404
