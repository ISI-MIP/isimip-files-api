import logging
from collections import defaultdict

from flask import Flask, request
from flask_cors import CORS as FlaskCORS

from .jobs import create_job, delete_job, fetch_job
from .settings import CORS, LOG_FILE, LOG_LEVEL
from .utils import get_errors_response
from .validators import validate_data

logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE)


def create_app():
    # create and configure the app
    app = Flask(__name__)

    if CORS:
        FlaskCORS(app)

    @app.route('/', methods=['GET'])
    def index():
        return {
            'status': 'ok'
        }, 200

    @app.route('/', methods=['POST'])
    def create():
        errors = defaultdict(list)

        cleaned_data = validate_data(request.json, errors)
        if errors:
            return get_errors_response(errors)

        return create_job(*cleaned_data)

    @app.route('/<job_id>', methods=['GET'])
    def detail(job_id):
        return fetch_job(job_id)

    @app.route('/<job_id>', methods=['DELETE'])
    def delete(job_id):
        return delete_job(job_id)

    return app
