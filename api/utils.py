import hashlib
from pathlib import Path

from .settings import BASE_URL, OUTPUT_URL


def get_response(job, http_status):
    response = {
        'id': job.id,
        'job_url': BASE_URL + '/' + job.id,
        'meta': job.meta,
        'status': job.get_status(),
    }

    if job.get_status() == 'finished':
        if 'output_path' in job.meta:
            response['file_url'] = OUTPUT_URL + '/' + job.meta['output_path']

    return response, http_status


def get_errors_response(errors):
    return {
        'status': 'error',
        'errors': errors
    }, 400


def get_output_path(path, region):
    output_name = Path(path).name.replace(path.suffix, '_' + region + path.suffix)
    output_path = path.parent / output_name
    return str(output_path)


def get_hash(output_path):
    m = hashlib.sha1()
    m.update(str(output_path).encode())
    return m.hexdigest()
