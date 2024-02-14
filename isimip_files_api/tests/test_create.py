def test_empty(client):
    response = client.post('/', json={})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {'data': ['No json data provided with POST']}


def test_list(client):
    response = client.post('/', json=[1, 2, 3])
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {'data': ['Provided json data is malformatted']}


def test_missing(client):
    response = client.post('/', json={'foo': 'bar'})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'paths': ['This field is required.'],
        'operations': ['This field is required.']
    }


def test_malformatted(client):
    response = client.post('/', json={'paths': {'foo': 'bar'}, 'operations': {'foo': 'bar'}})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'paths': ['Provided json data is malformatted.'],
        'operations': ['Provided json data is malformatted.']
    }


def test_paths_to_many_files(client):
    response = client.post('/', json={'paths': [
        'test1.nc',
        'test2.nc',
        'test3.nc',
        'test4.nc',
        'test5.nc',
        'test6.nc',
        'test7.nc',
        'test8.nc',
        'test9.nc'
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'paths': ['To many files match that dataset (max: 8).'],
        'operations': ['This field is required.']
    }


def test_paths_below_root(client):
    response = client.post('/', json={'paths': [
        '../test.nc'
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'paths': ['../test.nc is below the root path.'],
        'operations': ['This field is required.']
    }


def test_paths_not_netcdf(client):
    response = client.post('/', json={'paths': [
        'test.txt'
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'paths': ['test.txt is not a NetCDF file.'],
        'operations': ['This field is required.']
    }


def test_paths_not_found(client):
    response = client.post('/', json={
        'paths': [
        'test.nc'
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'paths': ['test.nc was not found on the server.'],
        'operations': ['This field is required.']
    }


def test_operations_not_found(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'invalid'
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['operation "invalid" was not found']
    }


def test_operations_to_many_commands(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'cutout_bbox',
            'bbox': [-10, 10, -10, 10]
        },
        {
            'operation': 'mask_landonly'
        },
        {
            'operation': 'cutout_bbox',
            'bbox': [-23.43651, 23.43651, -180, 180]
        }
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['Operations result in to many commands (max: 2).']
    }


def test_operations_to_many_operations(client):
    response = client.post('/', json={'paths': ['constant.nc'], 'operations': [
        {
            'operation': 'mask_landonly'
        } for i in range(10)
    ]})
    assert response.status_code == 400
    assert response.json.get('status') == 'error'
    assert response.json.get('errors') == {
        'operations': ['To many operations provided (max: 8).']
    }
