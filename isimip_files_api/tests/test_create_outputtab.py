def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.create_job', mocker.Mock(return_value=({}, 201)))

    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'outputtab'
        }
    ]})

    assert response.status_code == 201
    assert response.json.get('errors') is None
