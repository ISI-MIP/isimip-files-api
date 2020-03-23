from redis import Redis
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

redis = Redis()


def create_job(task, job_id=None, args=[]):
    try:
        job = Job.fetch(job_id, connection=redis)
        return get_response(job, 200)
    except NoSuchJobError:
        job = Queue(connection=redis).enqueue(task, job_id=job_id, args=args)
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


def get_response(job, http_status):
    return {
        'id': job.id,
        'meta': job.meta,
        'status': job.get_status(),
    }, http_status
