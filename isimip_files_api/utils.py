import hashlib
from pathlib import Path

from .settings import BASE_URL, GLOBAL, OUTPUT_PREFIX, OUTPUT_URL


def get_response(job, http_status):
    response = {
        'id': job.id,
        'job_url': BASE_URL + '/' + job.id,
        'meta': job.meta,
        'status': job.get_status(),
    }

    if job.get_status() == 'finished':
        response['file_url'] = '{}/{}'.format(
            OUTPUT_URL,
            Path(OUTPUT_PREFIX + job.id).with_suffix('.zip').as_posix()
        )

    return response, http_status


def get_errors_response(errors):
    return {
        'status': 'error',
        'errors': errors
    }, 400


def get_output_name(path, args):
    if args['bbox']:
        region = 'lat{}to{}lon{}to{}'.format(*args['bbox'])
    elif args['country']:
        region = args['country'].lower()
    elif args['landonly']:
        region = 'landonly'

    path = Path(path)
    if GLOBAL in path.name:
        # replace the _global_ specifier
        return path.name.replace(GLOBAL, '_{}_'.format(region))
    else:
        # append region specifier
        return path.stem + '_{}'.format(region) + path.suffix


def get_hash(paths, args):
    m = hashlib.sha1()
    m.update(str(paths).encode())
    m.update(str(args).encode())
    return m.hexdigest()
