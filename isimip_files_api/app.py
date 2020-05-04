import logging

from flask import Flask, request
from flask_cors import CORS

from .jobs import create_job, delete_job, fetch_job
from .settings import LOG_FILE, LOG_LEVEL
from .tasks import mask_bbox, mask_country, mask_landonly
from .utils import get_errors_response, get_output_path
from .validators import (validate_bbox, validate_country, validate_data,
                         validate_landonly, validate_path)

logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE)


def create_app():
    # create and configure the app
    app = Flask(__name__)

    if CORS:
        CORS(app)

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
                output_path = get_output_path(path, '{}-{}-{}-{}'.format(*bbox))
                return create_job(mask_bbox, output_path, args=[path, output_path, bbox])

        elif 'country' in data:
            country = validate_country(data, errors)
            if not errors:
                output_path = get_output_path(path, country)
                return create_job(mask_country, output_path, args=[path, output_path, country])

        elif 'landonly' in data:
            validate_landonly(data, errors)
            if not errors:
                output_path = get_output_path(path, 'landonly')
                return create_job(mask_landonly, output_path, args=[path, output_path])

        else:
            errors['data'] = 'Either bbox, country, or landonly needs to be provided'

        # if it did not work, return errors
        return get_errors_response(errors)

    @app.route('/<job_id>', methods=['GET'])
    def detail(job_id):
        return fetch_job(job_id)

    @app.route('/<job_id>', methods=['DELETE'])
    def delete(job_id):
        return delete_job(job_id)

    return app
