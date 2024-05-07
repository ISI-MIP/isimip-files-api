import io
import json
from pathlib import Path

shapefile_path = Path('testing') / 'shapes' / 'pm.zip'
wrong_path = Path('testing') / 'shapes' / 'wrong.zip'
geojson_path = Path('testing') / 'shapes' / 'pm.json'


def test_shape(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    data = {
        'paths': ['constant.nc'],
        'operations': [
            {
                'operation': 'create_mask',
                'shape': 'pm.zip',
                'mask': 'pm.nc'
            }
        ]
    }

    response = client.post('/', data={
        'data': (io.BytesIO(json.dumps(data).encode()), 'data', 'application/json'),
        'pm.zip': (shapefile_path.open('rb'), 'pm.zip', 'application/zip')
    })

    assert response.status_code == 201, response.text
    assert response.json.get('errors') is None


def test_missing_shape(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'create_mask',
            'mask': 'pm.nc'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['shape is missing for operation "create_mask"']
    }


def test_missing_mask(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'create_mask',
            'shape': 'pm.zip'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['mask is missing for operation "create_mask"']
    }


def test_invalid_mask1(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'create_mask',
            'shape': 'pm.zip',
            'mask': 'pm.nc ; wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only letters, numbers, hyphens, underscores, and periods are permitted in "mask"'
                       ' for operation "create_mask"']
    }


def test_invalid_mask2(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'create_mask',
            'shape': 'pm.zip',
            'mask': '..pm.nc'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['consecutive periods are not permitted in "mask" for operation "create_mask"']
    }


def test_missing_file(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    data = {
        'paths': ['constant.nc'],
        'operations': [
            {
                'operation': 'create_mask',
                'shape': 'pm.zip',
                'mask': 'pm.nc'
            }
        ]
    }

    response = client.post('/', data={
        'data': (io.BytesIO(json.dumps(data).encode()), 'data', 'application/json')
    })

    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'uploads': ['File "pm.zip" for operation "create_mask" is not part of the uploads']
    }
