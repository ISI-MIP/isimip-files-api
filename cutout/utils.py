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
        if 'cutout_path' in job.meta:
            response['file_url'] = OUTPUT_URL + '/' + job.meta['cutout_path']

    return response, http_status


def get_errors_response(errors):
    return {
        'status': 'error',
        'errors': errors
    }, 400


def get_cutout_path(path, region):
    cutout_name = Path(path).name.replace(path.suffix, '_' + region + path.suffix)
    cutout_path = path.parent / cutout_name
    return str(cutout_path)


def get_hash(cutout_path):
    m = hashlib.sha1()
    m.update(str(cutout_path).encode())
    return m.hexdigest()
