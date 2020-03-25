from redis import Redis
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from .utils import get_hash, get_response

redis = Redis()


def create_job(task, cutout_path, args=[]):
    job_id = get_hash(cutout_path)

    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)
    except NoSuchJobError:
        job = Queue(connection=redis).enqueue(task, job_id=job_id, args=args)
        job.meta['cutout_path'] = str(cutout_path)
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
