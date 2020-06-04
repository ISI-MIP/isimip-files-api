import logging

from flask import Flask, request
from flask_cors import CORS as FlaskCORS

from .jobs import create_job, delete_job, fetch_job
from .settings import CORS, LOG_FILE, LOG_LEVEL
from .utils import get_errors_response, get_output_path
from .validators import validate_args, validate_data, validate_path

logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE)


def create_app():
    # create and configure the app
    app = Flask(__name__)

    if CORS:
        FlaskCORS(app)

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

        args = validate_args(data, errors)
        if errors:
            return get_errors_response(errors)

        output_path = get_output_path(path, args)
        return create_job(path, output_path, args)

    @app.route('/<job_id>', methods=['GET'])
    def detail(job_id):
        return fetch_job(job_id)

    @app.route('/<job_id>', methods=['DELETE'])
    def delete(job_id):
        return delete_job(job_id)

    return app
