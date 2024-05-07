operation = 'mask_bbox'

def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 23.43651]
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_compute_mean_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 23.43651],
            'compute_mean': True
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_output_csv_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 23.43651],
            'output_csv': True
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_missing_bbox(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['bbox is missing for operation "mask_bbox"']
    }


def test_wrong_bbox(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 'wrong']
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['bbox is not of the form [%f, %f, %f, %f] for operation "mask_bbox"']
    }


def test_wrong_bbox_west_high(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [181, 180, -23.43651, 23.43651]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['west longitude is > 180 in bbox for operation "mask_bbox"']
    }


def test_wrong_bbox_east_low(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, -181, -23.43651, 23.43651]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['east longitude is < -180 in bbox for operation "mask_bbox"']
    }


def test_wrong_bbox_east_high(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 181, -23.43651, 23.43651]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['east longitude is > 180 in bbox for operation "mask_bbox"']
    }


def test_wrong_bbox_south_low(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -91, 23.43651]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['south latitude is < -90 in bbox for operation "mask_bbox"']
    }


def test_wrong_bbox_south_high(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, 91, 23.43651]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['south latitude is > 90 in bbox for operation "mask_bbox"']
    }


def test_wrong_bbox_north_low(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, -91]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['north latitude is < -90 in bbox for operation "mask_bbox"']
    }


def test_wrong_bbox_north_high(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 91]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['north latitude is > 90 in bbox for operation "mask_bbox"']
    }


def test_invalid_compute_mean(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 23.43651],
            'compute_mean': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only true or false are permitted in "compute_mean" for operation "mask_bbox"']
    }


def test_invalid_output_csv(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 23.43651],
            'output_csv': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only true or false are permitted in "output_csv" for operation "mask_bbox"']

    }


def test_invalid_resolution(mocker, client):
    response = client.post('/', json={'paths': ['large.nc'], 'operations': [
        {
            'operation': operation,
            'bbox': [-180, 180, -23.43651, 23.43651]
        }
    ]})

    assert response.status_code == 400
    assert response.json.get('errors') == {
        'resolution': ['resolution of large.nc (360, 180) is to high (180, 90)'
                       ' for operation "mask_bbox"']
    }
