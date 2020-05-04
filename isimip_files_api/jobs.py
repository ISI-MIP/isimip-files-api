from redis import Redis
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from .settings import WORKER_TIMEOUT
from .tasks import run_task
from .utils import get_hash, get_response

redis = Redis()


def create_job(path, output_path, args):
    # get job_id from output path
    job_id = get_hash(output_path)
    job_args = [path, output_path, args]

    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)
    except NoSuchJobError:
        job = Job.create(run_task, id=job_id, timeout=WORKER_TIMEOUT, args=job_args, connection=redis)
        queue = Queue(connection=redis)
        queue.enqueue_job(job)
        job.meta['output_path'] = str(output_path)
        job.save_meta()
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
