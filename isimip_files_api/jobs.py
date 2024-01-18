from flask import current_app as app

from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from redis import Redis

from .responses import get_response
from .tasks import run_task
from .utils import get_hash

redis = Redis()


def count_jobs():
    queue = Queue(connection=redis)

    return {
        'started': queue.started_job_registry.count,
        'deferred': queue.deferred_job_registry.count,
        'finished': queue.finished_job_registry.count,
        'failed': queue.failed_job_registry.count,
        'scheduled': queue.scheduled_job_registry.count
    }

def create_job(paths, args):
    job_id = get_hash(paths, args)
    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)
    except NoSuchJobError:
        job = Job.create(run_task, id=job_id, args=[paths, args],
                         timeout=app.config['WORKER_TIMEOUT'],
                         ttl=app.config['WORKER_TTL'],
                         result_ttl=app.config['WORKER_RESULT_TTL'],
                         failure_ttl=app.config['WORKER_FAILURE_TTL'],
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
