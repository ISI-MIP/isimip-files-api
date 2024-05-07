operation = 'cutout_point'

def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'point': [13.064332, 52.380551]
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_missing_point(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['point is missing for operation "cutout_point"']
    }


def test_wrong_point(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'point': [13.064332, 'wrong']
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['point is not of the form [%f, %f] for operation "cutout_point"']
    }


def test_wrong_point_lat_low(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'point': [-181, 52.380551]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['longitude is < -180 in point for operation "cutout_point"']
    }


def test_wrong_point_lat_high(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'point': [181, 52.380551]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['longitude is > 180 in point for operation "cutout_point"']
    }


def test_wrong_point_lon_low(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'point': [13.064332, -91]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['latitude is < -90 in point for operation "cutout_point"']
    }


def test_wrong_point_lon_high(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'point': [13.064332, 91]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['latitude is > 90 in point for operation "cutout_point"']
    }


def test_invalid_resolution(mocker, client):
    response = client.post('/', json={'paths': ['large.nc'], 'operations': [
        {
            'operation': operation,
            'point': [13.064332, 52.380551]
        }
    ]})

    assert response.status_code == 400
    assert response.json.get('errors') == {
        'resolution': ['resolution of large.nc (360, 180) is to high (180, 90)'
                       ' for operation "cutout_point"']
    }
