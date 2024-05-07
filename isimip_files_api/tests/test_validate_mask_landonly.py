operation = 'mask_landonly'

def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': operation
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None


def test_invalid_resolution(mocker, client):
    response = client.post('/', json={'paths': ['large.nc'], 'operations': [
        {
            'operation': operation
        }
    ]})

    assert response.status_code == 400
    assert response.json.get('errors') == {
        'resolution': ['resolution of large.nc (360, 180) does not match mask resolution (180, 90)'
                       ' for operation "mask_landonly"']
    }
