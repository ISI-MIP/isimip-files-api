from flask import current_app as app

from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from redis import Redis

from .responses import get_response
from .tasks import run_task
from .utils import get_hash, store_uploads


def count_jobs():
    redis = Redis.from_url(app.config['REDIS_URL'])
    queue = Queue(connection=redis)

    return {
        'started': queue.started_job_registry.count,
        'deferred': queue.deferred_job_registry.count,
        'finished': queue.finished_job_registry.count,
        'failed': queue.failed_job_registry.count,
        'scheduled': queue.scheduled_job_registry.count
    }

def create_job(data, uploads):
    redis = Redis.from_url(app.config['REDIS_URL'])

    job_id = get_hash(data, uploads)

    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)
    except NoSuchJobError:
        # create tmp dir and store uploaded files
        store_uploads(job_id, uploads)

        # create and enqueue asyncronous job
        job = Job.create(run_task, id=job_id, args=[data['paths'], data['operations']],
                         timeout=app.config['WORKER_TIMEOUT'],
                         ttl=app.config['WORKER_TTL'],
                         result_ttl=app.config['WORKER_RESULT_TTL'],
                         failure_ttl=app.config['WORKER_FAILURE_TTL'],
                         connection=redis)
        queue = Queue(connection=redis)
        queue.enqueue_job(job)
        return get_response(job, 201)


def fetch_job(job_id):
    redis = Redis.from_url(app.config['REDIS_URL'])

    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)

    except NoSuchJobError:
        return {
            'status': 'not found'
        }, 404


def delete_job(job_id):
    redis = Redis.from_url(app.config['REDIS_URL'])

    try:
        job = Job.fetch(job_id, connection=redis)
        job.delete()
        return '', 204

    except NoSuchJobError:
        return {
            'status': 'not found'
        }, 404
