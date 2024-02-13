from flask import Flask, request

import tomli
from flask_cors import CORS as FlaskCORS

from .jobs import count_jobs, create_job, delete_job, fetch_job
from .logging import configure_logging
from .responses import get_errors_response
from .validators import validate_data, validate_operations, validate_paths


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object('isimip_files_api.config')
    app.config.from_prefixed_env()
    if 'CONFIG' in app.config:
        app.config.from_file(app.config['CONFIG'], load=tomli.load, text=False)

    # configure logging
    configure_logging(app)

    # enable CORS
    if app.config['CORS']:
        FlaskCORS(app)

    @app.route('/', methods=['GET'])
    def index():
        return {
            'status': 'ok',
            'jobs': count_jobs()
        }, 200

    @app.route('/', methods=['POST'])
    def create():
        app.logger.debug('request.json = %s', request.json)

        data = request.json

        errors = validate_data(data)
        if errors:
            app.logger.debug('errors = %s', errors)
            return get_errors_response(errors)

        errors = dict(**validate_paths(data),
                      **validate_operations(data))
        if errors:
            app.logger.debug('errors = %s', errors)
            return get_errors_response(errors)

        return create_job(data)

    @app.route('/<job_id>', methods=['GET'])
    def detail(job_id):
        return fetch_job(job_id)

    @app.route('/<job_id>', methods=['DELETE'])
    def delete(job_id):
        return delete_job(job_id)

    return app
