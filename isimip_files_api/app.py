from flask import Flask, request

import tomli
from flask_cors import CORS as FlaskCORS

from .jobs import count_jobs, create_job, delete_job, fetch_job
from .logging import configure_logging
from .operations import OperationRegistry
from .responses import get_errors_response
from .utils import get_config_path, handle_post_request
from .validators import validate_data, validate_operations, validate_paths, validate_uploads


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object('isimip_files_api.config')
    app.config.from_prefixed_env()

    config_path = get_config_path(app.config.get('CONFIG'))
    if config_path:
        app.config.from_file(get_config_path(config_path), load=tomli.load, text=False)

    # configure logging
    configure_logging(app)

    # enable CORS
    if app.config['CORS']:
        FlaskCORS(app)

    @app.route('/', methods=['GET'])
    def index():
        return {
            'status': 'ok',
            'jobs': count_jobs(),
            'operations': list(OperationRegistry().operations.keys()),
            'base_url': app.config.get('BASE_URL'),
            'output_url': app.config.get('OUTPUT_URL')
        }, 200

    @app.route('/', methods=['POST'])
    def create():
        data, uploads = handle_post_request(request)
        app.logger.debug('data = %s', data)
        app.logger.debug('files = %s', uploads.keys())

        # validation step 1: check data
        errors = validate_data(data)
        if errors:
            app.logger.debug('errors = %s', errors)
            return get_errors_response(errors)

        # validation step 2: check paths and operations
        errors = dict(**validate_paths(data),
                      **validate_operations(data))
        if errors:
            app.logger.debug('errors = %s', errors)
            return get_errors_response(errors)

        # validation step 3: check uploads
        errors = validate_uploads(data, uploads)
        if errors:
            app.logger.debug('errors = %s', errors)
            return get_errors_response(errors)

        return create_job(data, uploads)

    @app.route('/<job_id>', methods=['GET'])
    def detail(job_id):
        return fetch_job(job_id)

    @app.route('/<job_id>', methods=['DELETE'])
    def delete(job_id):
        return delete_job(job_id)

    return app
