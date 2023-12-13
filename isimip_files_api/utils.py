import hashlib
import re
from pathlib import Path

from .settings import BASE_URL, GLOBAL, OUTPUT_PREFIX, OUTPUT_URL, WORKER_RESULT_TTL


def get_response(job, http_status):
    file_name = get_zip_file_name(job.id)

    return {
        'id': job.id,
        'job_url': BASE_URL + '/' + job.id,
        'file_name': file_name,
        'file_url': OUTPUT_URL + '/' + file_name,
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
    if args.get('bbox'):
        south, north, west, east = args['bbox']
        region = f'lat{south}to{north}lon{west}to{east}'

    elif args.get('country'):
        region = args['country'].lower()

    elif args.get('point'):
        lat, lon = args['point']
        region = f'lat{lat}lon{lon}'

    else:
        region = 'landonly'

    path = Path(path)
    suffix = suffix if suffix else path.suffix
    if GLOBAL in path.name:
        # replace the _global_ specifier
        return path.with_suffix(suffix).name.replace(GLOBAL, f'_{region}_')
    else:
        # append region specifier
        return path.stem + f'_{region}' + suffix


def get_zip_file_name(job_id):
    return Path(OUTPUT_PREFIX + job_id).with_suffix('.zip').as_posix()


def get_hash(paths, args):
    m = hashlib.sha1()
    m.update(str(paths).encode())
    m.update(str(args).encode())
    return m.hexdigest()


def mask_cmd(cmd):
    return re.sub(r'\/\S+\/', '', cmd)
