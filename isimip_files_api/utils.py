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


def get_output_name(path, args, suffix=None):
    if args['bbox'] is not None:
        south, north, west, east = args['bbox']
        region = 'lat{}to{}lon{}to{}'.format(south, north, west, east)

    elif args['country'] is not None:
        region = args['country'].lower()

    elif args['point'] is not None:
        lat, lon = args['point']
        region = 'lat{}lon{}'.format(lat, lon)

    elif args['landonly'] is True:
        region = 'landonly'

    else:
        raise RuntimeError('Could not determine region string.')

    path = Path(path)
    suffix = suffix if suffix else path.suffix
    if GLOBAL in path.name:
        # replace the _global_ specifier
        return path.with_suffix(suffix).name.replace(GLOBAL, '_{}_'.format(region))
    else:
        # append region specifier
        return path.stem + '_{}'.format(region) + suffix


def get_zip_file_name(job_id):
    return Path(OUTPUT_PREFIX + job_id).with_suffix('.zip').as_posix()


def get_hash(paths, args):
    m = hashlib.sha1()
    m.update(str(paths).encode())
    m.update(str(args).encode())
    return m.hexdigest()
