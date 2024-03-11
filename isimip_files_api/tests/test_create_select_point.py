def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'select_point',
            'point': [52.380551, 13.064332]
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_output_csv_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'select_point',
            'point': [52.380551, 13.064332],
            'output_csv': True
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_missing_bbox(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'select_point'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['point is missing for operation "select_point"']
    }


def test_wrong_point(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'select_point',
            'point': [52.380551, 'wrong']
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['point is not of the form [%f, %f] for operation "select_point"']
    }


def test_invalid_output_csv(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'select_point',
            'point': [52.380551, 13.064332],
            'output_csv': 'wrong'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['only true or false are permitted in "output_csv" for operation "select_point"']
    }
