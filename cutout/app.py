import logging

from flask import Flask, request

from .jobs import create_job, delete_job, fetch_job
from .settings import LOG_FILE, LOG_LEVEL
from .tasks import cutout_bbox, cutout_country
from .utils import get_cutout_path
from .validators import (validate_bbox, validate_country, validate_data,
                         validate_path)

logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def list():
    return {
        'status': 'ok'
    }, 200


@app.route('/', methods=['POST'])
def create():
    data = request.json
    errors = {}

    validate_data(data, errors)
    path = validate_path(data, errors)

    if not errors:
        if 'bbox' in data:
            bbox = validate_bbox(data, errors)
            if not errors:
                cutout_path = get_cutout_path(path, '{}-{}-{}-{}'.format(*bbox))
                return create_job(cutout_bbox, str(cutout_path), args=[path, cutout_path, bbox])

        elif 'country' in data:
            country = validate_country(data, errors)
            if not errors:
                cutout_path = get_cutout_path(path, country)
                return create_job(cutout_country, str(cutout_path), args=[path, cutout_path, country])

    # if it did not work, return errors
    return {
        'status': 'error',
        'errors': errors
    }, 400


@app.route('/<job_id>', methods=['GET'])
def detail(job_id):
    return fetch_job(job_id)


@app.route('/<job_id>', methods=['DELETE'])
def delete(job_id):
    return delete_job(job_id)
