import hashlib
from pathlib import Path

from .settings import (BASE_URL, GLOBAL, OUTPUT_PREFIX, OUTPUT_URL,
                       WORKER_RESULT_TTL)


def get_response(job, http_status):
    return {
        'id': job.id,
        'job_url': BASE_URL + '/' + job.id,
        'file_url': OUTPUT_URL + '/' + get_zip_file_name(job.id),
        'meta': job.meta,
        'ttl': WORKER_RESULT_TTL,
        'status': job.get_status(),
    }, http_status


def get_errors_response(errors):
    return {
        'status': 'error',
        'errors': errors
    }, 400


def get_output_name(path, args):
    if args['task'] in ['cutout_bbox', 'mask_bbox']:
        south, north, west, east = args['bbox']
        region = 'lat{}to{}lon{}to{}'.format(south, north, west, east)
    elif args['task'] == 'mask_country':
        region = args['country'].lower()
    elif args['task'] == 'mask_landonly':
        region = 'landonly'

    path = Path(path)
    if GLOBAL in path.name:
        # replace the _global_ specifier
        return path.name.replace(GLOBAL, '_{}_'.format(region))
    else:
        # append region specifier
        return path.stem + '_{}'.format(region) + path.suffix


def get_zip_file_name(job_id):
    return Path(OUTPUT_PREFIX + job_id).with_suffix('.zip').as_posix()


def get_hash(paths, args):
    m = hashlib.sha1()
    m.update(str(paths).encode())
    m.update(str(args).encode())
    return m.hexdigest()
