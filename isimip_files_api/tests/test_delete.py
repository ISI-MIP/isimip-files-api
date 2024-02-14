def mocked_delete_job(job_id):
    if job_id == 'test':
        return {}, 204
    else:
        return {}, 404


def test_success(client, mocker):
    mocker.patch('isimip_files_api.app.fetch_job', mocked_delete_job)

    response = client.get('/test')

    assert response.status_code == 204


def test_wrong_id(client, mocker):
    mocker.patch('isimip_files_api.app.fetch_job', mocked_delete_job)

    response = client.get('/wrong')

    assert response.status_code == 404
