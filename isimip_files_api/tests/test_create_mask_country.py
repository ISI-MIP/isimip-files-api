def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_country',
            'country': 'deu'
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_compute_mean_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_country',
            'country': 'deu',
            'compute_mean': True
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_output_csv_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_country',
            'country': 'deu',
            'output_csv': True
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_missing_country(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_country'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['country is missing for operation "mask_country"']
    }


def test_wrong_country(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_country',
            'country': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['country not in the list of supported countries (e.g. deu) for operation "mask_country"']
    }


def test_invalid_compute_mean(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_country',
            'country': 'deu',
            'compute_mean': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only true or false are permitted in "compute_mean" for operation "mask_country"']
    }


def test_invalid_output_csv(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_country',
            'country': 'deu',
            'output_csv': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only true or false are permitted in "output_csv" for operation "mask_country"']
    }
