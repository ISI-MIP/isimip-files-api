import hashlib
import importlib
import re
from pathlib import Path

from flask import current_app as app


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
    if app.config['GLOBAL_TAG'] in path.name:
        # replace the _global_ specifier
        return path.with_suffix(suffix).name.replace(app.config['GLOBAL_TAG'], f'_{region}_')
    else:
        # append region specifier
        return path.stem + f'_{region}' + suffix


def get_zip_file_name(job_id):
    return Path(app.config['OUTPUT_PREFIX'] + job_id).with_suffix('.zip').as_posix()


def get_hash(paths, args):
    m = hashlib.sha1()
    m.update(str(paths).encode())
    m.update(str(args).encode())
    return m.hexdigest()


def mask_cmd(cmd):
    return re.sub(r'\/\S+\/', '', cmd)


def import_class(string):
    module_name, class_name = string.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)
