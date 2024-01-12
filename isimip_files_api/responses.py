from flask import current_app as app

from .utils import get_zip_file_name


def get_response(job, http_status):
    file_name = get_zip_file_name(job.id)

    return {
        'id': job.id,
        'job_url': app.config['BASE_URL'] + '/' + job.id,
        'file_name': file_name,
        'file_url': app.config['OUTPUT_URL'] + '/' + file_name,
        'meta': job.meta,
        'ttl': app.config['WORKER_RESULT_TTL'],
        'status': job.get_status(),
    }, http_status


def get_errors_response(errors):
    return {
        'status': 'error',
        'errors': errors
    }, 400
