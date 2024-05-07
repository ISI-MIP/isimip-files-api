def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'mask': 'pm.nc'
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_compute_mean_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'mask': 'pm.nc',
            'compute_mean': True
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_output_csv_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'mask': 'pm.nc',
            'output_csv': True
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_missing_mask(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['mask is missing for operation "mask_mask"']
    }


def test_invalid_mask1(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'shape': 'pm.zip',
            'mask': 'pm.nc ; wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only letters, numbers, hyphens, underscores, and periods are'
                       ' permitted in "mask" for operation "mask_mask"']
    }


def test_invalid_mask2(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'shape': 'pm.zip',
            'mask': '..pm.nc'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['consecutive periods are not permitted in "mask" for operation "mask_mask"']
    }


def test_invalid_var(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'shape': 'pm.zip',
            'mask': 'pm.nc',
            'var': 'm_0 ; wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only letters, numbers, underscores are permitted in "var"'
                       ' for operation "mask_mask"']
    }


def test_invalid_compute_mean(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'mask': 'pm.nc',
            'compute_mean': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only true or false are permitted in "compute_mean" for operation "mask_mask"']
    }


def test_invalid_output_csv(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'mask': 'pm.nc',
            'output_csv': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only true or false are permitted in "output_csv" for operation "mask_mask"']
    }


def test_invalid_resolution(mocker, client):
    response = client.post('/', json={'paths': ['large.nc'], 'operations': [
        {
            'operation': 'mask_mask',
            'mask': 'pm.nc'
        }
    ]})

    assert response.status_code == 400
    assert response.json.get('errors') == {
        'resolution': ['resolution of large.nc (360, 180) is to high (180, 90)'
                       ' for operation "mask_mask"']
    }
