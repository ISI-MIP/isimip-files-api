import hashlib
import importlib
import re
from pathlib import Path

from flask import current_app as app


def get_zip_file_name(job_id):
    return Path(app.config['OUTPUT_PREFIX'] + job_id).with_suffix('.zip').as_posix()


def get_hash(data):
    m = hashlib.sha1()
    m.update(str(data).encode())
    return m.hexdigest()


def mask_paths(string):
    return re.sub(r'\/\S+\/', '', string)


def import_class(string):
    module_name, class_name = string.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)
