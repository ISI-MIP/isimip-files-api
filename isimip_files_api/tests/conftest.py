import pytest

from redis import Redis

from ..app import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'INPUT_PATH': 'testing/input',
        'OUTPUT_PATH': 'testing/output',
        'LANDSEAMASK_FILE_PATH': 'testing/masks/mask.nc',
        'COUNTRYMASKS_FILE_PATH': 'testing/masks/mask.nc',
        'CDO_MAX_RESOLUTION': (180, 90),
        'NCKS_MAX_RESOLUTION': (180, 90),
        'MAX_FILES': 4
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def redis(app):
    return Redis.from_url(app.config['REDIS_URL'])
