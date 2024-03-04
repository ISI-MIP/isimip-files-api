import hashlib
import importlib
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from flask import current_app as app


def get_config_path(config_file):
    if config_file is not None:
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = Path().cwd() / config_path

        if config_path.is_file():
            return config_path


def handle_post_request(request):
    data = {}
    files = {}

    if request.content_type.startswith('multipart/form-data'):
        for file_name, file_storage in request.files.items():
            if file_name == 'data':
                data = json.loads(file_storage.read())
            else:
                files[file_name] = file_storage
    else:
        data = request.json

    return data, files


def get_hash(data, uploads):
    m = hashlib.sha1()
    m.update(str(data).encode())
    for file_name, file_storage in uploads.items():
        m.update(file_storage.read())
    return m.hexdigest()


def get_input_path():
    return Path(app.config['INPUT_PATH']).expanduser().resolve()


def get_tmp_path():
    return Path(app.config['TMP_PATH']).expanduser().resolve()


def get_output_path():
    return Path(app.config['OUTPUT_PATH']).expanduser().resolve()


def get_job_path(job_id):
    job_path = get_tmp_path().joinpath(app.config['OUTPUT_PREFIX'] + job_id)
    job_path.mkdir(parents=True, exist_ok=True)
    return job_path


def get_zip_file_name(job_id):
    return Path(app.config['OUTPUT_PREFIX'] + job_id).with_suffix('.zip').as_posix()


def get_zip_path(job_id):
    zip_path = get_output_path() / get_zip_file_name(job_id)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    return zip_path


def get_zip_file(job_id):
    zip_path = get_zip_path(job_id)
    return ZipFile(zip_path.as_posix(), 'w')


def store_uploads(job_id, uploads):
    job_path = get_job_path(job_id)

    for file_name, file_storage in uploads.items():
        with open(job_path / file_name, 'wb') as fp:
            file_storage.seek(0)
            file_storage.save(fp)


def remove_job_path(job_id):
    job_path = get_job_path(job_id)
    shutil.rmtree(job_path)


def mask_paths(string):
    return re.sub(r'\/\S+\/', '', string)


def import_class(string):
    module_name, class_name = string.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)
