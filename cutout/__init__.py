import logging

from flask import Flask, request

from .jobs import create_job, delete_job, fetch_job
from .settings import LOG_FILE, LOG_LEVEL
from .tasks import cutout_bbox, cutout_country
from .utils import get_cutout_path, get_errors_response
from .validators import (validate_bbox, validate_country, validate_data,
                         validate_path)

logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE)


def create_app():
    # create and configure the app
    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def list():
        return {
            'status': 'ok'
        }, 200

    @app.route('/', methods=['POST'])
    def create():
        errors = {}

        data = validate_data(request.json, errors)
        if errors:
            return get_errors_response(errors)

        path = validate_path(data, errors)
        if errors:
            return get_errors_response(errors)

        if 'bbox' in data:
            bbox = validate_bbox(data, errors)
            if not errors:
                cutout_path = get_cutout_path(path, '{}-{}-{}-{}'.format(*bbox))
                return create_job(cutout_bbox, cutout_path, args=[path, cutout_path, bbox])

        elif 'country' in data:
            country = validate_country(data, errors)
            if not errors:
                cutout_path = get_cutout_path(path, country)
                return create_job(cutout_country, cutout_path, args=[path, cutout_path, country])

        else:
            errors['data'] = 'Either bbox or country needs to be provided'

        # if it did not work, return errors
        return get_errors_response(errors)

    @app.route('/<job_id>', methods=['GET'])
    def detail(job_id):
        return fetch_job(job_id)

    @app.route('/<job_id>', methods=['DELETE'])
    def delete(job_id):
        return delete_job(job_id)

    return app
