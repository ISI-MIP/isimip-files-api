from flask import current_app as app

from .utils import get_zip_file_name


def get_response(job, http_status):
    file_name = get_zip_file_name(job.id)
    status = job.get_status()

    response = {
        'id': job.id,
        'job_url': app.config['BASE_URL'] + '/' + job.id,
        'meta': job.meta,
        'ttl': app.config['WORKER_RESULT_TTL'],
        'status': status
    }

    if status == 'finished':
        response.update({
            'file_name': file_name,
            'file_url': app.config['OUTPUT_URL'] + '/' + file_name,
        })

    return response, http_status


def get_errors_response(errors):
    return {
        'status': 'error',
        'errors': errors
    }, 400
