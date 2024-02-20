import base64
from pathlib import Path

shapefile_path = Path('testing/shapes/pm.zip')
wrong_path = Path('testing/shapes/wrong.zip')
geojson_path = Path('testing/shapes/pm.json')

def test_shapefile(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_shape',
            'shapefile': base64.b64encode(shapefile_path.read_bytes()).decode()
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_geojson(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_shape',
            'geojson': geojson_path.read_text()
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_missing_file(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_shape'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['shapefile or geojson is missing for operation "mask_shape"']
    }


def test_invalid_shapefile(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_shape',
            'shapefile': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['shapefile is not a valid base64 stream for operation "mask_shape"']
    }


def test_invalid_shapefile2(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_shape',
            'shapefile': base64.b64encode(b'this is not a valid shapefile').decode()
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['shapefile is a valid zip file for operation "mask_shape"']
    }


def test_invalid_shapefile3(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_shape',
            'shapefile': base64.b64encode(wrong_path.read_bytes()).decode()
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['shapefile is not a valid shape file for operation "mask_shape"']
    }


def test_invalid_geojson(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_shape',
            'geojson': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['geojson is not a valid json for operation "mask_shape"']
    }
