import pytest

from ..app import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'INPUT_PATH': 'testing/input',
        'OUTPUT_PATH': 'testing/output',
        'MAX_FILES': 8
    })

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()
