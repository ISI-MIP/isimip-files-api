import hashlib
from pathlib import Path

from .settings import BASE_URL, GLOBAL, INPUT_PATH, OUTPUT_URL


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


def get_output_name(path, args):
    if args['bbox']:
        region = '_lat{}to{}lon{}to{}_'.format(*args['bbox'])
    elif args['country']:
        region = '_{}_'.format(args['country'].lower())
    elif args['landonly']:
        region = '_landonly_'

    return Path(path).name.replace(GLOBAL, region)


def get_output_path(path, args):
    output_name = get_output_name(path, args)
    output_path = Path(path).parent / output_name
    if not output_path.suffix:
        output_path = output_path.with_suffix('.zip')

    return str(output_path)


def get_hash(output_path):
    m = hashlib.sha1()
    m.update(str(output_path).encode())
    return m.hexdigest()


def find_files(path):
    files = []
    for file_name in INPUT_PATH.joinpath(path).parent.iterdir():
        # filter files which starts with the name part of path and end with .nc or .nc4
        if file_name.name.startswith(Path(path).name) and file_name.suffix in ['.nc', '.nc4']:
            files.append(file_name)
    return files
