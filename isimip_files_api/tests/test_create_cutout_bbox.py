def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'cutout_bbox',
            'bbox': [-23.43651, 23.43651, -180, 180]
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_missing_bbox(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'cutout_bbox'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['bbox is missing for operation "cutout_bbox"']
    }


def test_wrong_bbox(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'cutout_bbox',
            'bbox': [-23.43651, 23.43651, -180, 'wrong']
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['bbox is not of the form [%f, %f, %f, %f] for operation "cutout_bbox"']
    }
